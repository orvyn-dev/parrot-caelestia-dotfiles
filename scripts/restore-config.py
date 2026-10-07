#!/usr/bin/env python3
"""Restore the three desktop configuration files with timestamped backups."""
# SPDX-License-Identifier: GPL-3.0-only
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "config/hypr/hyprland.lua": ".config/hypr/hyprland.lua",
    "config/caelestia/shell.json": ".config/caelestia/shell.json",
    "config/caelestia/cli.json": ".config/caelestia/cli.json",
}


def restore(source, home, check=False):
    source, home = source.resolve(), home.resolve()
    for relative in FILES:
        if not (source / relative).is_file():
            raise ValueError(f"Required configuration missing: {relative}")
    for target_relative in FILES.values():
        target = home / target_relative
        if target.exists() and not target.is_file() and not target.is_symlink():
            raise ValueError(f"Configuration target is not a file: {target_relative}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_root = home / ".local/share/parrot-caelestia/backups" / stamp
    for relative, target_relative in FILES.items():
        target, incoming = home / target_relative, source / relative
        if target.is_file() and target.read_bytes() == incoming.read_bytes():
            print(f"Already matches: {target_relative}")
            continue
        if check:
            print(f"Would restore: {target_relative}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            backup = backup_root / target_relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                backup.symlink_to(os.readlink(target))
            else:
                shutil.copy2(target, backup)
            target.unlink()
        shutil.copy2(incoming, target)
        print(f"Restored: {target_relative}")
    if not check:
        print(f"Backups, when needed: {backup_root}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "snapshot",
                        help="Snapshot directory; defaults to this repository's snapshot")
    parser.add_argument("--reference", action="store_true",
                        help="Restore the bundled reference configuration instead")
    parser.add_argument("--check", action="store_true", help="Report without writing")
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit("Run as your normal desktop user, without sudo.")
    try:
        restore(ROOT if args.reference else args.source.expanduser(), Path.home(), args.check)
    except (ValueError, OSError) as error:
        raise SystemExit(f"Restore stopped: {error}") from error


if __name__ == "__main__":
    main()
