#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path


def parse_ssh_command(ssh_cmd: str) -> tuple[str, str, str]:
    parts = shlex.split(ssh_cmd)
    if not parts or parts[0] != "ssh":
        raise SystemExit("SSH_CMD must start with 'ssh'")

    host = None
    port = None
    key = None
    i = 1
    while i < len(parts):
        part = parts[i]
        if part == "-p":
            i += 1
            if i >= len(parts):
                raise SystemExit("Missing value after -p")
            port = parts[i]
        elif part == "-i":
            i += 1
            if i >= len(parts):
                raise SystemExit("Missing value after -i")
            key = os.path.expanduser(parts[i])
        elif not part.startswith("-") and host is None:
            host = part
        i += 1

    if host is None:
        raise SystemExit("Could not find SSH host in SSH_CMD")
    if port is None:
        raise SystemExit("Could not find SSH port in SSH_CMD")
    if key is None:
        raise SystemExit("Could not find SSH identity file in SSH_CMD")

    return host, port, key


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ssh-cmd", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    host, port, key = parse_ssh_command(args.ssh_cmd)
    output_path = Path(args.output)
    output_path.write_text(
        f"SSH_HOST := {host}\nSSH_PORT := {port}\nSSH_KEY := {key}\n",
        encoding="utf-8",
    )

    print(f"Wrote {output_path}")
    print(f"SSH_HOST={host}")
    print(f"SSH_PORT={port}")
    print(f"SSH_KEY={key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
