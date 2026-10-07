#!/usr/bin/env python3
"""Remove the Caelestia setup built during the recorded Parrot installation.

Run as your normal user after logging into Plasma (Wayland):
    python3 remove-caelestia.py            # preview only
    python3 remove-caelestia.py --remove   # perform the removal

APT packages, Plasma, Hyprland, terminal configuration, personal wallpaper
images, and the dotfiles repository are outside this script's removal scope.
Shared Qt/system development packages are intentionally retained.

CLI removal uses pipx: https://pipx.pypa.io/stable/reference/cli.html
Quickshell kill command: https://manpages.debian.org/unstable/quickshell/quickshell.1.en.html
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def exists(path):
    return os.path.lexists(path)


def checked_parent(path):
    # Do not recurse into a destination reached through a directory symlink.
    for parent in path.parents:
        if parent.is_symlink():
            raise RuntimeError(f"Directory symlink needs a manual check: {parent}")


def startup_edit(home):
    path = home / ".config/hypr/hyprland.lua"
    if not exists(path):
        return None
    checked_parent(path)
    if path.is_symlink():
        raise RuntimeError(f"Hyprland config is a symlink; edit its target manually: {path}")
    text = path.read_text()
    begin = "-- BEGIN CAELESTIA SETUP"
    end = "-- END CAELESTIA SETUP"
    pattern = re.compile(
        r"(?ms)^[ \t]*-- BEGIN CAELESTIA SETUP[^\n]*\n.*?"
        r"^[ \t]*-- END CAELESTIA SETUP[^\n]*(?:\n|$)"
    )
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise RuntimeError("Caelestia startup markers are incomplete or repeated; inspect hyprland.lua first.")
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            raise RuntimeError("Cannot safely identify the Caelestia startup block in hyprland.lua.")
        block = matches[0].group()
        updated = pattern.sub("", text, count=1)
        # Brave is an independent application; preserve its existing shortcut.
        brave = 'hl.bind("SUPER + B", hl.dsp.exec_cmd("brave-browser"))'
        if brave in block and brave not in updated:
            updated = updated.rstrip() + "\n\n" + brave + "\n"
    else:
        updated = text
    active_lines = "\n".join(line for line in updated.splitlines() if not line.lstrip().startswith("--"))
    if re.search(r"caelestia|quickshell", active_lines, re.IGNORECASE):
        raise RuntimeError("Other Caelestia/Quickshell entries exist in hyprland.lua; remove those entries first.")
    return (path, text, updated) if updated != text else None


def other_quickshell_configs(home):
    roots = {home / ".config/quickshell", Path("/etc/xdg/quickshell")}
    for value in os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":"):
        if value and Path(value).is_absolute():
            roots.add(Path(value) / "quickshell")
    others = []
    for root in sorted(roots):
        if (root / "shell.qml").is_file():
            others.append(root / "shell.qml")
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if child.name != "caelestia" and (child / "shell.qml").is_file():
                    others.append(child / "shell.qml")
    return others


def pipx_app():
    executable = shutil.which("pipx")
    if not executable:
        if shutil.which("caelestia"):
            raise RuntimeError("Caelestia is on PATH but pipx is unavailable; locate its installation first.")
        return None
    result = subprocess.run([executable, "list", "--json"], capture_output=True, text=True, check=True)
    packages = json.loads(result.stdout).get("venvs", {})
    if "caelestia" in packages:
        return executable
    if shutil.which("caelestia"):
        raise RuntimeError("Caelestia is on PATH but is not the recorded pipx package; locate it first.")
    return None


def system_paths(include_helpers):
    qml = Path("/usr/lib/x86_64-linux-gnu/qt6/qml")
    paths = [Path("/usr/lib/caelestia"), qml / "Caelestia"]
    if include_helpers:
        paths += [
            Path("/usr/local/bin/quickshell"), Path("/usr/local/bin/qs"),
            Path("/usr/local/share/applications/org.quickshell.desktop"),
            Path("/usr/local/share/icons/hicolor/scalable/apps/org.quickshell.svg"),
            qml / "M3Shapes", Path("/usr/local/lib/libm3shapes.so"),
            Path("/usr/local/include/m3shapes"), Path("/usr/local/lib/cmake/M3Shapes"),
            Path("/usr/local/lib/libcava.so"), Path("/usr/local/lib/libcava.so.1"),
            Path("/usr/local/lib/libcava.so.1.0.0"), Path("/usr/local/include/cava"),
            Path("/usr/local/lib/pkgconfig/libcava.pc"),
        ]
    return [path for path in paths if exists(path)]


def vendored_files(home):
    # Quickshell installed static crash-reporting/build dependencies too.
    # Only remove paths recorded by its own CMake installation manifest.
    manifest = home / ".local/src/quickshell/build/install_manifest.txt"
    if not manifest.is_file():
        return [], "Quickshell install manifest missing: shared vendored development files are retained."
    directories = [
        Path("/usr/local/lib/cmake/zstd"), Path("/usr/local/lib/cmake/libdwarf"),
        Path("/usr/local/lib/cmake/cpptrace"), Path("/usr/local/include/cpptrace"),
        Path("/usr/local/include/ctrace"),
    ]
    individual = {Path(value) for value in (
        "/usr/local/lib/libzstd.a", "/usr/local/lib/libdwarf.a", "/usr/local/lib/libcpptrace.a",
        "/usr/local/include/zdict.h", "/usr/local/include/zstd.h", "/usr/local/include/zstd_errors.h",
        "/usr/local/include/libdwarf.h", "/usr/local/include/dwarf.h",
        "/usr/local/lib/pkgconfig/libzstd.pc", "/usr/local/lib/pkgconfig/libdwarf.pc",
    )}
    paths = set()
    for line in manifest.read_text().splitlines():
        # CMake can write an extra leading slash with prefix=/.
        path = Path("/" + line.lstrip("/"))
        if ".." in path.parts:
            raise RuntimeError("Unexpected parent traversal in Quickshell's install manifest.")
        if path in individual or any(root in path.parents for root in directories):
            if exists(path):
                if path.is_dir() and not path.is_symlink():
                    raise RuntimeError(f"Expected an installed file, found a directory: {path}")
                paths.add(path)
    return sorted(paths), None


def reject_package_owned(paths):
    for path in paths:
        checked_parent(path)
        queries = [str(path)]
        if path.is_dir() and not path.is_symlink():
            queries.append(str(path) + "/*")
        result = subprocess.run(["/usr/bin/dpkg-query", "-S", *queries], capture_output=True, text=True)
        if result.returncode == 0 or result.stdout.strip():
            raise RuntimeError(f"APT owns files at {path}; use the owning package's uninstaller instead.")
        if result.returncode != 1:
            raise RuntimeError(f"Cannot check package ownership for {path}: {result.stderr.strip()}")


def local_paths(home, include_helpers):
    names = [
        ".config/quickshell/caelestia", ".config/caelestia", ".cache/caelestia",
        ".local/state/caelestia", ".local/share/caelestia", ".local/share/fonts/caelestia",
        ".local/src/caelestia-cli", ".local/src/caelestia-shell-v1.1.1", ".local/src/caelestia-shell",
    ]
    if include_helpers:
        names += [".local/src/quickshell", ".local/src/m3shapes", ".local/src/libcava",
                  ".cache/quickshell"]
    paths = [home / name for name in names if exists(home / name)]
    face = home / ".face"
    dino = home / ".config/quickshell/caelestia/assets/dino.png"
    if face.is_file() and not face.is_symlink() and dino.is_file() and face.read_bytes() == dino.read_bytes():
        paths.append(face)
    for path in paths:
        checked_parent(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--remove", action="store_true", help="perform the displayed cleanup (default: preview)")
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError("Run this as your normal user, without sudo. It asks for sudo only for installed system files.")
    if args.remove and "KDE" not in os.environ.get("XDG_CURRENT_DESKTOP", "").upper().split(":"):
        raise RuntimeError("Log out, choose Plasma (Wayland), and run this from Konsole in that session.")

    home = Path.home()
    edit = startup_edit(home)
    pipx = pipx_app()
    others = other_quickshell_configs(home)
    include_helpers = not others
    installed = system_paths(include_helpers)
    vendor, notice = vendored_files(home) if include_helpers else ([], None)
    installed += vendor
    reject_package_owned(installed)
    local = local_paths(home, include_helpers)
    if notice:
        print(notice)
    if others:
        print("Other Quickshell configurations exist; their shared engine/libraries will be retained:")
        for path in others:
            print(f"  {path}")
    print("Caelestia removal plan:")
    if edit:
        print(f"  Remove the Caelestia startup/shortcuts block from {edit[0]}; save a backup.")
    if pipx:
        print("  Uninstall the pipx package: caelestia")
    for path in installed + local:
        print(f"  Delete {path}")
    if not args.remove:
        print("\nPreview only. To apply: python3 remove-caelestia.py --remove")
        return

    # Authenticate before changing the user's settings or removing files.
    if installed:
        subprocess.run(["sudo", "-v"], check=True)
    qs = Path("/usr/local/bin/quickshell")
    config = home / ".config/quickshell/caelestia"
    if qs.is_file() and config.is_dir():
        result = subprocess.run([str(qs), "-p", str(config), "kill", "--any-display"],
                                capture_output=True, text=True, timeout=15)
        print("Caelestia stop request sent (or no running instance found).")
    if edit:
        path, original, updated = edit
        if path.read_text() != original:
            raise RuntimeError("Hyprland configuration changed during cleanup; run the script again.")
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = path.with_name(path.name + ".before-removal-" + stamp)
        shutil.copy2(path, backup)
        path.write_text(updated)
        print(f"Hyprland settings backup: {backup}")
    if pipx:
        subprocess.run([pipx, "uninstall", "caelestia"], check=True)
    if installed:
        subprocess.run(["sudo", "--", "rm", "-rf", "--", *map(str, installed)], check=True)
        # Remove empty directories left by the manifest, without deleting unrelated contents.
        for root in (Path("/usr/local/lib/cmake/zstd"), Path("/usr/local/lib/cmake/libdwarf"),
                     Path("/usr/local/lib/cmake/cpptrace"), Path("/usr/local/include/cpptrace"),
                     Path("/usr/local/include/ctrace")) if include_helpers else ():
            if root.is_dir() and not root.is_symlink():
                subprocess.run(["sudo", "--", "find", str(root), "-depth", "-type", "d", "-empty", "-delete"], check=True)
        subprocess.run(["sudo", "/usr/sbin/ldconfig"], check=True)
    for path in local:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif exists(path):
            path.unlink()
    if shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f"], check=True)

    remaining = [path for path in installed + local if exists(path)]
    if remaining or shutil.which("caelestia"):
        raise RuntimeError("Some components remain; inspect the paths and any earlier error before continuing.")
    print("\nThe recorded Caelestia installation has been removed.")
    print("Shared APT packages remain installed; no APT purge or autoremove was performed.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"Cleanup stopped: {exc}", file=sys.stderr)
        sys.exit(1)
