#!/usr/bin/env bash
# Restore a Windows NTFS auto-mount on Parrot OS without altering Linux partitions.
set -Eeuo pipefail

MOUNT_POINT="/mnt/windows-drive"
DEFAULT_UUID="FE9A3ADD9A3A925F"
FSTAB="/etc/fstab"

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

if (( EUID != 0 )); then
  die "Run as your normal user with: sudo bash scripts/setup-windows-drive.sh [WINDOWS_UUID]"
fi
if [[ -z "${SUDO_UID:-}" || -z "${SUDO_GID:-}" ]]; then
  die "Run with sudo from your own Linux account, so the correct UID/GID can be used."
fi
if (( $# > 1 )); then
  die "Usage: sudo bash scripts/setup-windows-drive.sh [WINDOWS_UUID]"
fi

WINDOWS_UUID="${1:-$DEFAULT_UUID}"
DEVICE="$(blkid -U "$WINDOWS_UUID" 2>/dev/null || true)"
if [[ -z "$DEVICE" ]]; then
  lsblk -f
  die "UUID $WINDOWS_UUID not found. Identify your Windows NTFS partition using lsblk -f and rerun with its UUID."
fi
FS_TYPE="$(blkid -o value -s TYPE "$DEVICE")"
[[ "$FS_TYPE" == "ntfs" ]] || die "$DEVICE has filesystem type $FS_TYPE, not NTFS."

LINE="UUID=$WINDOWS_UUID $MOUNT_POINT ntfs-3g uid=$SUDO_UID,gid=$SUDO_GID,umask=022,nofail,x-gvfs-show 0 0"

printf 'Windows partition : %s\n' "$DEVICE"
printf 'Filesystem        : %s\n' "$FS_TYPE"
printf 'Target mountpoint : %s\n' "$MOUNT_POINT"
printf 'Linux UID/GID     : %s/%s\n' "$SUDO_UID" "$SUDO_GID"
printf 'fstab line        : %s\n\n' "$LINE"

if findmnt -rn --mountpoint "$MOUNT_POINT" >/dev/null; then
  SOURCE="$(findmnt -rn -o SOURCE --mountpoint "$MOUNT_POINT")"
  [[ "$SOURCE" == "$DEVICE" ]] || die "$MOUNT_POINT is already mounted from $SOURCE, not $DEVICE."
fi

read -r -p "Apply this mount configuration? [y/N] " REPLY
[[ "$REPLY" == "y" || "$REPLY" == "Y" ]] || { echo "No changes made."; exit 0; }

if ! command -v ntfs-3g >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ntfs-3g
fi

mkdir -p "$MOUNT_POINT"
if grep -Fqx -- "$LINE" "$FSTAB"; then
  echo "Matching fstab entry already exists; nothing to add."
else
  if awk -v id="UUID=$WINDOWS_UUID" -v target="$MOUNT_POINT" \
      '$0 !~ /^[[:space:]]*#/ && ($1 == id || $2 == target) {found=1} END {exit !found}' "$FSTAB"; then
    die "An existing fstab entry uses this UUID or mountpoint. Inspect /etc/fstab manually to avoid duplicates."
  fi
  BACKUP="$FSTAB.backup.$(date +%Y%m%d-%H%M%S)"
  cp -a "$FSTAB" "$BACKUP"
  printf '\n# Windows NTFS drive - Parrot OS\n%s\n' "$LINE" >> "$FSTAB"
  printf 'Backup saved: %s\n' "$BACKUP"
fi

systemctl daemon-reload
findmnt --verify --verbose
if ! findmnt -rn --mountpoint "$MOUNT_POINT" >/dev/null; then
  mount "$MOUNT_POINT"
fi
findmnt --mountpoint "$MOUNT_POINT"
printf '\nDone. Reboot and run: findmnt %s\n' "$MOUNT_POINT"
