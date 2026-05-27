#!/usr/bin/env python3
"""Extract live hosts from Nmap grepable output."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

UP_HOST_PATTERN = re.compile(r"^Host:\s+(\S+)\s+.*Status:\s+Up\b", re.IGNORECASE)


def parse_live_hosts(gnmap_text: str) -> list[str]:
    hosts: set[str] = set()
    for line in gnmap_text.splitlines():
        match = UP_HOST_PATTERN.search(line)
        if match:
            hosts.add(match.group(1))
    return sorted(hosts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract live host addresses from Nmap .gnmap host-discovery output."
    )
    parser.add_argument("input_gnmap", help="Path to Nmap .gnmap file.")
    parser.add_argument("output_txt", help="Path to output file with one host per line.")
    args = parser.parse_args()

    in_path = Path(args.input_gnmap)
    out_path = Path(args.output_txt)

    if not in_path.exists():
        raise FileNotFoundError(f"input file not found: {in_path}")

    hosts = parse_live_hosts(in_path.read_text(encoding="utf-8", errors="replace"))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(hosts) + ("\n" if hosts else ""), encoding="utf-8", newline="\n")

    print(f"live_hosts={len(hosts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
