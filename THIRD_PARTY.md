# Upstream projects and attribution

This is a personal installation and configuration repository. It documents
how the upstream projects were combined on Parrot Linux.

## Projects

| Project | Source | Role |
|---|---|---|
| Caelestia Shell | [caelestia-dots/shell](https://github.com/caelestia-dots/shell) | Desktop QML, native plugin, and bundled assets |
| Caelestia CLI | [caelestia-dots/cli](https://github.com/caelestia-dots/cli) | Wallpaper, colors, and desktop helper commands |
| Quickshell | [quickshell-mirror/quickshell](https://github.com/quickshell-mirror/quickshell) | Shell runtime |
| M3Shapes | [soramanew/m3shapes](https://github.com/soramanew/m3shapes) | Native Material shape library and QML module |
| libcava fork | [LukashonakV/cava](https://github.com/LukashonakV/cava) | CAVA shared-library build |
| Hyprland | [hyprwm/Hyprland](https://github.com/hyprwm/Hyprland) | Wayland compositor |
| Qt | [Qt documentation](https://doc.qt.io/qt-6.8/) | Qt 6.8 runtime, development libraries, and QML |
| Papirus | [PapirusDevelopmentTeam/papirus-icon-theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) | Application icons |
| Parrot | [Parrot OS](https://parrotsec.org/) | Distribution packages and backports |

## Caelestia-derived files

The reference Elevation component adapts Caelestia v1.1.1 for Qt 6.8.
The exported overrides and patch are differences against that upstream
release. Original upstream copyright and license notices remain applicable.

The documentation, reference configuration, helper scripts, and
Caelestia-derived compatibility component in this package are distributed
under GNU GPL version 3; see [LICENSE](LICENSE).
The exporter also includes the original Caelestia LICENSE at
`snapshot/licenses/Caelestia-LICENSE`.

Third-party projects retain their own licenses. This repository's license
does not relicense dependencies, fonts, icons, user images, or independently
licensed content that a user chooses to export.

## Font sources

Font binaries are downloaded into the user's home directory rather than
bundled in this Git repository.

| Family | Source |
|---|---|
| Rubik | [Google Fonts Rubik](https://github.com/google/fonts/tree/main/ofl/rubik), including its OFL notice |
| Material Symbols Rounded | [Google Material Design Icons](https://github.com/google/material-design-icons/tree/master/variablefont), with the upstream repository's license notices |
| Optional CaskaydiaCove Nerd Font | [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts), including the original font and patching notices |

The download helper uses the two URLs used during the setup. The exported
manifest records checksums of installed fonts without redistributing them.

## Images

Wallpaper images and the user's profile photo are not automatically exported.
The temporary dinosaur avatar is an asset from the installed Caelestia shell.
If adding images or screenshots to the public repository, retain the source
and license information for any separately included artwork.

## Technical references

- [Qt 6.9 additions](https://doc.qt.io/qt-6.9/whatsnew69.html)
- [Qt 6.8 MultiEffect](https://doc.qt.io/qt-6.8/qml-qtquick-effects-multieffect.html)
- [Qt 6.8 DelegateChooser](https://doc.qt.io/qt-6.8/qml-qt-labs-qmlmodels-delegatechooser.html)
- [Quickshell 0.3.1 API](https://quickshell.org/docs/v0.3.1/)
- [Quickshell IPC handlers](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/IpcHandler/)
- [Hyprland 0.55 Lua binds](https://wiki.hypr.land/0.55.0/Configuring/Basics/Binds/)
- [Hyprland 0.55 dispatchers](https://wiki.hypr.land/0.55.0/Configuring/Basics/Dispatchers/)
- [GitHub remote repositories](https://docs.github.com/en/get-started/git-basics/about-remote-repositories)

The version-specific pages and recorded terminal output take precedence over
newer examples when reproducing this installation.
