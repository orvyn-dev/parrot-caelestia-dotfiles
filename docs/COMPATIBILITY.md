# Qt 6.8 compatibility changes

Baseline: **Caelestia v1.1.1**, upstream commit prefix `e405bf8d`.
The working runtime uses **Qt 6.8.2** and **Quickshell 0.3.1**.

## 1. Elevation shadow

### Observed failure

```text
Type Elevation unavailable
RectangularShadow is not a type
```

`components/effects/Elevation.qml` used `RectangularShadow`, which Qt
introduced in 6.9.

### Change

The replacement is an `Item` with the same public properties used by the
existing callers: `level`, `dp`, `radius`, `color`, `blur`, `spread`, and
`offset`. A hidden, layered `Rectangle` provides the shadow shape, and
`MultiEffect` blurs it.

The source rectangle is hidden to avoid rendering it directly. It remains
available to the effect through its enabled layer. The existing elevation
level table, color, spread calculation, and animated `dp` are preserved.

The replacement lives at:
`overrides/quickshell/caelestia/components/effects/Elevation.qml`.

This is an approximation of the 6.9 shadow. The blur appearance can differ
slightly, particularly at high elevation or large sizes.

Sources:
[Qt 6.9 additions](https://doc.qt.io/qt-6.9/whatsnew69.html),
[Qt 6.8 MultiEffect](https://doc.qt.io/qt-6.8/qml-qtquick-effects-multieffect.html).

## 2. DelegateChooser import

### Observed failure

```text
modules/bar/Bar.qml: DelegateChooser is not a type
```

### Change

On Qt 6.8, the chooser types are available from the labs module:

```qml
import Qt.labs.qmlmodels
```

The installation needs the Parrot/Debian package:

```bash
sudo apt-get --no-remove install qml6-module-qt-labs-qmlmodels
```

The existing `QtQml.Models` import is retained for other model types.
The setup script added the labs import to QML files using unqualified
`DelegateChooser` or `DelegateChoice`. The reported update was
`modules/bar/Bar.qml`.

Source:
[Qt 6.8 DelegateChooser](https://doc.qt.io/qt-6.8/qml-qt-labs-qmlmodels-delegatechooser.html).

## 3. Locale maps for three processes

### Observed warning

```text
Unable to assign QJSValue to QVariantHash
```

The relevant processes used:

```qml
environment: ({
    LANG: "C.UTF-8",
    LC_ALL: "C.UTF-8"
})
```

### Change

The two Network.qml commands and the SystemUsage.qml sensors command pass
the locale directly to their child process:

```qml
command: ["env", "LANG=C.UTF-8", "LC_ALL=C.UTF-8", "nmcli", "radio", "wifi"]
command: ["env", "LANG=C.UTF-8", "LC_ALL=C.UTF-8", "nmcli", "-g",
          "ACTIVE,SIGNAL,FREQ,SSID,BSSID,SECURITY", "d", "w"]
command: ["env", "LANG=C.UTF-8", "LC_ALL=C.UTF-8", "sensors"]
```

The corresponding environment blocks are removed.
This keeps these parser-oriented helper commands in a predictable locale.
The desktop user's overall locale is not changed.

The change addresses the three observed warnings in this version combination;
it is not a claim that every Quickshell environment map has the same issue.

## 4. POSIX GPU-detection redirection

The GPU detection command runs through `sh -c`. Two occurrences of the
Bash-style `&>/dev/null` were replaced with:

```sh
>/dev/null 2>&1
```

This redirects stdout to /dev/null and stderr to the same destination under
a POSIX shell, including Debian's usual /bin/sh implementation.

## Apply the changes

### Preferred: use the laptop export

On a fresh, unmodified v1.1.1 source tree:

```bash
git -C "$HOME/.local/src/caelestia-shell-v1.1.1" apply --check \
  "$PWD/snapshot/patches/caelestia-qt68.patch"
git -C "$HOME/.local/src/caelestia-shell-v1.1.1" apply \
  "$PWD/snapshot/patches/caelestia-qt68.patch"
```

The repository must be your current working directory when using `$PWD`.
This patch is computed from the actual running files, including additional
edits if present.

### Reference recipe when no snapshot exists

```bash
python3 scripts/apply-qt68-fixes.py \
  "$HOME/.local/src/caelestia-shell-v1.1.1" --check
python3 scripts/apply-qt68-fixes.py \
  "$HOME/.local/src/caelestia-shell-v1.1.1"
```

The helper checks that HEAD equals the v1.1.1 tag, validates the expected
locale blocks before writing, and creates backups of changed source files.
Run it before building and installing the shell. It edits the source
worktree rather than the live desktop.

The compatibility changes are QML edits. After installing those files,
Quickshell can reload them without recompiling its own binary.

## Supported boundary

These fixes were used with the recorded v1.1.1/Qt 6.8.2 setup. They do not
make current Caelestia releases compatible with Qt 6.8 and do not justify
lowering a newer release's CMake minimum.
