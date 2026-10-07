#!/usr/bin/env python3
"""Capture working dotfiles into a new snapshot without changing live settings."""
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE_REF = "v1.1.1"
BASE_COMMIT_PREFIX = "e405bf8d"
QML_DIRS = {"assets", "components", "config", "modules", "services", "utils"}
CONFIGS = {
    ".config/hypr/hyprland.lua": "config/hypr/hyprland.lua",
    ".config/caelestia/shell.json": "config/caelestia/shell.json",
    ".config/caelestia/cli.json": "config/caelestia/cli.json",
}
SOURCES = {
    "quickshell": ("quickshell", "https://github.com/quickshell-mirror/quickshell.git"),
    "caelestia-shell": ("caelestia-shell-v1.1.1", "https://github.com/caelestia-dots/shell.git"),
    "caelestia-cli": ("caelestia-cli", "https://github.com/caelestia-dots/cli.git"),
    "m3shapes": ("m3shapes", "https://github.com/soramanew/m3shapes.git"),
    "libcava": ("libcava", "https://github.com/LukashonakV/cava.git"),
}
CMAKE_KEYS = {
    "CMAKE_BUILD_TYPE", "CMAKE_INSTALL_PREFIX", "CMAKE_INSTALL_LIBDIR",
    "CMAKE_INSTALL_INCLUDEDIR", "CMAKE_INSTALL_RPATH", "DISTRIBUTOR",
    "INSTALL_QMLDIR", "INSTALL_QML_PREFIX", "INSTALL_QSCONFDIR",
    "INSTALL_LIBDIR", "ENABLE_MODULES", "VENDOR_CPPTRACE", "X11",
}


def run(argv: list[str], required: bool = False) -> str | None:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        if required:
            raise ValueError(f"Unable to run required command: {argv[0]}")
        return None
    if result.returncode != 0:
        if required:
            raise ValueError(f"Required command failed: {' '.join(argv[:3])}")
        return None
    return re.sub(r"\x1b\[[0-9;]*m", "", result.stdout).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\n" in value or "\r" in value:
        raise ValueError(f"Unsupported relative path: {value!r}")
    return path


def copy_file(source: Path, stage: Path, relative: str) -> None:
    target = stage / safe_relative(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def qml_path(relative: str) -> bool:
    path = safe_relative(relative)
    return path.suffix == ".qml" and (
        relative == "shell.qml" or path.parts[0] in QML_DIRS
    )


def installed_qml(runtime: Path) -> dict[str, str]:
    result = {}
    for path in runtime.rglob("*.qml"):
        relative = path.relative_to(runtime).as_posix()
        if not qml_path(relative):
            continue
        if path.is_symlink() or runtime.resolve() not in path.resolve().parents:
            raise ValueError(f"QML path leaves the installed configuration: {relative}")
        result[relative] = path.read_text()
    return result


def baseline_qml(source: Path) -> tuple[str, dict[str, str]]:
    commit = run(
        ["git", "-C", str(source), "rev-parse", BASE_REF + "^{commit}"], required=True
    )
    if not commit.startswith(BASE_COMMIT_PREFIX):
        raise ValueError("The v1.1.1 tag differs from the recorded upstream baseline.")
    files = run(
        ["git", "-C", str(source), "ls-tree", "-r", "--name-only", BASE_REF], required=True
    )
    result = {}
    for relative in files.splitlines():
        if not qml_path(relative):
            continue
        completed = subprocess.run(
            ["git", "-C", str(source), "show", f"{BASE_REF}:{relative}"],
            capture_output=True, text=True, timeout=20
        )
        if completed.returncode:
            raise ValueError(f"Cannot read upstream file: {relative}")
        result[relative] = completed.stdout
    return commit, result


def qml_diff(relative: str, before: str | None, after: str | None) -> str:
    """Emit a Git-applicable text diff, including missing final newlines."""
    if before == after:
        return ""
    headers = f"diff --git a/{relative} b/{relative}\n"
    if before is None:
        headers += "new file mode 100644\n"
    elif after is None:
        headers += "deleted file mode 100644\n"
    result = [headers]
    for line in difflib.unified_diff(
        (before or "").splitlines(keepends=True),
        (after or "").splitlines(keepends=True),
        fromfile="a/" + relative if before is not None else "/dev/null",
        tofile="b/" + relative if after is not None else "/dev/null",
    ):
        if line.endswith("\n"):
            result.append(line)
        else:
            result.extend((line + "\n", "\\ No newline at end of file\n"))
    return "".join(result)


def cmake_settings(path: Path, home: Path) -> dict[str, str]:
    result = {}
    if not path.is_file():
        return result
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(("#", "//")) or "=" not in line:
            continue
        left, value = line.split("=", 1)
        key = left.split(":", 1)[0]
        if key in CMAKE_KEYS:
            result[key] = value.replace(str(home), "$HOME")
    return result


def collect_sources(home: Path) -> dict:
    result = {}
    for name, (folder, url) in SOURCES.items():
        source = home / ".local/src" / folder
        if not source.is_dir():
            result[name] = {"upstream": url, "checkout_present": False}
            continue
        commit = run(["git", "-C", str(source), "rev-parse", "HEAD"])
        dirty = run([
            "git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"
        ])
        result[name] = {
            "upstream": url,
            "checkout_present": True,
            "checkout_commit": commit,
            "tracked_checkout_changes": bool(dirty) if dirty is not None else None,
            "cmake_settings": cmake_settings(source / "build/CMakeCache.txt", home),
        }
    return result


def terminal_files(home: Path) -> list[tuple[Path, str]]:
    paths = {
        home / ".zshrc": "terminal/home/.zshrc",
        home / ".zshenv": "terminal/home/.zshenv",
        home / ".config/starship.toml": "terminal/config/starship.toml",
        home / ".config/konsolerc": "terminal/config/konsolerc",
    }
    zsh = home / ".config/zsh"
    if zsh.is_dir():
        for path in zsh.rglob("*"):
            if path.is_file() and (
                path.suffix == ".zsh"
                or path.name in {".zshrc", ".zshenv", "LICENSE", "README.md"}
            ):
                paths[path] = "terminal/config/zsh/" + path.relative_to(zsh).as_posix()
    konsole = home / ".local/share/konsole"
    if konsole.is_dir():
        for pattern in ("*.profile", "*.colorscheme"):
            for path in konsole.glob(pattern):
                paths[path] = "terminal/local-share/konsole/" + path.name
    return [(path, relative) for path, relative in paths.items() if path.is_file()]


def package_versions(root: Path) -> str:
    packages = set()
    for name in ("build.txt", "runtime.txt"):
        for line in (root / "packages" / name).read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                packages.add(line.strip())
    packages.update({
        "libgbm1", "libpipewire-0.3-0t64", "libxkbcommon0", "libcurl3t64-gnutls",
    })
    # Build dpkg's format without expanding anything in a shell.
    fmt = "$" + "{db:Status-Status}\t$" + "{binary:Package}\t$" + "{Version}\n"
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f", fmt, *sorted(packages)],
            capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.TimeoutExpired):
        return "# dpkg-query unavailable; no package versions captured.\n"
    rows = []
    for row in result.stdout.splitlines():
        fields = row.split("\t")
        if len(fields) == 3 and fields[0] == "installed":
            rows.append("\t".join(fields[1:]))
    return "\n".join(sorted(rows)) + "\n"


def export(home: Path, destination: Path, root: Path, include_terminal: bool) -> dict:
    home = home.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise ValueError("Snapshot directory already exists. Choose a new --output path.")
    if destination == home or destination in home.parents:
        raise ValueError("Snapshot destination must be a separate directory.")
    for relative in CONFIGS:
        path = home / relative
        if not path.is_file():
            raise ValueError(f"Required working configuration missing: {relative}")
        if path.suffix == ".json" and not isinstance(json.loads(path.read_text()), dict):
            raise ValueError(f"Expected a JSON object: {relative}")
    runtime = home / ".config/quickshell/caelestia"
    source = home / ".local/src/caelestia-shell-v1.1.1"
    baseline_commit, baseline = baseline_qml(source)
    current = installed_qml(runtime)
    if "shell.qml" not in current:
        raise ValueError("Installed Caelestia shell.qml missing.")
    license_path = runtime / "LICENSE"
    if not license_path.is_file():
        license_path = source / "LICENSE"
    if not license_path.is_file():
        raise ValueError("Unable to find Caelestia's upstream LICENSE.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="caelestia-export-", dir=destination.parent) as work:
        stage = Path(work) / "snapshot"
        stage.mkdir()
        for relative, output in CONFIGS.items():
            copy_file(home / relative, stage, output)
        copy_file(license_path, stage, "licenses/Caelestia-LICENSE")
        changed, deleted, diffs = [], [], []
        for relative in sorted(set(baseline) | set(current)):
            before, after = baseline.get(relative), current.get(relative)
            if before == after:
                continue
            if after is None:
                deleted.append(relative)
            else:
                changed.append(relative)
                copy_file(runtime / relative, stage,
                          "overrides/quickshell/caelestia/" + relative)
            diffs.append(qml_diff(relative, before, after))
        patch_path = stage / "patches/caelestia-qt68.patch"
        patch_path.parent.mkdir()
        patch_path.write_text("".join(diffs))
        if include_terminal:
            for path, relative in terminal_files(home):
                copy_file(path, stage, relative)
        (stage / "packages.tsv").write_text(package_versions(root))
        commands = {
            "hyprland": ["Hyprland", "--version"],
            "quickshell": ["/usr/local/bin/quickshell", "--version"],
            "caelestia_cli": [str(home / ".local/bin/caelestia"), "--version"],
            "qt_version": ["qmake6", "-query", "QT_VERSION"],
            "qt_qml_directory": ["qmake6", "-query", "QT_INSTALL_QML"],
            "rubik_font": ["fc-match", "-f", "%{family}\n", "Rubik"],
            "material_font": ["fc-match", "-f", "%{family}\n", "Material Symbols Rounded"],
            "monospace_font": ["fc-match", "-f", "%{family}\n", "CaskaydiaCove NF"],
        }
        versions = {name: run(command) for name, command in commands.items()}
        versions = {
            name: value.replace(str(home), "$HOME") if value else value
            for name, value in versions.items()
        }
        hashes = {
            path.relative_to(stage).as_posix(): sha256(path)
            for path in sorted(stage.rglob("*")) if path.is_file()
        }
        manifest = {
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "record_type": "actual laptop export",
            "caelestia_baseline_tag": BASE_REF,
            "caelestia_baseline_commit": baseline_commit,
            "qml_patch_files": changed,
            "qml_deleted_files": deleted,
            "include_terminal": include_terminal,
            "versions": versions,
            "sources": collect_sources(home),
            "font_sha256": {
                path.name: sha256(path)
                for path in (home / ".local/share/fonts/caelestia").glob("*.ttf")
                if path.is_file()
            },
            "files_sha256": hashes,
            "notes": [
                "Source checkout commits and installed binary versions are separate observations.",
                "Only selected dotfiles, QML differences, and dependency metadata were exported.",
                "Wallpaper images, .face, credentials, logs, and runtime state are not exported.",
            ],
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (stage / "SHA256SUMS").write_text(
            "".join(f"{value}  {name}\n" for name, value in sorted(hashes.items()))
        )
        os.rename(stage, destination)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "snapshot")
    parser.add_argument("--include-terminal", action="store_true",
                        help="Also export Zsh, Starship, and Konsole settings")
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit("Run as your normal desktop user, without sudo.")
    try:
        manifest = export(Path.home(), args.output, ROOT, args.include_terminal)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Export stopped: {error}") from error
    print(f"Snapshot saved: {args.output.expanduser().resolve()}")
    print(f"QML changes: {len(manifest['qml_patch_files'])}")
    print(f"QML deletions: {len(manifest['qml_deleted_files'])}")
    print("Review the snapshot, then follow docs/EXPORT-AND-GITHUB.md.")


if __name__ == "__main__":
    main()
