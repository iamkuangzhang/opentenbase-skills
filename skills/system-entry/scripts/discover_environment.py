#!/usr/bin/env python3
"""只读 OpenTenBase 环境识别脚本。

本脚本只执行有边界的只读检查。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TIMEOUT = 5
CONFIG_NAMES = {"opentenbase_config.ini", "config.ini", "pgxc_ctl.conf"}
SENSITIVE_RE = re.compile(r"(password|passwd|secret|token|private_key)\s*=\s*[^,\s]+", re.IGNORECASE)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(argv: list[str], *, timeout: int = TIMEOUT, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, env=env)
        return {
            "argv": argv,
            "returncode": proc.returncode,
            "stdout": redact(proc.stdout.strip()),
            "stderr": redact(proc.stderr.strip()),
            "timeout": False,
        }
    except FileNotFoundError as exc:
        return {"argv": argv, "returncode": 127, "stdout": "", "stderr": str(exc), "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": 124,
            "stdout": redact((exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""),
            "stderr": "command timed out",
            "timeout": True,
        }
    except Exception as exc:  # keep discovery alive
        return {"argv": argv, "returncode": 1, "stdout": "", "stderr": str(exc), "timeout": False}


def redact(text: str) -> str:
    return SENSITIVE_RE.sub(lambda m: m.group(1) + "=<redacted>", text)


def split_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def command_path(name: str) -> str:
    return shutil.which(name) or "unknown"


def type_all(name: str) -> dict[str, Any]:
    return run(["bash", "-lc", f"type -a {name}"], timeout=TIMEOUT) if command_path("bash") != "unknown" else {"argv": ["type", name], "returncode": 127, "stdout": "", "stderr": "bash not found", "timeout": False}


def bounded_find(root: Path, max_depth: int = 5) -> list[str]:
    results: list[str] = []
    try:
        root = root.expanduser().resolve()
    except Exception:
        return results
    if not root.exists() or not root.is_dir():
        return results
    root_parts = len(root.parts)
    for current, dirs, files in os.walk(root):
        cur = Path(current)
        depth = len(cur.parts) - root_parts
        if depth >= max_depth:
            dirs[:] = []
        for name in files:
            if name in CONFIG_NAMES:
                path = cur / name
                if is_relevant_config(path):
                    results.append(str(path))
    return sorted(set(results))


def is_relevant_config(path: Path) -> bool:
    name = path.name
    if name in {"opentenbase_config.ini", "pgxc_ctl.conf"}:
        return True
    lowered = str(path).lower()
    return "opentenbase" in lowered or "pgxc" in lowered


def parse_pgxc_ports(config_paths: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in config_paths:
        if not path.endswith("pgxc_ctl.conf"):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        names = extract_assignment(text, "coordNames")
        ports = extract_assignment(text, "coordPorts") or extract_assignment(text, "coordForwardPorts")
        hosts = extract_assignment(text, "coordMasterServers")
        for idx, port in enumerate(ports):
            port = clean_token(port)
            if not port.isdigit():
                continue
            host = clean_token(hosts[idx]) if idx < len(hosts) else "127.0.0.1"
            if not is_sane_host(host):
                continue
            candidates.append({
                "source": path,
                "role": "coordinator",
                "name": names[idx] if idx < len(names) else f"coord{idx + 1}",
                "host": host,
                "port": port,
            })
    return candidates


def extract_assignment(text: str, key: str) -> list[str]:
    match = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+)$", text, re.MULTILINE)
    if not match:
        return []
    raw = match.group(1).strip().strip("'\"")
    raw = raw.replace(",", " ").replace("(", " ").replace(")", " ")
    return [clean_token(item) for item in raw.split() if clean_token(item)]


def clean_token(value: str) -> str:
    return value.strip().strip("'\"(),")


def is_sane_host(value: str) -> bool:
    if not value or "TABSE_TEST" in value or "$" in value:
        return False
    return bool(re.match(r"^[A-Za-z0-9_.:-]+$", value))


def process_info() -> list[dict[str, Any]]:
    result = run(["ps", "-ef"], timeout=TIMEOUT)
    rows = []
    for line in split_lines(result["stdout"]):
        lower = line.lower()
        if any(token in lower for token in ("postgres", "gtm", "pgxc", "opentenbase")):
            rows.append({"line": line})
    return rows


def port_info() -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    argv = ["ss", "-lntp"] if command_path("ss") != "unknown" else ["netstat", "-lntp"]
    result = run(argv, timeout=TIMEOUT)
    rows = []
    if result["returncode"] != 0:
        warnings.append(f"端口命令执行失败：{result['stderr'] or result['returncode']}")
    for line in split_lines(result["stdout"]):
        lower = line.lower()
        if any(token in lower for token in ("postgres", "gtm", "opentenbase")):
            rows.append({"line": line})
    if not rows and result["stdout"]:
        warnings.append("端口命令有输出，但权限可能隐藏了进程名")
    return rows, warnings


def coordinator_candidates_from_ports(ports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in ports:
        line = row.get("line", "")
        if "postgres" not in line.lower():
            continue
        for match in re.finditer(r":(\d{4,5})\b", line):
            port = match.group(1)
            if not port.startswith("3") or port in seen:
                continue
            seen.add(port)
            candidates.append({
                "source": "listening_port",
                "role": "coordinator",
                "name": f"listener_{port}",
                "host": "127.0.0.1",
                "port": port,
            })
    return candidates


def version_of(path: str, arg: str = "--version") -> str:
    if path == "unknown":
        return "unknown"
    result = run([path, arg], timeout=TIMEOUT)
    return result["stdout"].splitlines()[0] if result["returncode"] == 0 and result["stdout"] else "unknown"


def discover_database(psql: str, candidates: list[dict[str, Any]], no_database: bool) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    database = {"reachable_cn": [], "version": "unknown"}
    topology = {"gtm": [], "coordinators": [], "datanodes": []}
    warnings: list[str] = []
    if no_database:
        warnings.append("已通过 --no-database 跳过数据库检查")
        return database, topology, warnings
    if psql == "unknown":
        warnings.append("未找到 psql，跳过数据库检查")
        return database, topology, warnings

    tried = set()
    for cand in candidates[:8]:
        host = normalize_host(str(cand.get("host") or "127.0.0.1"))
        port = str(cand.get("port") or "")
        if not port or (host, port) in tried:
            continue
        tried.add((host, port))
        env = dict(os.environ)
        env["PGCONNECT_TIMEOUT"] = "5"
        user = env.get("USER") or env.get("LOGNAME") or "opentenbase"
        base = [psql, "-h", host, "-p", port, "-d", "postgres", "-U", user, "-Atc"]
        one = run(base + ["SELECT 1;"], timeout=TIMEOUT + 2, env=env)
        if one["returncode"] != 0:
            warnings.append(f"CN 候选 {host}:{port} 不可连接：{one['stderr'] or one['stdout']}")
            continue
        ver = run(base + ["SELECT version();"], timeout=TIMEOUT + 2, env=env)
        node = run(base + ["SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;"], timeout=TIMEOUT + 2, env=env)
        database["reachable_cn"].append({"host": host, "port": port, "source": cand.get("source", "candidate")})
        if ver["returncode"] == 0 and ver["stdout"]:
            database["version"] = ver["stdout"].splitlines()[0]
        if node["returncode"] == 0:
            for line in split_lines(node["stdout"]):
                parts = line.split("|")
                if len(parts) < 4:
                    continue
                item = {"name": parts[0], "type": parts[1], "host": parts[2], "port": parts[3], "source": "pgxc_node"}
                if parts[1].upper().startswith("C"):
                    topology["coordinators"].append(item)
                elif parts[1].upper().startswith("D"):
                    topology["datanodes"].append(item)
                elif "G" in parts[1].upper():
                    topology["gtm"].append(item)
        else:
            warnings.append(f"在 {host}:{port} 查询 pgxc_node 失败：{node['stderr'] or node['stdout']}")
        break
    if not database["reachable_cn"] and not candidates:
        warnings.append("未从有边界证据中发现 CN 候选")
    return database, topology, warnings


def normalize_host(host: str) -> str:
    if host in {"localhost", "0.0.0.0", "*", ""}:
        return "127.0.0.1"
    return host


def management_selection(candidates: list[dict[str, Any]], config_paths: list[str], processes: list[dict[str, Any]]) -> dict[str, Any]:
    names = {c["name"] for c in candidates}
    evidence = []
    for c in candidates:
        evidence.append(f"{c['name']} 二进制：{c['path']}")
    for path in config_paths:
        if path.endswith("pgxc_ctl.conf"):
            evidence.append(f"pgxc_ctl 配置：{path}")
        elif path.endswith(".ini") or path.endswith("config.ini"):
            evidence.append(f"opentenbase_ctl 风格配置候选：{path}")
    if processes:
        evidence.append(f"OpenTenBase 相关进程行数：{len(processes)}")

    has_otb = "opentenbase_ctl" in names
    has_pgxc = "pgxc_ctl" in names
    has_pgxc_conf = any(p.endswith("pgxc_ctl.conf") for p in config_paths)
    has_otb_conf = any(p.endswith("opentenbase_config.ini") or p.endswith("config.ini") for p in config_paths)

    selected = "unknown"
    confidence = "unknown"
    if has_otb and has_otb_conf and not (has_pgxc and has_pgxc_conf):
        selected = "opentenbase_ctl"
        confidence = "medium"
    elif has_pgxc and has_pgxc_conf and not (has_otb and has_otb_conf):
        selected = "pgxc_ctl"
        confidence = "medium"
    elif (has_otb or has_otb_conf) and (has_pgxc or has_pgxc_conf):
        selected = "ambiguous"
        confidence = "low"
    elif has_otb or has_pgxc:
        selected = "unknown"
        confidence = "low"

    return {
        "selected": selected,
        "confidence": confidence,
        "candidates": candidates,
        "evidence": evidence,
    }


def consistency_status(config_cn: list[dict[str, Any]], topology: dict[str, Any], processes: list[dict[str, Any]], ports: list[dict[str, Any]], warnings: list[str]) -> dict[str, Any]:
    local_warnings = list(warnings)
    sources = 0
    if config_cn:
        sources += 1
    if topology["coordinators"] or topology["datanodes"]:
        sources += 1
    if processes:
        sources += 1
    if ports:
        sources += 1
    if sources >= 3 and not local_warnings:
        status = "consistent"
    elif sources >= 2:
        status = "partial"
    elif sources == 1:
        status = "unknown"
        local_warnings.append("只发现一类拓扑证据")
    else:
        status = "unknown"
        local_warnings.append("未发现拓扑证据")
    if config_cn and topology["coordinators"] and len(config_cn) != len(topology["coordinators"]):
        status = "ambiguous"
        local_warnings.append("配置候选中的 CN 数量与 pgxc_node 查询结果不同")
    return {"status": status, "warnings": local_warnings}


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    command_evidence: list[dict[str, Any]] = []

    def record(argv: list[str], *, timeout: int = TIMEOUT) -> dict[str, Any]:
        result = run(argv, timeout=timeout)
        command_evidence.append(result)
        return result

    host_addresses = split_lines(record(["hostname", "-I"])["stdout"])
    tool_names = ["opentenbase_ctl", "pgxc_ctl", "psql", "postgres", "pg_config"]
    tool_entries = []
    for name in tool_names:
        path = command_path(name)
        if path != "unknown":
            tool_entries.append({"name": name, "path": path, "type_a": type_all(name)["stdout"]})

    roots = [Path.home(), Path.cwd(), Path(args.config_search_root)]
    if args.extra_config_search_root:
        roots.extend(Path(p) for p in args.extra_config_search_root)
    config_paths: list[str] = []
    for root in roots:
        config_paths.extend(bounded_find(root, max_depth=args.max_depth))
    config_paths = sorted(set(config_paths))

    processes = process_info()
    ports, port_warnings = port_info()
    warnings.extend(port_warnings)

    psql = command_path("psql")
    pg_config = command_path("pg_config")
    postgres = command_path("postgres")
    config_cn = parse_pgxc_ports(config_paths)
    observed_cn = coordinator_candidates_from_ports(ports)
    cn_candidates = config_cn + [item for item in observed_cn if (item["host"], item["port"]) not in {(c["host"], c["port"]) for c in config_cn}]
    database, topology, db_warnings = discover_database(psql, cn_candidates, args.no_database)
    warnings.extend(db_warnings)

    version = database["version"]
    if version == "unknown":
        version = version_of(psql)
    binary_root = "unknown"
    if pg_config != "unknown":
        bindir = run([pg_config, "--bindir"])
        if bindir["returncode"] == 0 and bindir["stdout"]:
            binary_root = bindir["stdout"].strip()

    summary = {
        "timestamp": now(),
        "host": {
            "user": record(["whoami"])["stdout"] or "unknown",
            "id": record(["id"])["stdout"] or "unknown",
            "hostname": record(["hostname"])["stdout"] or socket.gethostname(),
            "addresses": host_addresses,
            "pwd": str(Path.cwd()),
            "uname": record(["uname", "-a"])["stdout"] or "unknown",
        },
        "opentenbase": {
            "detected": bool(tool_entries or processes or config_paths or database["reachable_cn"]),
            "version": version or "unknown",
            "binary_root": binary_root,
            "psql": psql,
            "postgres": postgres,
            "pg_config": pg_config,
            "pg_config_version": version_of(pg_config),
            "postgres_version": version_of(postgres),
        },
        "management": management_selection(tool_entries, config_paths, processes),
        "config_files": [{"path": path} for path in config_paths],
        "processes": processes,
        "ports": ports,
        "database": database,
        "topology": topology,
        "consistency": consistency_status(cn_candidates, topology, processes, ports, warnings),
        "safety": {
            "write_operations_allowed": False,
            "reason": "system-entry 按设计只读",
        },
        "command_evidence": command_evidence,
        "errors": errors,
    }
    return summary


def render_human(data: dict[str, Any]) -> str:
    lines = [
        "OpenTenBase system-entry 环境摘要",
        f"时间：{data['timestamp']}",
        f"用户：{data['host'].get('user', 'unknown')}",
        f"主机：{data['host'].get('hostname', 'unknown')}",
        f"地址：{', '.join(data['host'].get('addresses') or []) or 'unknown'}",
        f"检测到 OpenTenBase：{data['opentenbase'].get('detected')}",
        f"版本：{data['opentenbase'].get('version')}",
        f"二进制目录：{data['opentenbase'].get('binary_root')}",
        f"psql: {data['opentenbase'].get('psql')}",
        f"postgres: {data['opentenbase'].get('postgres')}",
        f"pg_config: {data['opentenbase'].get('pg_config')}",
        f"管理工具：{data['management'].get('selected')} ({data['management'].get('confidence')})",
        f"配置文件数量：{len(data.get('config_files', []))}",
        f"进程数量：{len(data.get('processes', []))}",
        f"端口数量：{len(data.get('ports', []))}",
        f"可连接 CN：{len(data['database'].get('reachable_cn', []))}",
        f"CN 数量：{len(data['topology'].get('coordinators', []))}",
        f"DN 数量：{len(data['topology'].get('datanodes', []))}",
        f"一致性：{data['consistency'].get('status')}",
        "是否允许写操作：false",
    ]
    warnings = data.get("consistency", {}).get("warnings", [])
    if warnings:
        lines.append("警告：")
        lines.extend(f"- {item}" for item in warnings)
    if data.get("management", {}).get("evidence"):
        lines.append("管理工具证据：")
        lines.extend(f"- {item}" for item in data["management"]["evidence"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="只读识别 OpenTenBase 环境")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--output", help="将 JSON 摘要写入指定路径")
    parser.add_argument("--no-database", action="store_true", help="跳过 psql 检查")
    parser.add_argument("--config-search-root", default="/data/opentenbase", help="主要配置搜索根目录，搜索有深度限制")
    parser.add_argument("--extra-config-search-root", action="append", default=[], help="额外配置搜索根目录，搜索有深度限制")
    parser.add_argument("--max-depth", type=int, default=5, help="最大配置搜索深度")
    args = parser.parse_args(argv)

    data = build_summary(args)
    if args.output:
        Path(args.output).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(render_human(data))
    if data["opentenbase"]["detected"]:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
