#!/usr/bin/env python3
"""Apply the documented fixes to a Caelestia v1.1.1 source tree.

Use the exported patch instead when snapshot/patches/caelestia-qt68.patch
is available: that patch is generated from the actual running QML files.
"""
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = re.compile(
    r'(?m)^[ \t]*environment:\s*\(\{\s*\n'
    r'\s*LANG:\s*"C\.UTF-8",\s*\n'
    r'\s*LC_ALL:\s*"C\.UTF-8"\s*\n'
    r'\s*\}\)[ \t]*\n'
)
COMMANDS = {
    "services/Network.qml": [
        '["nmcli", "radio", "wifi"]',
        '["nmcli", "-g", "ACTIVE,SIGNAL,FREQ,SSID,BSSID,SECURITY", "d", "w"]',
    ],
    "services/SystemUsage.qml": ['["sensors"]'],
}


def planned_changes(source: Path) -> dict[Path, str]:
    elevation = source / "components/effects/Elevation.qml"
    if not elevation.is_file():
        raise ValueError("Source does not contain components/effects/Elevation.qml.")
    replacement = (
        ROOT / "overrides/quickshell/caelestia/components/effects/Elevation.qml"
    ).read_text()
    changes = {}
    if elevation.read_text() != replacement:
        changes[elevation] = replacement

    for relative, commands in COMMANDS.items():
        path = source / relative
        original = path.read_text()
        text = original
        transformed = [
            '["env", "LANG=C.UTF-8", "LC_ALL=C.UTF-8", ' + old[1:]
            for old in commands
        ]
        old_counts = [text.count(command) for command in commands]
        new_counts = [text.count(command) for command in transformed]
        env_count = len(ENVIRONMENT.findall(text))
        if all(count == 1 for count in old_counts) and env_count == len(commands):
            text = ENVIRONMENT.sub("", text)
            for old, new in zip(commands, transformed):
                text = text.replace(old, new, 1)
        elif not (
            all(count == 1 for count in new_counts)
            and all(count == 0 for count in old_counts)
            and env_count == 0
        ):
            raise ValueError(f"{relative}: unexpected or partially patched locale blocks.")
        if relative == "services/SystemUsage.qml":
            text = text.replace("&>/dev/null", ">/dev/null 2>&1")
        if text != original:
            changes[path] = text

    for path in source.rglob("*.qml"):
        if "build" in path.relative_to(source).parts:
            continue
        text = changes.get(path, path.read_text())
        if not re.search(r"(?<![\w.])Delegate(?:Chooser|Choice)\s*\{", text):
            continue
        if re.search(r"(?m)^import\s+Qt\.labs\.qmlmodels(?:\s|$)", text):
            continue
        match = re.search(r"(?m)^import\s+", text)
        if match is None:
            raise ValueError(f"{path}: unable to find a QML import.")
        text = text[:match.start()] + "import Qt.labs.qmlmodels\n" + text[match.start():]
        changes[path] = text
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Caelestia v1.1.1 source directory")
    parser.add_argument("--check", action="store_true", help="Report changes without writing")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    baseline = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "v1.1.1^{commit}"],
        capture_output=True, text=True, check=True
    ).stdout.strip()
    head = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True
    ).stdout.strip()
    if head != baseline:
        raise SystemExit("Use a source tree checked out at v1.1.1.")
    changes = planned_changes(source)
    if args.check:
        for path in changes:
            print(f"Would update: {path.relative_to(source)}")
        print(f"{len(changes)} file(s) need changes.")
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path, content in changes.items():
        backup = path.with_name(path.name + ".before-qt68-" + stamp)
        shutil.copy2(path, backup)
        path.write_text(content)
        print(f"Updated: {path.relative_to(source)}")
    print("Compatibility fixes applied." if changes else "Fixes are already applied.")


if __name__ == "__main__":
    main()
