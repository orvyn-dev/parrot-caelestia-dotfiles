# Install or reproduce the desktop

This is the documented recipe for **Parrot 7 Echo, Qt 6.8.2, Hyprland 0.55.2,
Quickshell 0.3.1, and Caelestia v1.1.1 with local fixes**.

If the desktop already works, start with
[the export guide](EXPORT-AND-GITHUB.md). You do not need to reinstall it
to create the GitHub repository.

Run the commands below in Konsole as your normal user. Commands explicitly
prefixed with `sudo` install system packages or compiled components.
The commands work in Bash or Zsh; installing Fish for shell helpers does
not select it as your login shell.

## 1. Open the dotfiles repository

Extract or clone this repository, open its directory in Konsole, then record
its absolute path:

```bash
caelestia_repo="$PWD"
mkdir -p "$HOME/.local/src"
```

The repository contains the documentation and configuration. Dependency
source trees go in `~/.local/src`, outside the dotfiles repository.

For an exported repository, inspect the recorded commits:

```bash
python3 -m json.tool "$caelestia_repo/snapshot/manifest.json"
```

Skip that command if no laptop snapshot exists yet.

## 2. Check the environment and package sources

```bash
printf 'Desktop: %s\nSession: %s\n' "$XDG_CURRENT_DESKTOP" "$XDG_SESSION_TYPE"
lspci -nnk | rg -i -A 3 'VGA|3D|Display'
apt-cache policy hyprland quickshell qt6-base-dev wayland-protocols
```

The original desktop was KDE on Wayland. Intel UHD 620 used the `i915`
kernel driver. These checks identify your current session, graphics driver,
and the versions available from the configured Parrot repositories.

The recorded installation already had **echo-backports** enabled. The
`/echo-backports` selectors below assume that repository exists. Keep Qt
development packages and runtime modules on the matching Parrot Qt series.

```bash
sudo apt-get update
apt-get -s --no-remove install \
  hyprland/echo-backports xdg-desktop-portal-hyprland
```

`-s` simulates the transaction. `--no-remove` stops a transaction that
would remove packages. Read the simulated result, then perform the same
installation:

```bash
sudo apt-get --no-remove install \
  hyprland/echo-backports xdg-desktop-portal-hyprland
Hyprland --version
dpkg -L hyprland | rg '/wayland-sessions/.*\.desktop$'
```

The working package was `0.55.2+ds-1~bpo13+1`. The commands select the
backports candidate available **when you run them**, so compare the version
with the manifest before treating a newer package as the same setup.

The portal connects Wayland applications to desktop facilities such as
screen sharing. KDE can remain installed alongside Hyprland.

## 3. Install development packages with matching backports

Parrot's main repository had priority 600 and backports priority 599 during
setup. Several newer runtime libraries were already installed from
backports, but APT selected older development packages by default.
Development packages with exact runtime dependencies must match them.

First simulate:

```bash
apt-get -s --no-remove install \
  build-essential git cmake ninja-build pkg-config \
  qt6-base-dev qt6-base-private-dev \
  qt6-declarative-dev qt6-declarative-private-dev \
  qt6-shadertools-dev qt6-wayland-dev qt6-wayland-private-dev \
  qt6-svg-dev qt6-image-formats-plugins \
  libcli11-dev libdrm-dev libegl-dev \
  libgbm-dev/echo-backports \
  libpipewire-0.3-dev/echo-backports \
  libspa-0.2-dev/echo-backports \
  libxkbcommon-dev/echo-backports \
  libvulkan-dev libwayland-dev wayland-protocols/echo-backports spirv-tools \
  libpam0g-dev libpolkit-gobject-1-dev libpolkit-agent-1-dev \
  libjemalloc-dev libunwind-dev libdwarf-dev
```

When dependency resolution succeeds, install:

```bash
sudo apt-get --no-remove install \
  build-essential git cmake ninja-build pkg-config \
  qt6-base-dev qt6-base-private-dev \
  qt6-declarative-dev qt6-declarative-private-dev \
  qt6-shadertools-dev qt6-wayland-dev qt6-wayland-private-dev \
  qt6-svg-dev qt6-image-formats-plugins \
  libcli11-dev libdrm-dev libegl-dev \
  libgbm-dev/echo-backports \
  libpipewire-0.3-dev/echo-backports \
  libspa-0.2-dev/echo-backports \
  libxkbcommon-dev/echo-backports \
  libvulkan-dev libwayland-dev wayland-protocols/echo-backports spirv-tools \
  libpam0g-dev libpolkit-gobject-1-dev libpolkit-agent-1-dev \
  libjemalloc-dev libunwind-dev libdwarf-dev
```

| Package group | Purpose |
|---|---|
| Compiler, Git, CMake, Ninja, pkg-config | Download, configure, and compile source |
| Qt development and private headers | Compile Quickshell and native QML plugins against the installed Qt |
| Wayland, protocols, DRM, GBM, EGL, Vulkan | Display integration and graphics interfaces |
| PipeWire / SPA | Audio integration |
| PAM and Polkit agent development files | Authentication and authorization interfaces |
| jemalloc, unwind, dwarf | Allocator and crash reporting dependencies |

The recorded versions included GBM 26.1.6, PipeWire 1.6.9, xkbcommon 1.13.1,
and Wayland protocols 1.47. Qt remained 6.8.2.

Check the two dependencies that caused specific build failures:

```bash
pkg-config --modversion polkit-agent-1
test -f /usr/share/wayland-protocols/staging/ext-background-effect/ext-background-effect-v1.xml
```

`test` succeeds silently when the protocol XML exists.

## 4. Install shell helpers and QML runtime modules

The calculator development package pulled in curl development headers.
Their backports versions were needed to match the installed curl library.
Use the same simulated-then-real process:

```bash
apt-get -s --no-remove install \
  meson pipx python3-venv python3-dev \
  libfftw3-dev libiniparser-dev libaubio-dev libqalculate-dev libsensors-dev \
  libcurl4-gnutls-dev/echo-backports \
  libnghttp3-dev/echo-backports \
  libngtcp2-dev/echo-backports libngtcp2-crypto-gnutls-dev/echo-backports \
  ddcutil brightnessctl lm-sensors power-profiles-daemon \
  swappy fish grim slurp wl-clipboard cliphist fuzzel libnotify-bin \
  cava qalc pavucontrol papirus-icon-theme kdialog \
  konsole network-manager fontconfig curl unzip \
  qml6-module-qtqml qml6-module-qtqml-models qml6-module-qtqml-workerscript \
  qml6-module-qtquick qml6-module-qtquick-controls qml6-module-qtquick-layouts \
  qml6-module-qtquick-window qml6-module-qtquick-shapes \
  qml6-module-qtquick-effects qml6-module-qtquick-dialogs \
  qml6-module-qt-labs-qmlmodels
```

```bash
sudo apt-get --no-remove install \
  meson pipx python3-venv python3-dev \
  libfftw3-dev libiniparser-dev libaubio-dev libqalculate-dev libsensors-dev \
  libcurl4-gnutls-dev/echo-backports \
  libnghttp3-dev/echo-backports \
  libngtcp2-dev/echo-backports libngtcp2-crypto-gnutls-dev/echo-backports \
  ddcutil brightnessctl lm-sensors power-profiles-daemon \
  swappy fish grim slurp wl-clipboard cliphist fuzzel libnotify-bin \
  cava qalc pavucontrol papirus-icon-theme kdialog \
  konsole network-manager fontconfig curl unzip \
  qml6-module-qtqml qml6-module-qtqml-models qml6-module-qtqml-workerscript \
  qml6-module-qtquick qml6-module-qtquick-controls qml6-module-qtquick-layouts \
  qml6-module-qtquick-window qml6-module-qtquick-shapes \
  qml6-module-qtquick-effects qml6-module-qtquick-dialogs \
  qml6-module-qt-labs-qmlmodels
```

| Helper | Role |
|---|---|
| `brightnessctl`, `ddcutil` | Laptop backlight and supported external-monitor brightness |
| `lm-sensors`, `power-profiles-daemon` | Hardware readings and power profiles |
| `grim`, `slurp`, `swappy` | Screenshot capture, selection, and editing |
| `wl-clipboard`, `cliphist`, `fuzzel` | Clipboard operations, history, and picker |
| `qalc`, `cava`, `pavucontrol` | Calculator, audio visualizer helper, and audio controls |
| Papirus and KDialog | Application icons and a wallpaper file picker |
| QML module packages | Runtime imports used by the shell |

The lists in `packages/` also serve as input to the export script. They
are package names, not a command to install all candidates indiscriminately;
the selectors above capture the dependency choices used in this setup.

## 5. Restore exported dependency revisions

Quickshell has a confirmed revision below. M3Shapes, libcava, and the CLI
need their **exported** checkout commits for a closer reproduction.
Define this helper once, in the same Konsole session:

```bash
checkout_exported_revision() {
  caelestia_project="$1"
  caelestia_checkout="$2"
  if [ ! -f "$caelestia_repo/snapshot/manifest.json" ]; then
    printf 'No snapshot: %s remains at the cloned revision.\n' "$caelestia_project"
    return 0
  fi
  caelestia_revision="$(python3 - "$caelestia_repo/snapshot/manifest.json" "$caelestia_project" <<'PY'
import json
import sys
with open(sys.argv[1]) as source:
    manifest = json.load(source)
print(manifest.get("sources", {}).get(sys.argv[2], {}).get("checkout_commit") or "")
PY
  )" || return 1
  if [ -n "$caelestia_revision" ]; then
    git -C "$caelestia_checkout" checkout --detach "$caelestia_revision"
  else
    printf 'No recorded checkout commit for %s; check the manifest notes.\n' "$caelestia_project"
  fi
}
```

The helper reads the snapshot, then selects its commit in a fresh dependency
clone. It does not guess missing commits. Without an export, the three
unrecorded dependencies will be current clones, which can differ from the
working laptop.

## 6. Build Quickshell

On a fresh machine:

```bash
git clone https://github.com/quickshell-mirror/quickshell.git \
  "$HOME/.local/src/quickshell"
git -C "$HOME/.local/src/quickshell" checkout --detach \
  11ca60be22b063478ed9586ca1d7f92f0f261caf

cmake -S "$HOME/.local/src/quickshell" \
  -B "$HOME/.local/src/quickshell/build" \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DDISTRIBUTOR="Local build on Parrot" \
  -DVENDOR_CPPTRACE=ON \
  -DX11=OFF

cmake --build "$HOME/.local/src/quickshell/build" --parallel 2
sudo cmake --install "$HOME/.local/src/quickshell/build"
```

`-S` selects the source directory; `-B` selects its separate build directory.
Ninja runs the compile steps. `--parallel 2` limits concurrent jobs, as used
on the laptop. `RelWithDebInfo` retains debugging information. X11 support
was disabled for this Wayland setup.

The local installation goes into `/usr/local`. The recorded vendored crash
reporting build also installed cpptrace, libdwarf, and zstd static libraries,
headers, and build metadata there. See [Build history](BUILD-HISTORY.md).

Check the installed binary:

```bash
command -v quickshell qs
/usr/local/bin/quickshell --version
```

Expected recorded result: **Quickshell 0.3.1**, revision
`11ca60be22b063478ed9586ca1d7f92f0f261caf`.

## 7. Build M3Shapes

This dependency was built during the setup and is included in the build
record. Select its exported commit after cloning:

```bash
git clone https://github.com/soramanew/m3shapes.git \
  "$HOME/.local/src/m3shapes"
checkout_exported_revision m3shapes "$HOME/.local/src/m3shapes"

cmake -S "$HOME/.local/src/m3shapes" \
  -B "$HOME/.local/src/m3shapes/build" \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/ \
  -DCMAKE_INSTALL_LIBDIR=usr/local/lib \
  -DCMAKE_INSTALL_INCLUDEDIR=usr/local/include \
  -DINSTALL_QMLDIR="$(qmake6 -query QT_INSTALL_QML)"

cmake --build "$HOME/.local/src/m3shapes/build" --parallel 2
sudo cmake --install "$HOME/.local/src/m3shapes/build"
sudo ldconfig
```

The library is installed under `/usr/local/lib`; its QML plugin goes in Qt's
actual QML directory. `qmake6 -query` finds the distribution-specific path,
which on the recorded machine was `/usr/lib/x86_64-linux-gnu/qt6/qml`.
`ldconfig` refreshes the system's shared-library cache.

## 8. Build the libcava fork

The C++ audio visualizer dependency uses a fork that exposes a shared
library. The ordinary `cava` executable and this library are separate.

```bash
git clone https://github.com/LukashonakV/cava.git \
  "$HOME/.local/src/libcava"
checkout_exported_revision libcava "$HOME/.local/src/libcava"

meson setup \
  "$HOME/.local/src/libcava/build" \
  "$HOME/.local/src/libcava" \
  --prefix=/usr/local \
  --libdir=lib \
  --buildtype=release \
  --auto-features=disabled \
  -Dbuild_target=lib \
  -Dinput_pipewire=enabled \
  -Dcava_font=false

meson compile -C "$HOME/.local/src/libcava/build" -j 2
sudo meson install -C "$HOME/.local/src/libcava/build" --no-rebuild
sudo ldconfig
pkg-config --modversion libcava
```

Meson configures this project instead of CMake. The options build its library
target and enable PipeWire input. Optional backends are disabled, so warnings
that ALSA, PulseAudio, SDL, or JACK are unavailable were expected in this build.
The installed pkg-config version was **1.0.0**.

M3Shapes and libcava were prepared before selecting the older Caelestia
release. The v1.1.1 plugin's CMake file only directly links Qt Core, QML, Gui,
and Concurrent. These two builds document the completed setup; they are not
evidence that this older native plugin links the newer release's dependencies.

## 9. Install the Caelestia CLI in a user environment

```bash
git clone https://github.com/caelestia-dots/cli.git \
  "$HOME/.local/src/caelestia-cli"
checkout_exported_revision caelestia-cli "$HOME/.local/src/caelestia-cli"
pipx install "$HOME/.local/src/caelestia-cli"
"$HOME/.local/bin/caelestia" --help
```

`pipx` gives the Python CLI its own virtual environment and exposes the
`caelestia` command in `~/.local/bin`. The current upstream Python project
requires Python 3.13 or newer, supplied by this Parrot installation.
Use the exported commit to preserve the laptop's CLI version.

If `caelestia` is not already on the terminal's PATH, these commands make it
available for this session:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v caelestia
caelestia scheme --help
caelestia wallpaper --help
```

The Hyprland startup command also supplies this PATH prefix. The setup
preserves the existing Zsh configuration and the browser's default selection.

Source: [Caelestia CLI](https://github.com/caelestia-dots/cli) and
[Python project metadata](https://github.com/caelestia-dots/cli/blob/main/pyproject.toml).

## 10. Select Caelestia v1.1.1 in a separate worktree

```bash
git clone https://github.com/caelestia-dots/shell.git \
  "$HOME/.local/src/caelestia-shell"
git -C "$HOME/.local/src/caelestia-shell" worktree add --detach \
  "$HOME/.local/src/caelestia-shell-v1.1.1" v1.1.1
```

A worktree creates another checkout sharing Git's objects with the main
clone. Detached HEAD keeps this directory at the selected release.
The recorded commit begins with `e405bf8d`.

The checked newer releases required Qt 6.9. Keeping the v1.1.1 worktree
separate avoids mixing their files with the Qt 6.8 setup.

## 11. Apply the Qt 6.8 QML changes

**When a laptop snapshot exists**, apply its actual runtime patch:

```bash
if [ -s "$caelestia_repo/snapshot/patches/caelestia-qt68.patch" ]; then
  git -C "$HOME/.local/src/caelestia-shell-v1.1.1" apply --check \
    "$caelestia_repo/snapshot/patches/caelestia-qt68.patch" &&
  git -C "$HOME/.local/src/caelestia-shell-v1.1.1" apply \
    "$caelestia_repo/snapshot/patches/caelestia-qt68.patch"
fi
```

`--check` checks that the patch applies to this fresh tree before making
changes. An empty exported patch means no QML differences were captured.

**When no snapshot exists**, use the reference compatibility helper instead:

```bash
python3 "$caelestia_repo/scripts/apply-qt68-fixes.py" \
  "$HOME/.local/src/caelestia-shell-v1.1.1" --check
python3 "$caelestia_repo/scripts/apply-qt68-fixes.py" \
  "$HOME/.local/src/caelestia-shell-v1.1.1"
```

Use one route. The helper replaces the shadow component, adds the labs
model import, adapts the three locale commands, and fixes shell redirection.
It saves source-file backups before writing. These changes are explained in
[Compatibility](COMPATIBILITY.md).

## 12. Build and install the older shell

```bash
mkdir -p "$HOME/.config/quickshell/caelestia"

cmake -S "$HOME/.local/src/caelestia-shell-v1.1.1" \
  -B "$HOME/.local/src/caelestia-shell-v1.1.1/build" \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/ \
  -DCMAKE_INSTALL_RPATH='$ORIGIN' \
  -DDISTRIBUTOR="Local build on Parrot" \
  -DINSTALL_QMLDIR="$(qmake6 -query QT_INSTALL_QML)" \
  -DINSTALL_QSCONFDIR="$HOME/.config/quickshell/caelestia"

cmake --build "$HOME/.local/src/caelestia-shell-v1.1.1/build" --parallel 2
sudo cmake --install "$HOME/.local/src/caelestia-shell-v1.1.1/build"
sudo chown -R "$(id -u):$(id -g)" "$HOME/.config/quickshell/caelestia"
```

The build compiles Caelestia's native plugin and helper binaries. The
installation places the native QML module in Qt's QML directory, helpers
under `/usr/lib/caelestia`, and the shell's QML files in your user directory.

The quoted `'$ORIGIN'` stays literal for the dynamic loader and lets the
plugin resolve colocated libraries. The final ownership command makes the
installed user configuration editable after the privileged installation.

## 13. Install fonts

```bash
bash "$caelestia_repo/scripts/download-fonts.sh"
fc-match -f '%{family}\n' 'Rubik'
fc-match -f '%{family}\n' 'Material Symbols Rounded'
```

The script installs Rubik and Material Symbols Rounded under
`~/.local/share/fonts/caelestia`, then refreshes the font cache.
Rubik provides text, and Material Symbols Rounded renders the icon names
as glyphs.

The old shell also names `CaskaydiaCove NF` for monospace text. Its exact
font resolution was not recorded in the original output. The snapshot
records what `fc-match` finds. If desired, install the corresponding
CascadiaCode Nerd Font from
[Nerd Fonts](https://github.com/ryanoasis/nerd-fonts/releases) and refresh
the font cache.

Font download links follow upstream branches, so the export also records
the installed font checksums. Preserve the original font files separately
if exact font bytes are needed.

## 14. Restore the desktop dotfiles

With a laptop snapshot:

```bash
python3 "$caelestia_repo/scripts/restore-config.py" --check
python3 "$caelestia_repo/scripts/restore-config.py"
```

Without a snapshot:

```bash
python3 "$caelestia_repo/scripts/restore-config.py" --reference --check
python3 "$caelestia_repo/scripts/restore-config.py" --reference
```

Run one pair. The helper copies the Lua file and the two Caelestia JSON
settings. Existing differing files or symlinks are backed up under
`~/.local/share/parrot-caelestia/backups/<timestamp>`. `--check` only reports
what would change.

The reference sets Konsole as the terminal and initially disables optional
CLI theming integrations. Its Brave shortcut launches `brave-browser`
directly. Brave itself was already installed on the working machine; its
installation and the default-browser preference are independent.

Optional terminal exports are preserved in `snapshot/terminal/`; the helper
does not automatically restore them. Review those files and copy the ones
you want to their corresponding home paths:

| Exported location | Destination |
|---|---|
| `terminal/home/.zshrc`, `.zshenv` | `~/.zshrc`, `~/.zshenv` |
| `terminal/config/zsh/` | `~/.config/zsh/` |
| `terminal/config/starship.toml` | `~/.config/starship.toml` |
| `terminal/config/konsolerc` | `~/.config/konsolerc` |
| `terminal/local-share/konsole/` | `~/.local/share/konsole/` |

Those settings can refer to plugins, commands, themes, or fonts installed
separately. Their export is a configuration backup, not a full Zsh plugin
manager installation.

## 15. Enter Hyprland and test the shell

Save your work, log out, and choose **Hyprland** in the desktop-session
selector. The old session was **Plasma (Wayland)** and can still be used
to edit settings if needed.

The Lua autostart launches the shell in the Hyprland session. If you want
to inspect a startup failure, run it in the foreground after closing the
existing shell instance:

```bash
env QS_ICON_THEME=Papirus-Dark PATH="$HOME/.local/bin:$PATH" \
  /usr/local/bin/quickshell -p "$HOME/.config/quickshell/caelestia"
```

The foreground form holds the terminal while it runs. Ctrl+C stops that
foreground shell process. For a detached launch:

```bash
env QS_ICON_THEME=Papirus-Dark PATH="$HOME/.local/bin:$PATH" \
  /usr/local/bin/quickshell -p "$HOME/.config/quickshell/caelestia" -n -d
```

`-n` prevents an extra instance of this configuration; `-d` detaches.
Use `quickshell --help` and `quickshell kill --help` to inspect the
installed version's instance controls.

## 16. Set wallpaper, colors, and avatar

Use a real image file:

```bash
mkdir -p "$HOME/Pictures/Wallpapers"
caelestia_wallpaper="$(kdialog --getopenfilename "$HOME/Pictures" \
  "*.png *.jpg *.jpeg *.webp|Wallpaper images")"
if [ -n "$caelestia_wallpaper" ] && [ -f "$caelestia_wallpaper" ]; then
  caelestia wallpaper -f "$caelestia_wallpaper" &&
  caelestia scheme set -n dynamic
fi
```

KDialog lets you select an existing wallpaper. The CLI records the wallpaper
and generates the dynamic shell colors. Canceling the picker leaves the
selection alone. No generated state files need to be copied manually.

For the temporary bundled avatar, only when no `~/.face` exists:

```bash
if [ ! -e "$HOME/.face" ] && [ ! -L "$HOME/.face" ]; then
  cp -- "$HOME/.config/quickshell/caelestia/assets/dino.png" "$HOME/.face"
fi
```

Replace that file with your preferred profile image later.

## 17. Verify the finished desktop

```bash
hyprctl reload
hyprctl configerrors
hyprctl monitors
hyprctl globalshortcuts
qmake6 -query QT_VERSION
/usr/local/bin/quickshell --version
command -v konsole brave-browser caelestia
```

`configerrors` should print no errors. The monitor report should show the
connected outputs and the intended scale. On the recorded laptop the
external screen was positioned to the right.

Test **SUPER + Space**, **D**, **C**, **Escape**, **Enter**, and **B**.
Save your work, log out and back into Hyprland, and verify automatic startup.
See the [shortcut table](../README.md#shortcuts).

Reloading the Lua configuration checks its syntax and updates binds.
The `hyprland.start` event runs when the session starts; a reload is not a
substitute for testing startup after a new login.

After verification, [export the working configuration](EXPORT-AND-GITHUB.md)
and commit it. Keep source build directories outside this repository.
