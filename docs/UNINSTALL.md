# Remove the recorded Caelestia installation

Caelestia was successfully removed from the original Parrot laptop on
**7 October 2026**. The laptop returned to Plasma (Wayland). Hyprland and the
shared APT dependencies remain installed.

The existing `snapshot/` preserves the working installation from before
removal. Keep that snapshot for reference or reproduction. Exporting again
after uninstalling cannot reproduce it: the running shell and its source
checkout have been deleted.

## Scope

[`scripts/remove-caelestia.py`](../scripts/remove-caelestia.py) targets the
source-built setup described in [Installation](INSTALL.md): Parrot 7 Echo,
Qt 6.8.2, Quickshell 0.3.1, and Caelestia v1.1.1 with local fixes. It is not
a general uninstaller for arbitrary Caelestia installations.

The script removes:

- The marked Caelestia startup and shortcut block in `hyprland.lua`, after
  saving a timestamped backup. It preserves the existing Brave shortcut.
- The pipx-managed `caelestia` CLI environment.
- Caelestia's native helpers, QML plugin, user configuration, generated state,
  dedicated caches and fonts, and source folders.
- The custom Quickshell, M3Shapes, and libcava builds and their source folders
  when no other Quickshell configuration is found in the checked XDG locations.
- Whitelisted vendored development files recorded by Quickshell's CMake
  install manifest, when that manifest exists and the helper builds are removed.
- The temporary dinosaur avatar, only when `~/.face` exactly matches the
  installed `assets/dino.png`.

APT-owned files are checked before removal. Unexpected directory symlinks
or an incomplete startup block cause the script to stop for inspection.
Other Quickshell configurations found in the checked locations cause the
shared engine and helper builds to be retained. The script does not detect
every possible custom configuration path or another project's use of a
locally installed development library; review its preview for such setups.

Plasma, Hyprland, Zsh, Konsole, Brave, personal wallpaper images, the dotfiles
repository, and shared APT packages are outside the removal scope. There is
no APT purge or autoremove operation.

## 1. Return to Plasma

Save your work and log out of Hyprland. With the recorded bindings,
**Super + Shift + E** exits the session. Select **Plasma (Wayland)** on the
login screen and open Konsole.

Run the script as your normal desktop user. Do not put `sudo` before Python;
the script asks for sudo only when removing installed system files.

## 2. Preview the removal

From this repository:

```bash
python3 scripts/remove-caelestia.py
```

This prints the removal plan without modifying settings or deleting files.
Check that the listed paths correspond to this installation.

## 3. Remove the setup

```bash
python3 scripts/remove-caelestia.py --remove
```

Enter your password if prompted. The script requests that the Caelestia
instance stop, updates Hyprland's configuration, uninstalls the CLI, removes
the identified files, and refreshes the library and font caches.

The confirmed run finished with:

```text
uninstalled caelestia!

The recorded Caelestia installation has been removed.
Shared APT packages remain installed; no APT purge or autoremove was performed.
```

The script checks that its identified removal targets no longer exist and
that the Caelestia executable is no longer on PATH. If it prints
`Cleanup stopped`, inspect that error before assuming the removal completed.

## Reinstalling later

Use [Installation](INSTALL.md) and the saved snapshot to rebuild and restore
the recorded setup. Restoring dotfiles alone does not reinstall the removed
binaries or QML plugins. The snapshot is historical evidence of the working
desktop, rather than a snapshot of the laptop after removal.

## Validation

The removal helper was checked with isolated fixtures for startup-block
editing, retaining independent shortcuts and personal files, APT ownership,
symlink handling, manifest path selection, and other Quickshell configurations.
Its removal run also completed successfully on the original Parrot laptop.
