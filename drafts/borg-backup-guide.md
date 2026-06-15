# Borg Backup: Encrypted, Deduplicated, Reliable

If you've ever watched a backup job eat 300GB for what should have been a 2GB incremental, or had to explain to your future self why your backups live on an unencrypted USB drive in a drawer, this guide is for you.

BorgBackup (usually just called **Borg**) is a deduplicating archiver with compression and encryption. It's been around since 2010, forked from Attic, and it's the kind of tool that doesn't get flashy headlines—but quietly keeps people's data safe in server closets and home labs around the world.

This isn't a theoretical overview. This is the Borg setup I'd actually run.

---

## Why Borg?

Borg does three things exceptionally well:

1. **Deduplication** — Only stores unique data chunks. Back up a 50GB VM twice, and the second backup might add only a few hundred megabytes if most blocks haven't changed.
2. **Compression** — Optional zlib, lz4, or zstd compression reduces archive size.
3. **Encryption** — Everything is encrypted client-side. Your passphrase never leaves your machine. Back up to a friend's server, a cloud provider, or a NAS in the basement—if they don't have your key, they don't have your data.

The result: efficient, secure backups that don't waste disk space or bandwidth.

---

## How Borg Compares to Alternatives

| Tool | Deduplication | Encryption | Compression | Best For |
|------|-------------|------------|-------------|----------|
| **Borg** | ✅ Block-level | ✅ Client-side AES-256 | ✅ zstd/lz4/zlib | Local & remote archives, Linux servers, daily incrementals |
| **rsync** | ❌ None | ❌ None | ❌ None | Fast file syncing, mirroring |
| **Restic** | ✅ Block-level | ✅ Client-side | ✅ Auto | Cloud-native (S3, B2), multi-platform |
| **Duplicati** | ✅ Block-level | ✅ AES-256 | ✅ ZIP | GUI users, Windows/Linux/Mac |
| **Kopia** | ✅ Block-level | ✅ AES-256-GCM | ✅ Auto | Modern UI, policy-driven, S3/B2/Azure |
| **Proxmox Backup Server** | ✅ Fixed-size chunks | ✅ AES-256-GCM | ✅ Zstandard | Proxmox VMs/containers only |

**Rsync** isn't really a backup tool—it's a sync tool. No versioning, no dedup, no encryption. Use it for mirroring, not for disaster recovery.

**Restic** is Borg's closest competitor. It has broader cloud support and doesn't require a server-side Borg installation. But Borg is generally faster for local repositories and has more mature pruning and archive management. If you're backing up to S3, Restic might be the better fit. If you're backing up to a local NAS or a VPS with Borg installed, Borg wins on speed and flexibility.

**Duplicati** is friendly and GUI-driven, but it's slower and has a reputation for occasionally breaking its own database. Fine for desktops, less ideal for servers.

**Kopia** is the new kid on the block—modern UI, policy-driven, great cloud support. But it's younger, the ecosystem is smaller, and Borg's CLI is more battle-tested.

**Proxmox Backup Server** is excellent if you live entirely in Proxmox-land. For anything else, you need a second tool anyway.

I run Borg because it's fast, it's scriptable, and it doesn't surprise me.

---

## Installation

Borg is in most distro repositories. If you need the latest version, check the [official releases](https://github.com/borgbackup/borg/releases).

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install borgbackup

# Fedora/RHEL
sudo dnf install borgbackup

# Arch
sudo pacman -S borg

# macOS
brew install borgbackup

# pip (if you must)
pip install borgbackup
```

Verify:
```bash
borg --version
# borg 1.4.0 (or newer)
```

---

## Basic Commands

### Initialize a Repository

```bash
# Local repository
borg init --encryption=repokey-blake2 /mnt/backups/borg-repo

# Remote repository via SSH
borg init --encryption=repokey-blake2 user@backup-server:/backups/myhost
```

Encryption modes worth knowing:
- `repokey-blake2` — Key stored in the repo, passphrase-protected (easiest, recommended)
- `keyfile-blake2` — Key stored locally on the client (more secure, but don't lose it)
- `none` — Don't. Just don't.

You'll be prompted for a passphrase. Make it good. Store it in a password manager. This is your data's lifeline.

### Create a Backup Archive

```bash
export BORG_REPO=/mnt/backups/borg-repo
export BORG_PASSPHRASE='your-super-secret-passphrase'

borg create \
  --verbose \
  --filter AME \
  --list \
  --stats \
  --show-rc \
  --compression zstd,9 \
  --exclude-caches \
  --exclude '/home/*/Downloads' \
  --exclude '/home/*/.cache' \
  --exclude '/var/log/journal' \
  ::'{hostname}-{now:%Y-%m-%d-%H%M}' \
  /etc \
  /home \
  /var/www
```

Breakdown:
- `--compression zstd,9` — zstd at level 9 (good balance of speed vs. size)
- `::{hostname}-{now:...}` — Archive naming with timestamp
- `--exclude-caches` — Skips directories tagged with `CACHEDIR.TAG`

### List Archives

```bash
borg list
```

### List Contents of an Archive

```bash
borg list ::myhost-2025-01-15-0300
```

### Extract a Backup

```bash
# Extract everything to current directory
borg extract ::myhost-2025-01-15-0300

# Extract specific path
borg extract ::myhost-2025-01-15-0300 home/user/documents

# Extract to a specific destination
borg extract --destination /tmp/restore ::myhost-2025-01-15-0300
```

**Important:** Extraction preserves original paths. If you back up `/etc/hosts`, extracting puts it at `./etc/hosts` relative to your current directory.

### Delete an Archive

```bash
borg delete ::myhost-2025-01-15-0300
```

Or delete the whole repo:
```bash
borg delete /mnt/backups/borg-repo
```

---

## Real-World Backup Strategy

Here's what I actually run. Adjust retention to your paranoia level.

### The Policy

- **Daily** incremental backups at 2:00 AM
- **Weekly** doesn't exist as a separate "full" in Borg—every backup is a full snapshot. But I keep weekly snapshots longer.
- **Pruning:** Keep 7 daily, 4 weekly, 6 monthly, 1 yearly

### The Script

```bash
#!/bin/bash
# /usr/local/bin/backup-daily.sh

set -euo pipefail

export BORG_REPO="ssh://backup-user@nas.local/mnt/backups/borg/myhost"
export BORG_PASSPHRASE="$(cat /root/.borg-passphrase)"
export BORG_RSH="ssh -i /root/.ssh/backup_ed25519"

LOGFILE="/var/log/borg/backup-$(date +%Y%m%d).log"
mkdir -p /var/log/borg

borg create \
  --verbose \
  --stats \
  --show-rc \
  --compression zstd,6 \
  --exclude-caches \
  --exclude '/home/*/.cache' \
  --exclude '/var/tmp' \
  --exclude '/var/log/journal' \
  --exclude '/proc' \
  --exclude '/sys' \
  --exclude '/dev' \
  --exclude '/run' \
  ::'{hostname}-{now:%Y-%m-%d-%H%M}' \
  /etc \
  /home \
  /var/www \
  /usr/local/etc \
  /root \
  2>&1 | tee "$LOGFILE"

# Prune old backups
borg prune \
  --verbose \
  --list \
  --show-rc \
  --keep-daily=7 \
  --keep-weekly=4 \
  --keep-monthly=6 \
  --keep-yearly=1 \
  2>&1 | tee -a "$LOGFILE"

# Compact to reclaim space (Borg 1.2+)
borg compact 2>&1 | tee -a "$LOGFILE"

# Check backup health monthly (on the 1st)
if [[ $(date +%d) == "01" ]]; then
  borg check --show-rc 2>&1 | tee -a "$LOGFILE"
fi
```

Make it executable:
```bash
chmod +x /usr/local/bin/backup-daily.sh
```

---

## Automation with Systemd Timers

I prefer systemd timers over cron—they have better logging, failure handling, and it's easier to see if a job is running.

### Timer Unit

```ini
# /etc/systemd/system/borg-backup.timer
[Unit]
Description=Daily Borg Backup

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Service Unit

```ini
# /etc/systemd/system/borg-backup.service
[Unit]
Description=Borg Backup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup-daily.sh
User=root
Environment="BORG_REPO=ssh://backup-user@nas.local/mnt/backups/borg/myhost"
EnvironmentFile=/root/.borg-env

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/log/borg
```

### Environment File

```bash
# /root/.borg-env
BORG_PASSPHRASE=your-passphrase-here
BORG_RSH=ssh -i /root/.ssh/backup_ed25519
```

### Enable and Start

```bash
systemctl daemon-reload
systemctl enable --now borg-backup.timer

# Check status
systemctl list-timers borg-backup.timer
journalctl -u borg-backup.service -f
```

If you prefer cron, that's fine too:

```bash
# /etc/cron.d/borg-backup
0 2 * * * root /usr/local/bin/backup-daily.sh
```

---

## Remote Backups

### Over SSH (Standard)

The examples above already use SSH. Key requirements:

1. Generate a dedicated key pair (no passphrase, since it's automated):
```bash
ssh-keygen -t ed25519 -f /root/.ssh/backup_ed25519 -N ""
```

2. Copy public key to backup server:
```bash
ssh-copy-id -i /root/.ssh/backup_ed25519.pub backup-user@nas.local
```

3. Restrict the key on the server side (`~backup-user/.ssh/authorized_keys`):
```
restrict,command="borg serve --restrict-to-path /mnt/backups/borg/myhost" ssh-ed25519 AAAAC3... root@myhost
```

This is critical. The `restrict` and `command` options ensure that even if the client is compromised, the attacker can only run Borg operations on that specific path—not get a shell.

### Rsync.net

[Rsync.net](https://rsync.net) is a popular Borg-compatible storage provider. They offer discounted rates if you mention you're using Borg.

```bash
export BORG_REPO="ssh://1234@usw-s001.rsync.net/borg-repo"
export BORG_RSH="ssh -i /root/.ssh/rsyncnet_ed25519"
```

Same workflow, just a different remote.

### S3-Compatible (Via Rclone or S3FS)

Borg doesn't speak S3 natively, but you can mount S3 buckets with [rclone](https://rclone.org) or s3fs:

```bash
# Mount S3 bucket
rclone mount remote:backup-bucket /mnt/s3-backup --vfs-cache-mode writes &

# Use Borg on the mount
export BORG_REPO=/mnt/s3-backup/borg-repo
borg init --encryption=repokey-blake2
```

Caveat: S3-backed repositories are slower. Borg expects POSIX filesystem semantics. Use this for cold storage, not your primary backup target.

---

## Docker Container Backup Strategy

Docker volumes aren't regular directories. Here's how I back them up:

### Method 1: Volume Mounts (Preferred)

If your compose file already mounts data to the host:

```yaml
# docker-compose.yml
services:
  nextcloud:
    image: nextcloud
    volumes:
      - /opt/nextcloud/data:/var/www/html/data
      - /opt/nextcloud/config:/var/www/html/config
```

Just back up `/opt/nextcloud`:

```bash
borg create ::'{hostname}-{now}' /opt/nextcloud
```

### Method 2: Named Volumes

For named volumes, use a temporary container:

```bash
# Backup
borg create ::'{hostname}-{now}' \
  /etc \
  /home \
  --stdin-name nextcloud-data \
  -- \
  docker run --rm -v nextcloud_data:/data -i busybox tar -cf - -C /data .
```

Or simpler, mount the Docker volume directory directly:

```bash
# Docker volumes live here on Linux
borg create ::'{hostname}-{now}' /var/lib/docker/volumes/nextcloud_data/_data
```

### Method 3: Application-Aware (Database Dumps)

For databases, dump first, then back up the dump:

```bash
#!/bin/bash
# Pre-backup database dumps
mkdir -p /opt/backups/dumps

docker exec postgres pg_dumpall -U postgres > /opt/backups/dumps/postgres-all.sql
docker exec mariadb mysqldump --all-databases -u root -p'password' > /opt/backups/dumps/mariadb-all.sql

# Now back up everything
borg create ::'{hostname}-{now}' /etc /home /opt/backups/dumps
```

---

## VM Backup Strategy

### Proxmox VMs (LXC and QEMU)

Proxmox has its own backup system, but I also mirror critical data to Borg.

**For LXC containers:**

```bash
# Stop container (or use --suspend for running)
pct stop 100

# Backup the container's rootfs
borg create ::'pve-100-{now}' /var/lib/lxc/100/rootfs

pct start 100
```

**For QEMU VMs:**

```bash
# Create a snapshot
qm snapshot 101 pre-backup

# Backup the VM disk (while snapshot is active)
borg create ::'vm-101-{now}' /var/lib/vz/images/101/

# Remove snapshot after successful backup
qm delsnapshot 101 pre-backup
```

Better yet, use Proxmox Backup Server for VMs and Borg for the files/databases inside them. Layered protection.

### Generic VM Backup

For any VM (VirtualBox, VMware, KVM):

1. **Snapshot or shutdown** the VM
2. **Back up the virtual disk files** (.qcow2, .vmdk, etc.)
3. **Also back up the VM config** (XML, .vmx files)

```bash
# KVM/QEMU example
borg create ::'kvm-win10-{now}' \
  /etc/libvirt/qemu/win10.xml \
  /var/lib/libvirt/images/win10.qcow2
```

---

## Restoring from Backup

This is where the panic usually sets in. Here's the step-by-step:

### 1. Find the Right Archive

```bash
borg list
# myhost-2025-01-15-0200    Wed, 2025-01-15 02:00:01
# myhost-2025-01-14-0200    Tue, 2025-01-14 02:00:01
```

### 2. See What's Inside

```bash
borg list ::myhost-2025-01-15-0200
```

### 3. Extract to a Temporary Location

```bash
cd /tmp/restore-test
borg extract ::myhost-2025-01-15-0200 home/user/documents
```

### 4. Verify the Data

Actually open some files. Make sure they're not corrupted. Don't skip this step.

### 5. Restore in Place (Carefully)

```bash
# Move old directory aside (don't delete yet!)
mv /home/user/documents /home/user/documents.broken-$(date +%s)

# Extract from backup
borg extract ::myhost-2025-01-15-0200 home/user/documents
mv /home/user/documents/home/user/documents /home/user/documents
rmdir /home/user/documents/home/user
```

### 6. Mount an Archive (Read-Only)

For browsing without extracting:

```bash
mkdir -p /mnt/borg-mount
borg mount ::myhost-2025-01-15-0200 /mnt/borg-mount
ls /mnt/borg-mount
df -h /mnt/borg-mount  # It's a FUSE mount, no extra disk space used
borg umount /mnt/borg-mount
```

### 7. Full System Restore

If you're restoring an entire system (e.g., after a drive failure):

1. Boot from a Linux live USB
2. Install Borg: `apt install borgbackup`
3. Mount your new root filesystem: `mount /dev/sda1 /mnt`
4. Restore: `borg extract --destination /mnt ::myhost-2025-01-15-0200`
5. Fix fstab, reinstall bootloader, reboot

---

## Monitoring Backup Health

Backups you don't monitor are Schrödinger's backups—both working and broken until you need them.

### Check Repository Health

```bash
borg check --verify-data ::
# or just check metadata (faster)
borg check ::
```

Run `--verify-data` monthly, regular `check` weekly.

### Extract Exit Codes

Borg returns specific exit codes:
- `0` — Success
- `1` — Warning (e.g., files changed while reading)
- `2` — Error

Check this in your scripts:

```bash
borg create ...
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Backup succeeded"
elif [ $EXIT_CODE -eq 1 ]; then
  echo "Backup succeeded with warnings"
else
  echo "Backup FAILED with code $EXIT_CODE"
  # Send alert
fi
```

### Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/borg-health-check.sh

export BORG_REPO=ssh://backup-user@nas.local/mnt/backups/borg/myhost
export BORG_PASSPHRASE=$(cat /root/.borg-passphrase)

LAST_ARCHIVE=$(borg list --short | tail -1)
LAST_DATE=$(echo "$LAST_ARCHIVE" | grep -oP '\d{4}-\d{2}-\d{2}')
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d yesterday +%Y-%m-%d)

if [[ "$LAST_DATE" != "$TODAY" && "$LAST_DATE" != "$YESTERDAY" ]]; then
  echo "ALERT: No backup found for today or yesterday! Last: $LAST_ARCHIVE"
  # Send to monitoring/alerting
  exit 1
fi

# Check repo integrity
borg check --show-rc || exit 1

echo "Backup health: OK"
```

### Monitoring Integrations

- **Prometheus**: Use [borg-exporter](https://github.com/prometheus-community/node-exporter-textfile-collector-scripts/blob/master/borg_backup.sh) or parse logs
- **Nagios/Zabbix**: Wrap the health check script
- **Uptime Kuma**: HTTP ping a small status file written by your backup script
- **Simple**: Email yourself on failure using `mail` or `sendmail`

---

## Performance Tuning

### Compression Levels

| Level | Speed | Size | Use Case |
|-------|-------|------|----------|
| `lz4` | Fastest | Largest | Large files, fast networks, CPU-constrained |
| `zstd,3` | Fast | Small | Default sweet spot |
| `zstd,9` | Slow | Smaller | Slow networks, storage-constrained |
| `zstd,22` | Slowest | Smallest | Initial seed, archival |

I run `zstd,6` for daily backups. Adjust based on your bottleneck (CPU vs. storage vs. bandwidth).

### Segment Size

For very large repositories, increase the segment size:

```bash
borg config /mnt/backups/borg-repo additional_free_space 2G
borg config /mnt/backups/borg-repo storage_quota 500G
```

### Parallelization

Borg is single-threaded for compression, but you can run multiple backups in parallel to different repos. For a single large backup, you're mostly waiting on I/O.

### Network Speed

For remote backups over slow links:

```bash
# Use lower compression (faster = less data to send = paradoxically faster)
# Actually, use higher compression to reduce bandwidth
--compression zstd,9

# Or use a tool like mbuffer for network buffering
borg create --remote-buffer 100M ...
```

### Cache Location

Borg caches chunk hashes locally. For large repos, ensure your cache directory (`~/.cache/borg`) is on fast storage:

```bash
export BORG_CACHE_DIR=/tmp/borg-cache  # Or an SSD mount
```

### Exclude Smart

The biggest performance win is backing up less:

```bash
--exclude '/home/*/.cache'
--exclude '/var/log/journal'
--exclude '/var/lib/docker/overlay2'  # Container layers, not your data
--exclude '/swapfile'
--exclude '*.tmp'
```

---

## Conclusion

Borg isn't the newest backup tool, and it doesn't have the slickest web UI. What it has is fifteen years of reliability, a CLI that doesn't change every six months, and the kind of predictable behavior that lets you sleep through the night.

If you set up one thing from this guide, make it the systemd timer with health checks. A backup you don't have to think about is the only backup worth having.

And please—test your restores. A backup you've never restored from is just a wish.

---

## Quick Reference

```bash
# Init
borg init --encryption=repokey-blake2 /path/to/repo

# Backup
borg create ::'{hostname}-{now}' /path/to/backup

# List
borg list
borg list ::archive-name

# Extract
borg extract ::archive-name path/within/backup

# Mount
borg mount ::archive-name /mnt/borg

# Prune
borg prune --keep-daily=7 --keep-weekly=4 --keep-monthly=6

# Check
borg check ::
borg check --verify-data ::

# Delete
borg delete ::archive-name

# Compact (reclaim space)
borg compact

# Info
borg info ::
borg info ::archive-name
```

---

*Happy backing up. May you never need this guide in an emergency.*
