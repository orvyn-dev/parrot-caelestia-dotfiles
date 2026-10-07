# Build history and known versions

This record is based on the setup's terminal output and the user's
interactive confirmation. The working desktop was reported on
**7 October 2026, Asia/Kolkata**.

## Completed components

| Component | Recorded result |
|---|---|
| Hyprland | Backports package 0.55.2; commit `39d7e209c79d451efab1b21151d5938289da838d` |
| Quickshell | 0.3.1; revision `11ca60be22b063478ed9586ca1d7f92f0f261caf`; local source build |
| M3Shapes | Native library and QML module built and installed; source commit not supplied |
| libcava fork | Shared library build; pkg-config reports 1.0.0; source commit not supplied |
| Caelestia Shell | v1.1.1 at upstream commit prefix `e405bf8d`; native plugin built; QML adapted for Qt 6.8 |
| Caelestia CLI | User command at `~/.local/bin/caelestia`; original exact installed version not supplied |
| Fonts | Rubik and Material Symbols Rounded confirmed with fontconfig |
| Shell behavior | Bar, dashboard, icons, shortcuts, and startup reported working |

The checkout commit and installed binary revision are different observations.
A checkout may have moved since a binary was installed. The export captures
both when available and records tracked source changes.

## Package selections that mattered

| Package | Recorded working version |
|---|---|
| Qt base development | `6.8.2+dfsg-9+deb13u2` |
| Qt declarative development | `6.8.2+dfsg-7` |
| Qt Wayland | `6.8.2-4` |
| Qt ShaderTools / SVG | `6.8.2-3` |
| GBM development | `26.1.6-1~bpo13+1` |
| PipeWire development | `1.6.9-2~bpo13+1` |
| xkbcommon development | `1.13.1-1~bpo13+1` |
| Wayland protocols | `1.47-1~bpo13+1` |
| curl GnuTLS development | `8.21.0-2~bpo13+1` |
| Qalculate development | `5.5.2-1+b1` |
| Aubio | `0.4.9` |
| Polkit | `126` |
| Compiler | GCC 14.2.0 |
| CMake / Ninja / Meson | 3.31.6 / 1.12.1 / 1.7.0 |

The snapshot's `packages.tsv` is the authoritative observation of what
is installed when exported. These historical versions explain the fixes;
they do not guarantee that a repository will retain every package version.

## Installation sequence

1. Installed Hyprland from echo-backports and retained Plasma.
2. Created a basic Lua configuration with Konsole and essential window binds.
3. Entered the Hyprland login session; checked displays and configuration.
4. Resolved temporary DNS blocking caused by a ProtonVPN helper connection.
   VPN client repair was then paused.
5. Installed development packages, selecting matching backports where needed.
6. Built Quickshell with local crash reporting dependencies and Wayland support.
7. Built M3Shapes and the PipeWire-only libcava shared library.
8. Tried the then-current Caelestia Shell and encountered its Qt 6.9 minimum.
9. Created a separate v1.1.1 worktree and built its older native plugin.
10. Replaced the unsupported shadow and added the labs model import.
11. Installed the two fonts and adapted locale maps and shell redirection.
12. Set terminal preferences, icons, wallpaper/color controls, and an avatar.
13. Added Lua autostart and shell/global shortcuts.
14. Confirmed the desktop working and prepared this documentation.

## Build output and installed locations

| Build | Completion observed | Installed outputs |
|---|---|---|
| Quickshell | 1426/1426 Ninja steps | `/usr/local/bin/quickshell`, `qs`, launcher/icon, and vendored crash reporting development files |
| M3Shapes | 28/28 Ninja steps | `/usr/local/lib/libm3shapes.so`, Qt `M3Shapes` module, headers, CMake metadata |
| libcava | 11/11 Ninja steps | `/usr/local/lib/libcava.so.1.0.0`, shared-library symlinks, headers, pkg-config file |
| Caelestia v1.1.1 | 20/20 Ninja steps | Qt `Caelestia` module, `/usr/lib/caelestia` helpers, and user QML configuration |

The Quickshell install log also listed `libzstd.a`, `libdwarf.a`, and
`libcpptrace.a`, together with their headers and CMake/pkg-config metadata
under `/usr/local`. That was a consequence of the vendored crash reporting
build and is part of this installation record.

Quickshell emitted the configuration warning that neither `INSTALL_QMLDIR`
nor `INSTALL_QML_PREFIX` was set. Its own QML modules were not installed as
separate tooling modules in that build. The installed Quickshell binary
nevertheless loaded the runtime shell after the compatibility changes.

## Failed approaches and their resolution

| Failure | Resolution used |
|---|---|
| Main-repository development packages mismatched installed backports runtimes | Select the matching development packages explicitly from echo-backports |
| Missing `polkit-agent-1` | Install `libpolkit-agent-1-dev` |
| Missing EGL development files | Install `libegl-dev` |
| Missing background-effect protocol XML with protocols 1.44 | Upgrade Wayland protocols to 1.47 from echo-backports |
| Current Caelestia CMake requires Qt 6.9 | Use the separate v1.1.1 source worktree |
| v1.1.1 QML still contains Qt 6.9 shadow type | Replace Elevation with a MultiEffect implementation |
| `DelegateChooser is not a type` | Install and import `Qt.labs.qmlmodels` |
| Literal icon names, missing font glyphs | Install Material Symbols Rounded and refresh font cache |
| Three `QJSValue to QVariantHash` warnings | Pass helper locale through `env` |

## What was not established

- The full original source commits for M3Shapes, libcava, and the CLI were
  not present in the supplied version output. Export the existing checkouts.
- The exact original monospace font file was not established by the
  supplied fontconfig output.
- Screen recording, every PAM/lock path, all hardware controls, and every
  optional application integration were not individually tested in the record.
- A clean Parrot reinstall was not performed to validate this written guide.
- ProtonVPN's async initialization timeout remains unresolved.

The exporter and restoration scripts were tested separately using temporary
configuration fixtures. That validates their file handling and patch
generation, not a new desktop installation.
