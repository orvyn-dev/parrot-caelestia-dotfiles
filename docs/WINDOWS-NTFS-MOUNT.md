# Restore Windows NTFS auto-mount after reinstalling Parrot OS

This documents the working Windows/Parrot dual-boot setup on the Dell Latitude 5300. **Do not restore an old complete /etc/fstab** after an OS reinstall: Linux root and swap UUIDs may have changed. Add only the Windows entry.

## Previously working configuration (27 October 2026)

| Setting | Value |
|---|---|
| Windows partition | `/dev/nvme0n1p3` |
| Windows filesystem | NTFS |
| Windows partition UUID | `FE9A3ADD9A3A925F` |
| Mount directory | `/mnt/windows-drive` |
| Driver | `ntfs-3g` (shown as `fuseblk` by `findmnt`) |
| Linux account UID/GID | `1000/1000` (script detects fresh-install values) |
| Mount options | `uid=1000,gid=1000,umask=022,nofail,x-gvfs-show` |

The Windows partition was mounted successfully and normal-user read, write, and delete access was tested. UUIDs and user IDs should be verified on a new installation.

## Fast restore on a freshly installed Parrot OS

1. Boot into Parrot OS. Windows must be fully shut down, not hibernated. Disable Windows Fast Startup before accessing NTFS from Linux.
2. Run `lsblk -f` and identify the **main Windows NTFS volume** (not the small Windows recovery partition). Its UUID should still be `FE9A3ADD9A3A925F` unless the Windows volume was reformatted or replaced.
3. Clone this repository and inspect the script:

   ```bash
   sudo apt update
   sudo apt install -y git
   git clone https://github.com/orvyn-dev/parrot-caelestia-dotfiles.git
   cd parrot-caelestia-dotfiles
   less scripts/setup-windows-drive.sh
   sudo bash scripts/setup-windows-drive.sh
   ```

4. The script shows the device, detected UID/GID, and proposed entry, then asks for confirmation. It installs ntfs-3g if needed, backs up fstab before changing it, avoids duplicate entries, reloads systemd, verifies fstab, and mounts the drive.
5. To check the result:

   ```bash
   findmnt /mnt/windows-drive
   ls /mnt/windows-drive
   xdg-open /mnt/windows-drive
   ```

6. After a reboot, **without running mount manually**, run `findmnt /mnt/windows-drive` to confirm automatic mounting.

If the NTFS UUID changed, run `lsblk -f` and specify the **new Windows UUID** explicitly:

```bash
sudo bash scripts/setup-windows-drive.sh YOUR_NEW_WINDOWS_UUID
```

Never use your Linux ext4 or swap UUID as the Windows UUID.

## Manual alternative

Install NTFS support, create the mountpoint, and back up fstab:

```bash
sudo apt update
sudo apt install -y ntfs-3g
sudo mkdir -p /mnt/windows-drive
sudo cp -a /etc/fstab /etc/fstab.backup
sudo nano /etc/fstab
```

Add exactly one Windows entry, replacing the UUID and UID/GID *if they changed* (`blkid` and `id -u; id -g`):

```fstab
# Windows Drive
UUID=FE9A3ADD9A3A925F /mnt/windows-drive ntfs-3g uid=1000,gid=1000,umask=022,nofail,x-gvfs-show 0 0
```

Do not modify the current installation's existing `/`, `/boot/efi`, swap, or `/tmp` entries. Reload, validate, then mount:

```bash
sudo systemctl daemon-reload
sudo findmnt --verify --verbose
sudo mount /mnt/windows-drive
findmnt /mnt/windows-drive
```

`findmnt --verify` may emit warnings such as "ntfs-3g seems unsupported by the current kernel" or "ntfs-3g does not match with on-disk ntfs". The ntfs-3g FUSE driver is userspace, so these checks are not by themselves proof of a mount failure. The actual `mount` and `findmnt` results matter.

## Access test (only when NTFS is safely writable)

```bash
touch /mnt/windows-drive/Parrot-Mount-Test.txt
ls -l /mnt/windows-drive/Parrot-Mount-Test.txt
rm /mnt/windows-drive/Parrot-Mount-Test.txt
```

An existing `hiberfil.sys` is normal and alone does not prove Windows is currently hibernated. If NTFS refuses a writable mount because of an unsafe Windows state, **do not force the mount or remove the hibernation file**; fully shut down Windows first.

This guide stores the *recipe*, not a copy of the machine's `/etc/fstab`. Do not publish full fstab files with sensitive network mounts or credentials.
