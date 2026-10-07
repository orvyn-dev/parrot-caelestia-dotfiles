# Parrot Caelestia Dotfiles

A documented Hyprland and Caelestia desktop setup for Parrot Linux, using
Konsole, Zsh, and the distribution's Qt 6.8.2.

The desktop, shell panels, shortcuts, and automatic startup were reported
working on **7 October 2026**. This repository preserves the installation
recipe and the compatibility changes that made the setup work.

## Start here

**On the already configured laptop**, run this from the extracted repository:

```bash
python3 scripts/export-dotfiles.py --include-terminal
```

This creates `snapshot/` with the **actual working dotfiles**, a patch made
from the running QML configuration, installed package versions, source
checkout commits, build settings, and checksums. It reads the existing
configuration and writes into this repository.

The bundled `config/` directory is a reference assembled from the setup
steps. The export captures additional settings you may have changed locally.
The optional terminal flag adds the existing Zsh, Starship, and Konsole
configuration; omit it to export only the desktop.

Then follow [Export and GitHub](docs/EXPORT-AND-GITHUB.md).

**For a fresh installation**, follow [Installation](docs/INSTALL.md) in order.
These are source builds for the recorded Parrot/Qt combination, rather than
an unattended installer for every Linux distribution.

## Recorded environment

| Component | Working setup |
|---|---|
| Distribution | Parrot 7 Echo, amd64 |
| Original login session | KDE Plasma, Wayland |
| Compositor | Hyprland 0.55.2, Lua configuration |
| Graphics | Intel UHD Graphics 620, `i915` |
| Laptop display | `eDP-1`, 1920 × 1080 at 60 Hz, scale 1 |
| External display | `HDMI-A-1`, 1920 × 1080 at 60 Hz, scale 1 |
| Qt | 6.8.2 from Parrot |
| Quickshell | 0.3.1, revision `11ca60be22b063478ed9586ca1d7f92f0f261caf` |
| Caelestia Shell | `v1.1.1`, upstream commit prefix `e405bf8d`, with local QML fixes |
| Terminal / interactive shell | Konsole / Zsh |
| Browser shortcut | Brave, launched directly |
| Fonts | Rubik and Material Symbols Rounded |
| Application icons | Papirus-Dark |

The exact source revisions for the CLI, M3Shapes, and libcava were not included
in the original terminal output. The export script records the existing
checkouts and installed version output instead of guessing those revisions.
See [reference versions](manifests/reference-versions.json).

## Why this Caelestia version?

The checked Caelestia releases from `v1.2.0` through `v2.5.0` declared a Qt
6.9 minimum, while this Parrot installation supplied Qt 6.8.2.
The setup used a separate `v1.1.1` worktree and adapted its QML.

The compatibility changes are:

1. Replace `RectangularShadow` with a Qt 6.8-compatible `MultiEffect` shadow.
2. Import `Qt.labs.qmlmodels` where `DelegateChooser` / `DelegateChoice` are used.
3. Pass the locale to three helper processes through `env`, avoiding the
   observed `QJSValue to QVariantHash` warnings.
4. Use POSIX redirection in the GPU detection command.

See [Compatibility](docs/COMPATIBILITY.md) for the implementation and limits.
The exported patch is generated against upstream `v1.1.1`, so it also captures
any additional QML changes made on the laptop.

## Repository contents

| Path | Purpose |
|---|---|
| `config/hypr/hyprland.lua` | Reference monitor setup, window controls, autostart, and shortcuts |
| `config/caelestia/shell.json` | Reference user settings: Konsole as the terminal |
| `config/caelestia/cli.json` | Reference CLI settings for shell-only initial color setup |
| `overrides/` | Reference Qt 6.8 shadow replacement |
| `scripts/export-dotfiles.py` | Capture the running laptop setup into a new snapshot |
| `scripts/apply-qt68-fixes.py` | Apply the documented compatibility changes to a fresh v1.1.1 tree |
| `scripts/restore-config.py` | Restore the three desktop dotfiles with timestamped backups |
| `scripts/download-fonts.sh` | Install the two fonts confirmed during setup |
| `packages/` | Build and runtime dependency lists |
| `manifests/` | Reference versions and notes about exact reproduction |
| `snapshot/` | Actual laptop export; created by the export script |
| `docs/INSTALL.md` | Full installation and restoration steps |
| `docs/TROUBLESHOOTING.md` | Errors encountered, causes, and the fixes used |
| `docs/BUILD-HISTORY.md` | What was built, what failed, and what remains separate |
| `docs/EXPORT-AND-GITHUB.md` | Export, review, commit, and upload instructions |
| `THIRD_PARTY.md` | Upstream projects, font sources, and attribution |

## Shortcuts

**SUPER** is the Windows key.

| Shortcut | Action |
|---|---|
| SUPER + Enter | Open Konsole |
| SUPER + Q | Close the focused window |
| SUPER + F | Toggle fullscreen |
| SUPER + V | Toggle floating |
| SUPER + Arrow | Focus a window in that direction |
| SUPER + 1–5 | Switch workspace |
| SUPER + Shift + 1–5 | Move the focused window to a workspace |
| SUPER + Left mouse drag | Move a window |
| SUPER + Right mouse drag | Resize a window |
| SUPER + Space | Toggle launcher |
| SUPER + D | Toggle dashboard |
| SUPER + C | Open control center |
| SUPER + Escape | Toggle session menu |
| SUPER + Shift + Space | Toggle multiple shell panels together |
| SUPER + B | Open Brave directly |
| SUPER + Shift + E | Exit the Hyprland session |
| Ctrl + W in Brave | Close the current browser tab |
| Ctrl + Shift + W in Konsole | Close the current terminal tab |

The Brave keybind runs `brave-browser`; it does not change the default browser.

## Wallpaper and colors

Save wallpaper candidates in `~/Pictures/Wallpapers`, then set a real image:

```bash
caelestia wallpaper -f "$HOME/Pictures/Wallpapers/your-image.jpg"
caelestia scheme set -n dynamic
```

The dynamic scheme derives the shell colors from the selected wallpaper.
The initial CLI configuration disables optional theming of other applications.
You can enable integrations individually later.

The dashboard profile image is `~/.face`. A bundled dinosaur was used as a
temporary avatar during setup. Wallpaper images, the profile image, caches,
and generated runtime state are not included automatically in the Git export.

## Autostart

The reference Lua file starts Quickshell from `hyprland.start` using:

```bash
env QS_ICON_THEME=Papirus-Dark PATH="$HOME/.local/bin:$PATH" \
  /usr/local/bin/quickshell \
  -p "$HOME/.config/quickshell/caelestia" -n -d
```

`-n` avoids another instance of this configuration. `-d` detaches from the
terminal. The path selects this Caelestia installation, and the local CLI
directory is available to shell helpers.

The chosen login entry is **Hyprland**. The original **Plasma (Wayland)**
session remains useful as a fallback for editing configuration.

## Verification

```bash
hyprctl configerrors
hyprctl globalshortcuts
/usr/local/bin/quickshell --version
qmake6 -query QT_VERSION
fc-match -f '%{family}\n' 'Rubik'
fc-match -f '%{family}\n' 'Material Symbols Rounded'
```

The configuration error command should print no errors. Test the launcher,
dashboard, control center, terminal, and browser shortcuts. Save your work
and check that the shell starts after logging back into Hyprland.

The working desktop was tested interactively on the laptop. The included
export and restoration helpers were also checked in an isolated file-system
fixture; a fresh operating-system installation was not performed for this
documentation package.

## Scope and updates

This repository documents the desktop setup. ProtonVPN diagnosis was paused
and is recorded separately in the troubleshooting notes; VPN profiles and
credentials are outside the export.

Keep the exported source commits when reproducing this Qt 6.8 installation.
Pulling current upstream Caelestia or replacing Qt can change the build
requirements. Rebuild Quickshell and the QML plugins when changing the Qt
installation they were compiled against.

## License and credits

The reference compatibility code is derived from Caelestia and is distributed
under GNU GPL version 3. See [LICENSE](LICENSE) and
[THIRD_PARTY.md](THIRD_PARTY.md). The export copies Caelestia's upstream
license into the snapshot alongside the QML patch.
