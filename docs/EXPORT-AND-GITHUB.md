# Export the working laptop and upload to GitHub

## 1. Extract the repository package

Extract `parrot-caelestia-dotfiles.zip` into your Projects directory, or
another location you use for Git repositories. Open Konsole inside the
extracted `parrot-caelestia-dotfiles` directory.

Every command below assumes that directory is the current working directory.
Use your normal desktop account, without sudo.

## 2. Capture the actual working files

```bash
python3 scripts/export-dotfiles.py --include-terminal
```

The terminal option adds the existing Zsh files, Starship configuration,
Konsole settings, profiles, and color schemes. Without that option, the
export contains just Hyprland/Caelestia and the build metadata.

The script requires the existing
`~/.local/src/caelestia-shell-v1.1.1` worktree so it can compare the installed
QML against the recorded upstream tag. Keep that source checkout until the
snapshot is created.

| Snapshot path | Contents |
|---|---|
| `snapshot/config/hypr/hyprland.lua` | Current running Hyprland configuration |
| `snapshot/config/caelestia/shell.json` | Current shell settings |
| `snapshot/config/caelestia/cli.json` | Current CLI settings |
| `snapshot/patches/caelestia-qt68.patch` | Installed QML differences against upstream v1.1.1 |
| `snapshot/overrides/quickshell/caelestia/` | Copies of changed QML files |
| `snapshot/terminal/` | Optional terminal dotfiles |
| `snapshot/manifest.json` | Source revisions, version output, build flags, and hashes |
| `snapshot/packages.tsv` | Installed APT versions for the selected dependencies |
| `snapshot/licenses/Caelestia-LICENSE` | Original upstream license |
| `snapshot/SHA256SUMS` | Checksums of exported files |

The script creates a new snapshot directory. It stops if that directory
already exists rather than mixing two exports. For another dated export:

```bash
python3 scripts/export-dotfiles.py --include-terminal \
  --output "snapshots/$(date +%Y%m%d-%H%M%S)"
```

For the first GitHub upload, use the default `snapshot/` location.

## 3. Review the exported configuration

```bash
python3 -m json.tool snapshot/manifest.json
rg --files --hidden snapshot
sed -n '1,180p' snapshot/config/hypr/hyprland.lua
```

Read your optional Zsh and terminal files before making them public. Remove
personal credentials or private commands if you have added any to those
configuration files. The export does not collect browser profiles, SSH keys,
VPN profiles, network connection credentials, shell history, caches, or logs.

Verify the snapshot's checksums from inside its directory:

```bash
cd snapshot
sha256sum -c SHA256SUMS
cd ..
```

If you intentionally edit an exported file before publishing, its old
checksum will no longer match. Re-export to a fresh directory to generate
a consistent manifest, or clearly identify that edit as a published
configuration change rather than a byte-for-byte laptop snapshot.

## 4. Create the local Git repository

```bash
git init -b main
git add .gitignore .gitattributes README.md LICENSE THIRD_PARTY.md \
  config docs manifests overrides packages scripts snapshot
git diff --cached --stat
git diff --cached
```

`git init` creates local version history. `git add` stages the selected
repository files. The two diff commands show what the first commit will
contain.

When the staged contents are correct:

```bash
git commit -m "Document working Parrot Hyprland and Caelestia setup"
```

If Git asks for your identity, set the name and email you want attached to
commits. A GitHub no-reply address is an option if you use one:

```bash
git config user.name "YOUR_COMMIT_NAME"
git config user.email "YOUR_COMMIT_EMAIL"
git commit -m "Document working Parrot Hyprland and Caelestia setup"
```

These settings apply to this repository because the commands omit
`--global`.

## 5. Create an empty GitHub repository

On GitHub, create a repository named `parrot-caelestia-dotfiles`.
Suggested description:

> My Parrot Linux desktop: Hyprland 0.55, Caelestia on Qt 6.8, Konsole and Zsh,
> with build notes and compatibility fixes.

Choose the visibility you want. Leave GitHub's automatic README, license,
and .gitignore options unselected, because this repository already contains
those files.

## 6. Connect and push

Replace `YOUR_GITHUB_USERNAME` with your account name:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/parrot-caelestia-dotfiles.git
git push -u origin main
```

Use your existing GitHub Git authentication when prompted. For HTTPS Git,
use a credential helper or a personal access token when Git asks for a
password. GitHub account passwords do not authenticate Git pushes.

GitHub reference:
[About remote repositories](https://docs.github.com/en/get-started/git-basics/about-remote-repositories).

## 7. Add a desktop screenshot, if desired

Arrange the desktop as you want it shown publicly, then run:

```bash
mkdir -p screenshots
grim screenshots/desktop.png
```

Add this line near the top of README.md after the image exists:

```markdown
![My Parrot Caelestia desktop](screenshots/desktop.png)
```

Commit the image and README change:

```bash
git add screenshots/desktop.png README.md
git commit -m "Add desktop screenshot"
git push
```

## Updating the dotfiles later

Make the desktop change, verify it in Hyprland, then export to a new dated
snapshot directory. Compare it with the previous snapshot and commit the
configuration change with a description of the behavior you changed.

Keep binaries, CMake build directories, dependency clones, fonts, runtime
logs, and generated caches outside the Git repository. The source versions,
package records, documentation, and patches are the reproducible part.
