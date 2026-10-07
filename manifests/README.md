# Version records

`reference-versions.json` contains the values observed in the setup
conversation. A null commit means the value was not supplied; it is not a
claim that the latest upstream commit was tested.

Run `python3 scripts/export-dotfiles.py` on the working laptop to generate
`snapshot/manifest.json`. It records:

- Installed Hyprland, Quickshell, CLI, and Qt version output.
- The full Caelestia v1.1.1 baseline commit.
- Existing source checkout commits, tracked changes, and selected CMake flags.
- Changed or deleted running QML files.
- Installed versions of the selected APT dependencies.
- Resolved font families, font checksums, and exported file checksums.

The checkout commit and the installed binary's version are separate pieces
of evidence. If a checkout has moved since its build, the manifest exposes
both observations rather than assuming they identify the same build.

For exact reproduction, retain `snapshot/manifest.json`,
`snapshot/packages.tsv`, and the generated patch in Git together.
