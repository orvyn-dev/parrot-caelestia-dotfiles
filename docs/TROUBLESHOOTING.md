# Troubleshooting from this setup

Use the [installation guide](INSTALL.md) for the ordered recipe. These notes
explain the failures that actually appeared during setup.

## APT selects a development package that would downgrade its runtime

Examples included:

```text
libgbm-dev depends on libgbm1 = 25.0.7, but 26.1.6 is selected
libpipewire-0.3-dev depends on 1.4.2, but 1.6.9 is installed
libxkbcommon-dev depends on 1.7.0, but 1.13.1 is installed
```

The development packages' exact dependencies conflicted with newer installed
backports libraries. Main had a slightly higher APT priority than backports.

Use the corresponding backports development package selectors and simulate
the transaction before installing. The curl issue later needed the same
treatment for `libcurl4-gnutls-dev` and matching HTTP/QUIC development packages.
See [the package steps](INSTALL.md#3-install-development-packages-with-matching-backports).

APT's general “held broken packages” message is not, by itself, proof that a
package was manually held. Inspect holds separately if needed:

```bash
apt-mark showhold
apt-cache policy libgbm1 libgbm-dev libpipewire-0.3-dev libcurl4-gnutls-dev
```

## CMake cannot find polkit-agent-1

```text
Package 'polkit-agent-1', required by 'virtual:world', not found
```

The GObject development package did not supply the agent development files:

```bash
sudo apt-get --no-remove install libpolkit-agent-1-dev
pkg-config --modversion polkit-agent-1
```

Rerun the same CMake configuration command after installing the dependency.
The recorded build also needed `libegl-dev` for EGL development files.

## Ninja cannot find ext-background-effect-v1.xml

```text
/usr/share/wayland-protocols/staging/ext-background-effect/ext-background-effect-v1.xml
missing and no known rule to make it
```

The installed protocol package was 1.44. The recorded fix upgraded it to
backports 1.47:

```bash
apt-get -s --no-remove install wayland-protocols/echo-backports
sudo apt-get --no-remove install wayland-protocols/echo-backports
test -f /usr/share/wayland-protocols/staging/ext-background-effect/ext-background-effect-v1.xml
```

Then rerun the Quickshell CMake command and build. Ninja needs that XML to
generate the protocol headers; reinstalling an unrelated QML module does
not supply it.

## Caelestia requires Qt 6.9 but Parrot has 6.8.2

```text
Project required a Qt minimum version of 6.9,
but current version is only 6.8.2.
```

The releases checked from v1.2.0 through v2.5.0 declared that minimum.
The working solution was a v1.1.1 worktree plus the QML compatibility changes.
See [Compatibility](COMPATIBILITY.md).

Changing the minimum in a newer release's CMake file does not provide
the missing Qt APIs. This repository preserves the older working version.

## RectangularShadow or DelegateChooser is not a type

Apply the exported patch to a fresh v1.1.1 source tree, or run the reference
compatibility helper before installation. Also install:

```bash
sudo apt-get --no-remove install qml6-module-qt-labs-qmlmodels
```

The shadow needs the replacement component. DelegateChooser needs the
`Qt.labs.qmlmodels` import on Qt 6.8. Installing only the labs package
does not add an import to existing QML files.

## The bar displays words such as calendar_month instead of icons

The icon text must be rendered with Material Symbols Rounded:

```bash
bash scripts/download-fonts.sh
fc-match -f '%{family}\n' 'Material Symbols Rounded'
fc-match -f '%{family}\n' 'Rubik'
```

Restart the shell so it sees the installed fonts. Fontconfig should resolve
the requested families, rather than an unrelated fallback.

## The dashboard repeatedly warns that ~/.face is missing

`~/.face` is the user avatar image. Use your own image or the temporary
bundled dinosaur:

```bash
if [ ! -e "$HOME/.face" ] && [ ! -L "$HOME/.face" ]; then
  cp -- "$HOME/.config/quickshell/caelestia/assets/dino.png" "$HOME/.face"
fi
```

The guard keeps an existing image or symlink.

## Wallpaper missing, path.txt missing, or scheme.json missing

These appeared before the wallpaper and color scheme were initialized.
Select a real wallpaper with KDialog or supply its actual path:

```bash
caelestia wallpaper -f "$HOME/Pictures/Wallpapers/your-image.jpg"
caelestia scheme set -n dynamic
```

Replace `your-image.jpg` with a file that exists. The CLI generates the
wallpaper and scheme state. A manually created empty JSON file does not
provide a valid color palette.

If the command is missing, check `~/.local/bin/caelestia` and PATH.
The Hyprland startup command includes that directory for shell helpers.

## Unable to assign QJSValue to QVariantHash

Three warnings pointed to Network.qml and SystemUsage.qml locale maps.
The fix removes those maps and prefixes the commands with
`env LANG=C.UTF-8 LC_ALL=C.UTF-8`. The reference helper and exported
patch capture this change. See [the locale adaptation](COMPATIBILITY.md#3-locale-maps-for-three-processes).

## Application icons are missing

Install Papirus and launch Quickshell with its theme selected:

```bash
sudo apt-get --no-remove install papirus-icon-theme
env QS_ICON_THEME=Papirus-Dark PATH="$HOME/.local/bin:$PATH" \
  /usr/local/bin/quickshell -p "$HOME/.config/quickshell/caelestia" -n -d
```

Some applications may still have missing or broken icon references.
The environment setting applies when the shell process starts.

## Opening Brave leaves the terminal busy

A program started in the foreground can keep the terminal occupied.
For a launch that detaches its output and survives closing the terminal:

```bash
nohup brave-browser https://chatgpt.com >/dev/null 2>&1 &
```

The Lua **SUPER + B** shortcut launches Brave from Hyprland, so it does
not occupy a Konsole tab. Browser launch and browser default selection
are independent.

The observed `puffpatch` temporary-file warnings alone did not establish
that Brave failed to open. Avoid changing browser security flags solely
to hide those messages.

## Closing an already opened tab or window

| Action | Shortcut |
|---|---|
| Close the current Brave tab | Ctrl + W |
| Close a Konsole tab | Ctrl + Shift + W |
| Close the focused application window | SUPER + Q |
| Exit a foreground command | Ctrl + C |

Closing the Konsole window running a foreground Quickshell process can
stop that process. Use the detached startup command for normal desktop use.

## Hyprland reload is clean but the shell did not start

`hyprctl reload` reloads the configuration. The Lua startup handler listens
for `hyprland.start`, so test it by starting a new Hyprland session.
For an immediate launch use the detached command above.

Check the paths and exported settings:

```bash
hyprctl configerrors
hyprctl globalshortcuts
command -v konsole brave-browser
test -x /usr/local/bin/quickshell
test -f "$HOME/.config/quickshell/caelestia/shell.qml"
```

The global shortcut registrations appear only while the shell is running.
`caelestia:launcher` and similar names come from its `GlobalShortcut`
objects, whose app ID is `caelestia`.

## grep -Ei reports an rg encoding error

The original shell mapped `grep` to `rg`. GNU grep's `-E` option and
ripgrep's `-E` option mean different things.
Use ripgrep's own syntax:

```bash
lspci -nnk | rg -i -A 3 'VGA|3D|Display'
```

No extra extended-regex flag is needed for that expression.

## ProtonVPN: diagnosis paused

The VPN issue was explicitly deferred while completing the shell.
The desktop documentation does not resolve or configure the VPN.

Two distinct problems were observed:

1. A Proton IPv6 helper connection selected `::1` as DNS. IPv4 ping worked,
   but DNS lookups failed. Disconnecting that helper and refreshing
   NetworkManager DNS restored ordinary browsing.
2. The VPN app and CLI timed out while awaiting the asynchronous creation
   of an IPv6 leak-protection connection. NetworkManager reported a
   successful connection-add operation, while the Python caller timed out.
   Repeated attempts created duplicate helper profiles.

The CLI's generic “Network connectivity issues detected” message masked
that second timeout. Successful HTTPS tests to example.com and protonvpn.com
showed ordinary connectivity at the time; they did not prove a working VPN.

An Eventlet/Trio `GreenSocket.sendmsg` import error was bypassed for diagnosis
using the per-command variable `EVENTLET_NO_GREENDNS=yes`. The later
initialization timeout remained.

Disconnecting or deleting leak-protection helpers can reduce their
protection and is not a VPN repair. No such cleanup is automated in this
repository. VPN credentials, profiles, and raw diagnostic logs are excluded
from the export. Resume that separate investigation when desired.
