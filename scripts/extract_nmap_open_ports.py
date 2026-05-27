#!/usr/bin/env python3
"""Extract open-port details from Nmap XML output."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

OPEN_STATES = {"open", "open|filtered", "unfiltered"}


def host_address(host: ET.Element) -> str:
    for addrtype in ("ipv4", "ipv6"):
        addr = host.find(f"./address[@addrtype='{addrtype}']")
        if addr is not None and addr.get("addr"):
            return addr.get("addr", "")
    fallback = host.find("./address")
    if fallback is not None and fallback.get("addr"):
        return fallback.get("addr", "")
    return "unknown_host"


def iter_open_ports(host: ET.Element) -> Iterable[dict[str, str]]:
    for port in host.findall("./ports/port"):
        state_el = port.find("./state")
        if state_el is None:
            continue
        state = state_el.get("state", "unknown")
        if state not in OPEN_STATES:
            continue

        service_el = port.find("./service")
        yield {
            "port": port.get("portid", "unknown"),
            "protocol": port.get("protocol", "unknown"),
            "state": state,
            "service_name": service_el.get("name", "unknown") if service_el is not None else "unknown",
            "product": service_el.get("product", "unknown") if service_el is not None else "unknown",
            "version": service_el.get("version", "unknown") if service_el is not None else "unknown",
            "extrainfo": service_el.get("extrainfo", "unknown") if service_el is not None else "unknown",
            "service_confidence": service_el.get("conf", "unknown") if service_el is not None else "unknown",
        }


def sort_key_host_port(row: dict[str, str]) -> tuple[str, int, str]:
    try:
        port_num = int(row["port"])
    except ValueError:
        port_num = 0
    return (row["host"], port_num, row["protocol"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parse Nmap XML and write: "
            "(1) CSV of open ports by host and "
            "(2) host-to-open-port-list mapping file."
        )
    )
    parser.add_argument("input_xml", help="Path to Nmap XML file.")
    parser.add_argument("output_csv", help="CSV path for open port rows.")
    parser.add_argument(
        "output_host_ports",
        help="Text path for host-to-open-ports map (format: host|comma,separated,ports).",
    )
    args = parser.parse_args()

    xml_path = Path(args.input_xml)
    csv_path = Path(args.output_csv)
    map_path = Path(args.output_host_ports)

    if not xml_path.exists():
        raise FileNotFoundError(f"input file not found: {xml_path}")

    root = ET.parse(xml_path).getroot()

    rows: list[dict[str, str]] = []
    host_ports: dict[str, set[str]] = {}

    for host in root.findall("./host"):
        status_el = host.find("./status")
        if status_el is None or status_el.get("state") != "up":
            continue

        host_id = host_address(host)
        host_ports.setdefault(host_id, set())

        for row in iter_open_ports(host):
            row["host"] = host_id
            rows.append(row)
            host_ports[host_id].add(row["port"])

    rows.sort(key=sort_key_host_port)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "host",
        "port",
        "protocol",
        "state",
        "service_name",
        "product",
        "version",
        "extrainfo",
        "service_confidence",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    with map_path.open("w", encoding="utf-8", newline="\n") as handle:
        for host_id in sorted(host_ports):
            ports = sorted(host_ports[host_id], key=lambda value: int(value) if value.isdigit() else 0)
            handle.write(f"{host_id}|{','.join(ports)}\n")

    print(f"rows={len(rows)} hosts={len(host_ports)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
