#!/usr/bin/env python3
"""只读 OpenTenBase 环境识别脚本。

本脚本只执行有边界的只读检查。JSON 字段保持英文，便于后续自动化消费；
人类可读输出使用中文。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT = 5
CONFIG_NAMES = {"opentenbase_config.ini", "config.ini", "pgxc_ctl.conf"}
SENSITIVE_RE = re.compile(r"(password|passwd|secret|token|private_key)\s*=\s*[^,\s]+", re.IGNORECASE)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(text: str) -> str:
    return SENSITIVE_RE.sub(lambda m: m.group(1) + "=<redacted>", text)


def split_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def command_path(name: str) -> str:
    return shutil.which(name) or "unknown"


def command_record(
    argv: list[str],
    *,
    purpose: str,
    kind: str = "shell",
    timeout: int = DEFAULT_TIMEOUT,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    started_at = now()
    try:
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, env=env)
        return {
            "kind": kind,
            "purpose": purpose,
            "argv": argv,
            "returncode": proc.returncode,
            "stdout": redact(proc.stdout.strip()),
            "stderr": redact(proc.stderr.strip()),
            "timeout": False,
            "started_at": started_at,
            "finished_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    except FileNotFoundError as exc:
        return {
            "kind": kind,
            "purpose": purpose,
            "argv": argv,
            "returncode": 127,
            "stdout": "",
            "stderr": str(exc),
            "timeout": False,
            "started_at": started_at,
            "finished_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else "command timed out"
        return {
            "kind": kind,
            "purpose": purpose,
            "argv": argv,
            "returncode": 124,
            "stdout": redact(stdout.strip()),
            "stderr": redact(stderr.strip()),
            "timeout": True,
            "started_at": started_at,
            "finished_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    except Exception as exc:  # 保持识别流程继续
        return {
            "kind": kind,
            "purpose": purpose,
            "argv": argv,
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "timeout": False,
            "started_at": started_at,
            "finished_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }


class Recorder:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def run(
        self,
        argv: list[str],
        *,
        purpose: str,
        kind: str = "shell",
        timeout: int = DEFAULT_TIMEOUT,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        result = command_record(argv, purpose=purpose, kind=kind, timeout=timeout, env=env)
        self.records.append(result)
        return result


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


def parse_role_entries(text: str, *, role: str, name_key: str, port_keys: list[str], host_key: str, source: str) -> list[dict[str, Any]]:
    names = extract_assignment(text, name_key)
    ports: list[str] = []
    for key in port_keys:
        ports = extract_assignment(text, key)
        if ports:
            break
    hosts = extract_assignment(text, host_key)
    entries: list[dict[str, Any]] = []
    for idx, port in enumerate(ports):
        port = clean_token(port)
        if not port.isdigit():
            continue
        host = clean_token(hosts[idx]) if idx < len(hosts) else "127.0.0.1"
        if not is_sane_host(host):
            continue
        entries.append(
            {
                "source": source,
                "role": role,
                "name": names[idx] if idx < len(names) else f"{role}{idx + 1}",
                "host": normalize_host(host),
                "port": port,
            }
        )
    return entries


def parse_pgxc_configs(config_paths: list[str]) -> dict[str, Any]:
    parsed = {"gtm": [], "coordinators": [], "datanodes": [], "warnings": []}
    for path in config_paths:
        if not path.endswith("pgxc_ctl.conf"):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            parsed["warnings"].append(f"无法读取 pgxc_ctl.conf：{path}: {exc}")
            continue
        parsed["coordinators"].extend(
            parse_role_entries(
                text,
                role="coordinator",
                name_key="coordNames",
                port_keys=["coordPorts", "coordForwardPorts"],
                host_key="coordMasterServers",
                source=path,
            )
        )
        parsed["datanodes"].extend(
            parse_role_entries(
                text,
                role="datanode",
                name_key="datanodeNames",
                port_keys=["datanodePorts", "datanodeForwardPorts"],
                host_key="datanodeMasterServers",
                source=path,
            )
        )
        gtm_entries = parse_role_entries(
            text,
            role="gtm",
            name_key="gtmName",
            port_keys=["gtmPort"],
            host_key="gtmMasterServer",
            source=path,
        )
        parsed["gtm"].extend(gtm_entries)
    return parsed


def process_info(recorder: Recorder) -> list[dict[str, Any]]:
    result = recorder.run(["ps", "-ef"], purpose="查看 OpenTenBase/PostgreSQL 相关进程")
    rows = []
    for line in split_lines(result["stdout"]):
        lower = line.lower()
        if any(token in lower for token in ("postgres", "gtm", "pgxc", "opentenbase")):
            rows.append({"line": line, "role_hint": process_role_hint(lower)})
    return rows


def process_role_hint(lower_line: str) -> str:
    if "gtm" in lower_line:
        return "gtm"
    if "coordinator" in lower_line or "coord" in lower_line or "cn" in lower_line:
        return "coordinator"
    if "datanode" in lower_line or "dn" in lower_line:
        return "datanode"
    if "postgres" in lower_line:
        return "postgres"
    return "unknown"


def port_info(recorder: Recorder) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    argv = ["ss", "-lntp"] if command_path("ss") != "unknown" else ["netstat", "-lntp"]
    result = recorder.run(argv, purpose="查看监听端口")
    rows = []
    if result["returncode"] != 0:
        warnings.append(f"端口命令执行失败：{result['stderr'] or result['returncode']}")
    for line in split_lines(result["stdout"]):
        lower = line.lower()
        if any(token in lower for token in ("postgres", "gtm", "opentenbase")):
            rows.append({"line": line, "ports": extract_ports_from_line(line)})
    if not rows and result["stdout"]:
        warnings.append("端口命令有输出，但权限可能隐藏了进程名")
    return rows, warnings


def extract_ports_from_line(line: str) -> list[str]:
    ports = []
    for match in re.finditer(r"(?<!:):(\d{1,5})\b", line):
        port = match.group(1)
        if 0 < int(port) <= 65535:
            ports.append(port)
    return sorted(set(ports))


def listener_ports(ports: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for row in ports:
        result.update(str(p) for p in row.get("ports", []))
    return result


def version_from_command(recorder: Recorder, path: str, label: str) -> str:
    if path == "unknown":
        return "unknown"
    result = recorder.run([path, "--version"], purpose=f"读取 {label} 版本")
    return result["stdout"].splitlines()[0] if result["returncode"] == 0 and result["stdout"] else "unknown"


def pg_config_value(recorder: Recorder, pg_config: str, flag: str, purpose: str) -> str:
    if pg_config == "unknown":
        return "unknown"
    result = recorder.run([pg_config, flag], purpose=purpose)
    return result["stdout"].strip() if result["returncode"] == 0 and result["stdout"] else "unknown"


def normalize_host(host: str) -> str:
    if host in {"localhost", "0.0.0.0", "*", ""}:
        return "127.0.0.1"
    return host


def unique_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for cand in candidates:
        host = normalize_host(str(cand.get("host") or "127.0.0.1"))
        port = str(cand.get("port") or "")
        key = (host, port)
        if not port or key in seen:
            continue
        copy = dict(cand)
        copy["host"] = host
        copy["port"] = port
        seen.add(key)
        result.append(copy)
    return result


def database_query(
    recorder: Recorder,
    psql: str,
    *,
    host: str,
    port: str,
    database: str,
    user: str,
    sql: str,
    connect_timeout: int,
    purpose: str,
) -> dict[str, Any]:
    env = dict(os.environ)
    env["PGCONNECT_TIMEOUT"] = str(connect_timeout)
    argv = [psql, "-h", host, "-p", port, "-d", database, "-U", user, "-Atc", sql]
    return recorder.run(argv, purpose=purpose, kind="sql", timeout=max(DEFAULT_TIMEOUT, connect_timeout + 3), env=env)


def discover_database(
    recorder: Recorder,
    psql: str,
    candidates: list[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    database = {
        "reachable_cn": [],
        "server_version": "unknown",
        "current_database": "unknown",
        "current_user": "unknown",
        "pgxc_node_query_ok": False,
        "pgxc_node_error": "",
    }
    topology = {"gtm": [], "coordinators": [], "datanodes": []}
    warnings: list[str] = []
    if args.no_database:
        warnings.append("已通过 --no-database 跳过数据库检查")
        return database, topology, warnings
    if psql == "unknown":
        warnings.append("未找到 psql，跳过数据库检查")
        return database, topology, warnings

    user = args.db_user or os.environ.get("USER") or os.environ.get("LOGNAME") or "opentenbase"
    for cand in unique_candidates(candidates)[:8]:
        host = normalize_host(str(cand.get("host") or "127.0.0.1"))
        port = str(cand.get("port") or "")
        one = database_query(
            recorder,
            psql,
            host=host,
            port=port,
            database=args.database,
            user=user,
            sql="SELECT 1;",
            connect_timeout=args.connect_timeout,
            purpose=f"测试 CN 连接 {host}:{port}",
        )
        if one["returncode"] != 0:
            warnings.append(f"CN 候选 {host}:{port} 不可连接：{one['stderr'] or one['stdout']}")
            continue

        database["reachable_cn"].append({"host": host, "port": port, "source": cand.get("source", "candidate")})
        ver = database_query(
            recorder,
            psql,
            host=host,
            port=port,
            database=args.database,
            user=user,
            sql="SELECT version();",
            connect_timeout=args.connect_timeout,
            purpose=f"读取 server_version {host}:{port}",
        )
        cur_db = database_query(
            recorder,
            psql,
            host=host,
            port=port,
            database=args.database,
            user=user,
            sql="SELECT current_database();",
            connect_timeout=args.connect_timeout,
            purpose=f"读取 current_database {host}:{port}",
        )
        cur_user = database_query(
            recorder,
            psql,
            host=host,
            port=port,
            database=args.database,
            user=user,
            sql="SELECT current_user;",
            connect_timeout=args.connect_timeout,
            purpose=f"读取 current_user {host}:{port}",
        )
        node = database_query(
            recorder,
            psql,
            host=host,
            port=port,
            database=args.database,
            user=user,
            sql="SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;",
            connect_timeout=args.connect_timeout,
            purpose=f"读取 pgxc_node {host}:{port}",
        )
        if ver["returncode"] == 0 and ver["stdout"]:
            database["server_version"] = ver["stdout"].splitlines()[0]
        if cur_db["returncode"] == 0 and cur_db["stdout"]:
            database["current_database"] = cur_db["stdout"].splitlines()[0]
        if cur_user["returncode"] == 0 and cur_user["stdout"]:
            database["current_user"] = cur_user["stdout"].splitlines()[0]
        if node["returncode"] == 0:
            database["pgxc_node_query_ok"] = True
            for line in split_lines(node["stdout"]):
                parts = line.split("|")
                if len(parts) < 4:
                    continue
                item = {"name": parts[0], "type": parts[1], "host": parts[2], "port": parts[3], "source": "pgxc_node"}
                node_type = parts[1].upper()
                if node_type.startswith("C"):
                    topology["coordinators"].append(item)
                elif node_type.startswith("D"):
                    topology["datanodes"].append(item)
                elif "G" in node_type:
                    topology["gtm"].append(item)
        else:
            database["pgxc_node_error"] = node["stderr"] or node["stdout"]
            warnings.append(f"在 {host}:{port} 查询 pgxc_node 失败：{database['pgxc_node_error']}")
        break

    if not database["reachable_cn"] and not candidates:
        warnings.append("没有显式 CN 参数，也没有从配置中发现 CN 候选；不会凭端口号猜测 CN")
    return database, topology, warnings


def contains_opentenbase(text: str) -> bool:
    return "opentenbase" in (text or "").lower()


def detection_summary(
    *,
    server_version: str,
    psql_version: str,
    postgres_binary_version: str,
    pg_config_version: str,
    config_paths: list[str],
    processes: list[dict[str, Any]],
    topology: dict[str, Any],
) -> dict[str, Any]:
    evidence: list[str] = []
    if contains_opentenbase(server_version):
        evidence.append("server_version 包含 OpenTenBase")
    if topology.get("coordinators") or topology.get("datanodes"):
        evidence.append("pgxc_node 返回 CN/DN 拓扑")
    if contains_opentenbase(postgres_binary_version):
        evidence.append("postgres_binary_version 包含 OpenTenBase")
    if contains_opentenbase(pg_config_version):
        evidence.append("pg_config_version 包含 OpenTenBase")
    if any("opentenbase" in p.lower() or p.endswith("pgxc_ctl.conf") for p in config_paths):
        evidence.append("发现 OpenTenBase/pgxc 相关配置")
    if processes:
        evidence.append("发现 OpenTenBase/PostgreSQL/GTM 相关进程")

    binary_only = (
        not contains_opentenbase(server_version)
        and not (topology.get("coordinators") or topology.get("datanodes"))
        and (contains_opentenbase(postgres_binary_version) or contains_opentenbase(pg_config_version))
    )
    if contains_opentenbase(server_version) or (topology.get("coordinators") or topology.get("datanodes")):
        confidence = "high"
        detected = True
    elif binary_only and (config_paths or processes):
        confidence = "medium"
        detected = True
    elif binary_only:
        confidence = "low"
        detected = True
    else:
        confidence = "none"
        detected = False

    if not evidence and (psql_version != "unknown" or postgres_binary_version != "unknown" or pg_config_version != "unknown"):
        evidence.append("仅发现 PostgreSQL 工具版本，不能证明是 OpenTenBase")

    return {"detected": detected, "confidence": confidence, "evidence": evidence}


def management_selection(
    tool_entries: list[dict[str, Any]],
    config_paths: list[str],
    processes: list[dict[str, Any]],
    topology: dict[str, Any],
) -> dict[str, Any]:
    names = {c["name"] for c in tool_entries}
    evidence: list[str] = []
    for c in tool_entries:
        evidence.append(f"{c['name']} 二进制：{c['path']}")
    for path in config_paths:
        if path.endswith("pgxc_ctl.conf"):
            evidence.append(f"pgxc_ctl 配置：{path}")
        elif path.endswith(".ini") or path.endswith("config.ini"):
            evidence.append(f"opentenbase_ctl 风格配置候选：{path}")
    if processes:
        evidence.append(f"相关进程行数：{len(processes)}")
    if topology.get("coordinators") or topology.get("datanodes"):
        evidence.append("pgxc_node 可读，已获得数据库拓扑")

    otb_score = 0
    pgxc_score = 0
    if "opentenbase_ctl" in names:
        otb_score += 1
    if "pgxc_ctl" in names:
        pgxc_score += 1
    if any(p.endswith("opentenbase_config.ini") or p.endswith("config.ini") for p in config_paths):
        otb_score += 1
    if any(p.endswith("pgxc_ctl.conf") for p in config_paths):
        pgxc_score += 1
    if processes:
        otb_score += 1
        pgxc_score += 1
    if topology.get("coordinators") or topology.get("datanodes"):
        otb_score += 1
        pgxc_score += 1

    selected = "unknown"
    confidence = "unknown"
    if otb_score >= 3 and otb_score >= pgxc_score + 2:
        selected = "opentenbase_ctl"
        confidence = "medium"
    elif pgxc_score >= 3 and pgxc_score >= otb_score + 2:
        selected = "pgxc_ctl"
        confidence = "medium"
    elif otb_score > 0 and pgxc_score > 0:
        selected = "ambiguous"
        confidence = "low"
    elif otb_score > 0:
        selected = "opentenbase_ctl"
        confidence = "low"
    elif pgxc_score > 0:
        selected = "pgxc_ctl"
        confidence = "low"

    return {
        "selected": selected,
        "confidence": confidence,
        "scores": {"opentenbase_ctl": otb_score, "pgxc_ctl": pgxc_score},
        "candidates": tool_entries,
        "evidence": evidence,
    }


def consistency_status(config_topology: dict[str, Any], db_topology: dict[str, Any], processes: list[dict[str, Any]], ports: list[dict[str, Any]], warnings: list[str]) -> dict[str, Any]:
    local_warnings = list(config_topology.get("warnings", [])) + list(warnings)
    config_cn = config_topology.get("coordinators", [])
    config_dn = config_topology.get("datanodes", [])
    db_cn = db_topology.get("coordinators", [])
    db_dn = db_topology.get("datanodes", [])
    active_ports = listener_ports(ports)

    if config_cn and db_cn and len(config_cn) != len(db_cn):
        local_warnings.append("配置候选中的 CN 数量与 pgxc_node 查询结果不同")
    if config_dn and db_dn and len(config_dn) != len(db_dn):
        local_warnings.append("配置候选中的 DN 数量与 pgxc_node 查询结果不同")
    if active_ports:
        for item in config_cn + config_dn:
            if str(item.get("port")) not in active_ports:
                local_warnings.append(f"配置节点端口未在本机监听列表中出现：{item.get('name')}:{item.get('port')}")

    sources = sum(bool(x) for x in [config_cn or config_dn, db_cn or db_dn, processes, ports])
    if local_warnings:
        status = "ambiguous" if (config_cn or config_dn) and (db_cn or db_dn) else "partial"
    elif sources >= 3:
        status = "consistent"
    elif sources >= 2:
        status = "partial"
    else:
        status = "unknown"
        local_warnings.append("拓扑证据不足")

    return {"status": status, "warnings": sorted(set(local_warnings))}


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    recorder = Recorder()
    errors: list[str] = []
    warnings: list[str] = []

    host_addresses = split_lines(recorder.run(["hostname", "-I"], purpose="读取主机 IP 地址")["stdout"])
    tool_names = ["opentenbase_ctl", "pgxc_ctl", "psql", "postgres", "pg_config"]
    tool_entries = []
    for name in tool_names:
        path = command_path(name)
        if path != "unknown":
            type_result = recorder.run(["bash", "-lc", f"type -a {name}"], purpose=f"定位 {name}") if command_path("bash") != "unknown" else None
            tool_entries.append({"name": name, "path": path, "type_a": type_result["stdout"] if type_result else ""})

    roots = [Path.home(), Path.cwd(), Path(args.config_search_root)]
    roots.extend(Path(p) for p in args.extra_config_search_root)
    config_paths: list[str] = []
    for root in roots:
        config_paths.extend(bounded_find(root, max_depth=args.max_depth))
    config_paths = sorted(set(config_paths))
    config_topology = parse_pgxc_configs(config_paths)

    processes = process_info(recorder)
    ports, port_warnings = port_info(recorder)
    warnings.extend(port_warnings)

    psql = command_path("psql")
    pg_config = command_path("pg_config")
    postgres = command_path("postgres")
    psql_version = version_from_command(recorder, psql, "psql")
    postgres_binary_version = version_from_command(recorder, postgres, "postgres")
    pg_config_version = version_from_command(recorder, pg_config, "pg_config")
    binary_root = pg_config_value(recorder, pg_config, "--bindir", "读取 pg_config --bindir")

    cn_candidates: list[dict[str, Any]] = []
    if args.cn_host and args.cn_port:
        cn_candidates.append(
            {
                "source": "explicit_args",
                "role": "coordinator",
                "name": "explicit_cn",
                "host": args.cn_host,
                "port": str(args.cn_port),
            }
        )
    cn_candidates.extend(config_topology.get("coordinators", []))

    database, db_topology, db_warnings = discover_database(recorder, psql, cn_candidates, args)
    warnings.extend(db_warnings)

    detection = detection_summary(
        server_version=database["server_version"],
        psql_version=psql_version,
        postgres_binary_version=postgres_binary_version,
        pg_config_version=pg_config_version,
        config_paths=config_paths,
        processes=processes,
        topology=db_topology,
    )

    summary = {
        "timestamp": now(),
        "host": {
            "user": recorder.run(["whoami"], purpose="读取当前用户")["stdout"] or "unknown",
            "id": recorder.run(["id"], purpose="读取用户 id")["stdout"] or "unknown",
            "hostname": recorder.run(["hostname"], purpose="读取主机名")["stdout"] or socket.gethostname(),
            "addresses": host_addresses,
            "pwd": str(Path.cwd()),
            "uname": recorder.run(["uname", "-a"], purpose="读取内核信息")["stdout"] or "unknown",
        },
        "opentenbase": {
            "detected": detection["detected"],
            "confidence": detection["confidence"],
            "detection_evidence": detection["evidence"],
            "binary_root": binary_root,
            "psql": psql,
            "postgres": postgres,
            "pg_config": pg_config,
            "server_version": database["server_version"],
            "psql_version": psql_version,
            "postgres_binary_version": postgres_binary_version,
            "pg_config_version": pg_config_version,
        },
        "management": management_selection(tool_entries, config_paths, processes, db_topology),
        "config_files": [{"path": path} for path in config_paths],
        "config_topology": config_topology,
        "processes": processes,
        "ports": ports,
        "database": database,
        "topology": db_topology,
        "consistency": consistency_status(config_topology, db_topology, processes, ports, warnings),
        "safety": {
            "write_operations_allowed": False,
            "reason": "system-entry 按设计只读",
        },
        "command_evidence": recorder.records,
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
        f"检测到 OpenTenBase：{data['opentenbase'].get('detected')} ({data['opentenbase'].get('confidence')})",
        f"server_version：{data['opentenbase'].get('server_version')}",
        f"psql_version：{data['opentenbase'].get('psql_version')}",
        f"postgres_binary_version：{data['opentenbase'].get('postgres_binary_version')}",
        f"pg_config_version：{data['opentenbase'].get('pg_config_version')}",
        f"二进制目录：{data['opentenbase'].get('binary_root')}",
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
    if data["opentenbase"].get("detection_evidence"):
        lines.append("检测证据：")
        lines.extend(f"- {item}" for item in data["opentenbase"]["detection_evidence"])
    warnings = data.get("consistency", {}).get("warnings", [])
    if warnings:
        lines.append("警告：")
        lines.extend(f"- {item}" for item in warnings)
    if data.get("management", {}).get("evidence"):
        lines.append("管理工具证据：")
        lines.extend(f"- {item}" for item in data["management"]["evidence"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="只读识别 OpenTenBase 环境")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--output", help="将 JSON 摘要写入指定路径")
    parser.add_argument("--db-user", help="数据库连接用户；默认使用当前 OS 用户")
    parser.add_argument("--database", default="postgres", help="连接的数据库名，默认 postgres")
    parser.add_argument("--cn-host", help="显式指定 CN host")
    parser.add_argument("--cn-port", help="显式指定 CN port")
    parser.add_argument("--connect-timeout", type=int, default=5, help="数据库连接超时秒数")
    parser.add_argument("--no-database", action="store_true", help="跳过 psql 检查")
    parser.add_argument("--config-search-root", default="/data/opentenbase", help="主要配置搜索根目录，搜索有深度限制")
    parser.add_argument("--extra-config-search-root", action="append", default=[], help="额外配置搜索根目录，搜索有深度限制")
    parser.add_argument("--max-depth", type=int, default=5, help="最大配置搜索深度")
    args = parser.parse_args(argv)
    if bool(args.cn_host) ^ bool(args.cn_port):
        parser.error("--cn-host 和 --cn-port 必须同时提供")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data = build_summary(args)
    if args.output:
        Path(args.output).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(render_human(data))
    return 0 if data["opentenbase"]["detected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
