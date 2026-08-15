---
layout: post.njk
title: "Docker Backup Playbook: Restic, Dockstash & the 3-2-1 Rule — Encrypted Off-Site Backups in 15 Minutes"
date: 2026-08-14
description: "r/selfhosted asks 'how do you back up Docker volumes?' every single week. Here's the definitive answer: copy-paste Docker Compose for encrypted, deduplicated, off-site backups using Restic, Dockstash, Fortified, and backup-maker — with the 3-2-1 rule baked in."
tags: ["docker", "backup", "restic", "dockstash", "self-hosted", "homelab", "devops", "3-2-1", "b2", "s3"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/docker-backup-playbook-restic-dockstash-2026"
---

# Docker Backup Playbook: Restic, Dockstash & the 3-2-1 Rule

Every week on r/selfhosted, someone posts the same question: *"How do you back up your Docker volumes?"* And every week, the answers are a mess. Some people say "just rsync the whole /var/lib/docker folder" (please don't). Others say "I use a bash script I wrote in 2019" (also please don't). A few mention Restic but don't explain how to actually set it up.

Here's the thing: Docker volume backups are not hard. They're just poorly documented. The tools exist. The patterns are proven. You just need someone to show you the copy-paste version.

This is that post. By the end, you'll have encrypted, deduplicated, off-site backups for every Docker volume on your server — and you'll understand *why* each piece is there.

---

## Why This Matters (More Than You Think)

Let me tell you a quick story. In 2024, I lost my Home Assistant database. Not the whole server — just the MariaDB volume that stored two years of sensor data, automations, and device configurations. I had no backups. I spent a weekend rebuilding automations from memory and lost six months of energy monitoring data that I'll never get back.

That was the last time I ran a homelab without proper backups.

Here's what's at stake on a typical self-hosted server:

| Service | What You Lose Without Backups |
|---------|------------------------------|
| **Immich** | Every photo and video you've taken |
| **Vaultwarden** | Every password you own |
| **Home Assistant** | Years of automations and sensor history |
| **Jellyfin** | Watch history, playlists, custom metadata |
| **Nextcloud** | Documents, calendars, contacts |
| **Databases** | Every app's structured data |

Docker makes running services easy. It also makes losing them easy — one bad `docker compose down -v` and your volumes are gone. One corrupted disk and your entire homelab is a memory.

The good news? The backup tooling ecosystem has exploded in 2025-2026. We now have purpose-built tools that make Docker backups trivial. Let's walk through them.

---

## The 3-2-1 Rule (Non-Negotiable)

Before we touch any tools, let's establish the baseline. The 3-2-1 rule has been the gold standard for decades, and it applies perfectly to Docker volumes:

- **3 copies** of your data
- On **2 different types of media**
- With **1 copy off-site**

In practice for a homelab:

| Copy | Location | Media | Tool |
|------|----------|-------|------|
| **Primary** | Your Docker host | NVMe/SSD | Your running services |
| **Local backup** | External drive, NAS, or second machine | HDD | Restic (local repo) |
| **Off-site backup** | Backblaze B2, S3, or rsync.net | Cloud | Restic (remote repo) |

**Why two media types?** Because if your SSD fails, you don't want your backup on another SSD from the same batch. A spinning disk or cloud storage gives you diversity.

**Why off-site?** Because fire, flood, theft, and power surges don't care about your RAID array. If your house burns down, your local backup burns with it.

The tools we're about to set up handle all three copies automatically.

---

## The Tools: What We're Using and Why

### Restic: The Engine

[Restic](https://restic.net/) is the backbone of this entire playbook. It's a command-line backup tool written in Go that does three things exceptionally well:

1. **Deduplication** — Only stores unique data. If you back up 10 nearly-identical database dumps, Restic only stores the differences. Your 50GB of Docker volumes might only take 15GB in the repo.
2. **Encryption** — Everything is encrypted with AES-256 before it leaves your machine. Your cloud provider never sees your data.
3. **Snapshots** — Every backup is a point-in-time snapshot. You can restore from any point in history.

Restic supports local storage, SFTP, S3, Backblaze B2, Azure, Google Cloud Storage, and rclone backends. For most homelabbers, the combo is: **local repo on an external drive + remote repo on Backblaze B2**.

### Dockstash: The Docker-Native Wrapper

[Dockstash](https://github.com/shyim/dockstash) is a relatively new tool (2025) that wraps Restic in a Docker-native interface. Instead of writing shell scripts that stop containers, dump databases, run restic, and restart everything, Dockstash does it declaratively.

Key features:
- **Docker Compose integration** — Define backups in the same compose file as your services
- **Pre/post hooks** — Automatically dump databases before backup, run health checks after
- **Label-based discovery** — Tag volumes you want backed up, Dockstash finds them
- **Scheduling** — Built-in cron for automated backups

### Fortified: The Newcomer

[Fortified](https://github.com/dadatuputi/fortified) is even newer (2026) and takes a different approach. Instead of wrapping Restic, it's a standalone backup orchestrator designed specifically for Docker Compose stacks. It uses a YAML-based backup definition that lives alongside your compose files.

What makes Fortified interesting:
- **Stack-aware** — Understands that "backing up Immich" means backing up the database, the uploads folder, and the config — as a unit
- **Restore testing** — Can spin up a temporary stack from a backup to verify it works
- **Notifications** — Built-in Discord, Telegram, and Gotify alerts

### backup-maker: The Simple One

[backup-maker](https://github.com/niclasrst/backup-maker) is the simplest of the bunch. It's a single Go binary that creates tar archives of Docker volumes and pushes them to S3-compatible storage. No deduplication, no snapshots — just straightforward volume backups.

It's the right choice if:
- You have a small number of volumes
- You don't need incremental backups
- You want something you can understand in 5 minutes

---

## The Setup: Copy-Paste Docker Compose

Here's the complete setup. Create a `backups` directory on your Docker host and save this as `docker-compose.yml`:

```yaml
# backups/docker-compose.yml
# Encrypted, deduplicated Docker volume backups with Restic + Dockstash
# 3-2-1 rule: local repo on external drive + remote repo on Backblaze B2

services:
  # ──────────────────────────────────────────
  # Dockstash — Restic wrapper for Docker
  # ──────────────────────────────────────────
  dockstash:
    image: ghcr.io/shyim/dockstash:latest
    container_name: dockstash
    restart: unless-stopped
    environment:
      # Restic repository password (generate with: openssl rand -base64 32)
      RESTIC_PASSWORD: ${RESTIC_PASSWORD}
      # Backblaze B2 credentials
      B2_ACCOUNT_ID: ${B2_ACCOUNT_ID}
      B2_ACCOUNT_KEY: ${B2_ACCOUNT_KEY}
      # Local backup path (mount your external drive here)
      LOCAL_REPO: /backups/local
      # Remote backup repo (Backblaze B2)
      REMOTE_REPO: b2:${B2_BUCKET_NAME}:/docker-backups
      # Schedule: daily at 3 AM
      BACKUP_SCHEDULE: "0 3 * * *"
      # Retention: keep 7 daily, 4 weekly, 6 monthly, 2 yearly
      RETENTION_POLICY: |
        --keep-daily 7
        --keep-weekly 4
        --keep-monthly 6
        --keep-yearly 2
      # Prune old snapshots after backup
      PRUNE_AFTER_BACKUP: "true"
      # Healthchecks.io URL for monitoring (optional)
      HEALTHCHECK_URL: ${HEALTHCHECK_URL:-}
    volumes:
      # Mount external drive for local backups
      - /mnt/backup-drive:/backups/local
      # Docker socket for volume discovery
      - /var/run/docker.sock:/var/run/docker.sock:ro
      # Dockstash config
      - ./dockstash:/config

  # ──────────────────────────────────────────
  # Fortified — Stack-aware backup orchestrator
  # ──────────────────────────────────────────
  fortified:
    image: ghcr.io/dadatuputi/fortified:latest
    container_name: fortified
    restart: unless-stopped
    environment:
      FORTIFIED_CONFIG: /config/fortified.yml
      TZ: ${TZ:-America/New_York}
    volumes:
      - ./fortified:/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /mnt/backup-drive:/backups
    # Fortified uses its own config file (see below)

  # ──────────────────────────────────────────
  # backup-maker — Simple tar + S3 backups
  # ──────────────────────────────────────────
  backup-maker:
    image: ghcr.io/niclasrst/backup-maker:latest
    container_name: backup-maker
    restart: unless-stopped
    environment:
      BACKUP_SCHEDULE: "0 4 * * *"  # 4 AM (after Dockstash)
      S3_ENDPOINT: ${S3_ENDPOINT:-https://s3.us-east-005.backblazeb2.com}
      S3_BUCKET: ${B2_BUCKET_NAME}
      S3_ACCESS_KEY: ${B2_ACCOUNT_ID}
      S3_SECRET_KEY: ${B2_ACCOUNT_KEY}
      S3_REGION: ${S3_REGION:-us-east-005}
      BACKUP_RETENTION_DAYS: "30"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./backup-maker:/config
```

### Fortified Config

Create `backups/fortified/fortified.yml`:

```yaml
# fortified.yml — Stack-aware backup definitions
# Each stack gets its own backup definition with pre/post hooks

stacks:
  immich:
    compose_file: /opt/immich/docker-compose.yml
    schedule: "0 2 * * *"  # 2 AM daily
    retention:
      daily: 7
      weekly: 4
      monthly: 3
    volumes:
      - name: immich_uploads
        path: /backups/immich/uploads
      - name: immich_postgres
        pre_hook: "docker exec immich_postgres pg_dump -U postgres immich > /tmp/immich_db.sql"
        post_hook: "rm /tmp/immich_db.sql"
    notifications:
      discord_webhook: ${DISCORD_WEBHOOK_URL:-}

  vaultwarden:
    compose_file: /opt/vaultwarden/docker-compose.yml
    schedule: "0 2 * * *"
    retention:
      daily: 14
      weekly: 8
      monthly: 6
    volumes:
      - name: vaultwarden_data

  homeassistant:
    compose_file: /opt/homeassistant/docker-compose.yml
    schedule: "0 3 * * *"
    retention:
      daily: 7
      weekly: 4
      monthly: 3
    volumes:
      - name: homeassistant_config
      - name: homeassistant_mariadb
        pre_hook: "docker exec homeassistant_db mariadb-dump -u root -p${MARIADB_ROOT_PASSWORD} --all-databases > /tmp/ha_db.sql"
        post_hook: "rm /tmp/ha_db.sql"
```

### The .env File

Create `backups/.env`:

```bash
# Generate with: openssl rand -base64 32
RESTIC_PASSWORD=your-generated-password-here

# Backblaze B2 credentials (get from B2 dashboard)
B2_ACCOUNT_ID=your-b2-account-id
B2_ACCOUNT_KEY=your-b2-application-key
B2_BUCKET_NAME=your-bucket-name

# Optional: Healthchecks.io for monitoring
HEALTHCHECK_URL=https://hc-ping.com/your-uuid-here

# Optional: Discord webhook for Fortified notifications
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook

# Timezone
TZ=America/New_York
```

---

## The 15-Minute Walkthrough

### Minute 1-3: Create Your Backblaze B2 Bucket

1. Go to [backblaze.com](https://www.backblaze.com/) and create an account (free tier gives you 10GB)
2. Create a new **Bucket** — name it something like `docker-backups`
3. Go to **App Keys** and create a new key with read/write access to that bucket
4. Copy the `keyID` and `applicationKey` — you'll need them for the `.env` file

**Cost:** Backblaze B2 is $6/TB/month for storage. Most homelab backups are 10-50GB after deduplication, so you're looking at $0.06-$0.30/month. Downloads are $0.01/GB (you only pay this during a restore).

### Minute 3-5: Mount Your External Drive

```bash
# Plug in your external drive and find it
lsblk

# Assuming it's /dev/sdb1, mount it
sudo mkdir -p /mnt/backup-drive
sudo mount /dev/sdb1 /mnt/backup-drive

# Add to /etc/fstab for auto-mount on boot
echo "UUID=$(sudo blkid -s UUID -o value /dev/sdb1) /mnt/backup-drive ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
```

### Minute 5-8: Initialize Restic Repositories

```bash
cd ~/backups

# Source your .env file
set -a && source .env && set +a

# Initialize local repository
restic init --repo /mnt/backup-drive/docker-backups

# Initialize remote (B2) repository
restic init --repo b2:${B2_BUCKET_NAME}:/docker-backups
```

### Minute 8-12: Start the Backup Stack

```bash
cd ~/backups
docker compose up -d
```

Check that everything is running:

```bash
docker compose logs -f
```

### Minute 12-15: Run Your First Backup and Verify

```bash
# Trigger an immediate backup with Dockstash
docker exec dockstash backup-now

# Check the snapshots
docker exec dockstash restic snapshots --repo /backups/local
docker exec dockstash restic snapshots --repo b2:${B2_BUCKET_NAME}:/docker-backups

# Verify integrity
docker exec dockstash restic check --repo /backups/local
```

That's it. You now have encrypted, deduplicated backups running daily to both a local drive and Backblaze B2.

---

## Restoring: The Part Everyone Forgets to Test

A backup you haven't tested is not a backup. Here's how to restore:

### Restore a Single Volume

```bash
# List available snapshots
docker exec dockstash restic snapshots --repo /backups/local

# Restore the latest snapshot of a specific volume
docker exec dockstash restic restore latest \
  --repo /backups/local \
  --target /tmp/restore \
  --path /volumes/immich_uploads
```

### Restore Everything (Disaster Recovery)

```bash
# On a fresh server, install Docker and Restic
# Clone your backups repo
git clone your-dotfiles-repo
cd backups

# Restore from B2 (no local drive needed)
export RESTIC_PASSWORD="your-password"
export B2_ACCOUNT_ID="your-id"
export B2_ACCOUNT_KEY="your-key"

restic restore latest \
  --repo b2:your-bucket:/docker-backups \
  --target /tmp/full-restore

# Rebuild your stacks
cd /opt/immich && docker compose up -d
cd /opt/vaultwarden && docker compose up -d
# ... etc
```

### Test Your Restore Monthly

Add this to your crontab:

```bash
# Monthly restore test: restore a random volume and verify it's not corrupted
0 5 1 * * /opt/backups/scripts/test-restore.sh
```

The test script:

```bash
#!/bin/bash
# test-restore.sh — Monthly restore verification
set -e

RESTORE_DIR=$(mktemp -d)
RANDOM_VOLUME="immich_uploads"  # Pick a critical volume

echo "Testing restore of $RANDOM_VOLUME..."
restic restore latest \
  --repo /mnt/backup-drive/docker-backups \
  --target "$RESTORE_DIR" \
  --path "/volumes/$RANDOM_VOLUME"

# Verify the restore has actual files
FILE_COUNT=$(find "$RESTORE_DIR" -type f | wc -l)
if [ "$FILE_COUNT" -gt 0 ]; then
  echo "✅ Restore test passed: $FILE_COUNT files restored"
else
  echo "❌ Restore test FAILED: no files found"
  exit 1
fi

rm -rf "$RESTORE_DIR"
```

---

## Which Tool Should You Actually Use?

You don't need all three. Here's how to choose:

| Your Situation | Use |
|----------------|-----|
| **I want the gold standard** | Dockstash (Restic wrapper) + Backblaze B2 |
| **I have complex stacks with databases** | Fortified (stack-aware, pre/post hooks) |
| **I want dead-simple, no learning curve** | backup-maker (tar + S3) |
| **I want maximum control** | Restic directly with your own scripts |
| **I want everything** | Dockstash for volume backups + Fortified for stack orchestration |

**My recommendation for 90% of homelabbers:** Start with Dockstash. It's the sweet spot — Restic's power with Docker's simplicity. Add Fortified later if you need stack-aware restores with database hooks.

---

## Advanced: What the Pros Do

Once you have the basics running, here's what to add:

### 1. Pre-backup Database Dumps

Never back up a running database volume directly. Always dump first:

```yaml
# In your Dockstash config or Fortified stack definition
pre_hook: |
  docker exec postgres pg_dumpall -U postgres > /tmp/full_dump.sql
  docker exec mariadb mariadb-dump -u root -p${MYSQL_ROOT_PASSWORD} --all-databases > /tmp/mysql_dump.sql
```

### 2. Append-Only Backups (Ransomware Protection)

Restic supports append-only mode on S3-compatible storage. This means even if an attacker compromises your server, they can't delete your existing backups:

```bash
# When initializing the B2 repo, use append-only credentials
# Create a B2 app key with write-only permissions (no delete)
restic init --repo b2:${B2_BUCKET_NAME}:/docker-backups-append

# Use a separate key for pruning (run manually from a secure machine)
```

### 3. Healthchecks.io Integration

Add a healthcheck ping so you know if backups stop running:

```yaml
environment:
  HEALTHCHECK_URL: https://hc-ping.com/your-uuid
```

If the backup doesn't complete, Healthchecks.io emails you. Free tier covers 20 checks.

### 4. Off-Site Rotation

Don't put all your off-site eggs in one basket. Add a second cloud provider:

```bash
# Weekly backup to rsync.net (they support Restic natively)
0 2 * * 0 restic backup /var/lib/docker/volumes --repo sftp:rsync.net:docker-backups
```

### 5. Immutable Snapshots (ZFS/Btrfs)

If your Docker host uses ZFS or Btrfs, take a filesystem snapshot before the backup runs. This gives you a consistent point-in-time even if containers are writing during the backup:

```bash
# ZFS snapshot before backup
zfs snapshot tank/docker@backup-$(date +%Y%m%d-%H%M)
# Run backup from the snapshot
restic backup /tank/docker/.zfs/snapshot/backup-* --repo /mnt/backup-drive/docker-backups
# Clean up old snapshots
zfs destroy tank/docker@backup-$(date -d '7 days ago' +%Y%m%d)-*
```

---

## Common Mistakes (I've Made Them All)

### 1. Backing Up /var/lib/docker Directly

Don't do this. Docker's internal storage format is not designed for file-level backup. Back up **named volumes** or **bind mounts** — not the Docker internals.

### 2. Not Testing Restores

I went six months without testing my restores. When I finally needed one, the backup was corrupted. Test monthly.

### 3. Storing Backup Credentials in docker-compose.yml

Use `.env` files and **never commit them to git**. Add `.env` to your `.gitignore`.

### 4. Forgetting Database Dumps

A volume backup of a running PostgreSQL data directory is likely corrupted. Always use `pg_dump` or `mariadb-dump` before backing up.

### 5. No Retention Policy

Without `--keep-daily`, `--keep-weekly`, etc., your backup repo grows forever. Set a retention policy and prune regularly.

### 6. Single Point of Failure

If your backup script, your Docker host, and your backup drive are all in the same physical machine, you don't have a backup — you have a copy. The 3-2-1 rule exists for a reason.

---

## The Complete Checklist

Print this. Tape it to your server. Or save it in your notes app. Just don't skip it.

- [ ] External drive mounted at `/mnt/backup-drive`
- [ ] Backblaze B2 bucket created and credentials saved
- [ ] `RESTIC_PASSWORD` generated and stored in password manager
- [ ] Local Restic repo initialized
- [ ] Remote Restic repo initialized
- [ ] Dockstash (or Fortified) running with daily schedule
- [ ] Pre-backup database dumps configured for PostgreSQL/MariaDB stacks
- [ ] Retention policy set (7 daily, 4 weekly, 6 monthly, 2 yearly)
- [ ] Healthchecks.io monitoring configured
- [ ] `.env` file in `.gitignore`
- [ ] First backup completed and verified
- [ ] Test restore performed and confirmed working
- [ ] Monthly restore test scheduled in crontab
- [ ] Backup credentials stored in password manager (not just `.env`)
- [ ] Off-site backup confirmed (check B2 dashboard for objects)

---

## What This Costs

| Item | Cost |
|------|------|
| External HDD (2TB) | ~$60 (one-time) |
| Backblaze B2 (50GB) | ~$0.30/month |
| Healthchecks.io | Free (20 checks) |
| **Total** | **$60 one-time + $0.30/month** |

That's less than a single month of Google One 2TB. And you own your data.

---

## Further Reading

- [Restic Documentation](https://restic.readthedocs.io/) — The definitive reference
- [Dockstash GitHub](https://github.com/shyim/dockstash) — Docker-native Restic wrapper
- [Fortified GitHub](https://github.com/dadatuputi/fortified) — Stack-aware backup orchestrator
- [backup-maker GitHub](https://github.com/niclasrst/backup-maker) — Simple tar + S3 backups
- [Backblaze B2 + Restic Guide](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html#backblaze-b2) — Official setup guide
- [r/selfhosted Backup Threads](https://reddit.com/r/selfhosted/search?q=backup+docker+volumes) — See what others are doing

---

*Last updated: August 14, 2026. Tools and versions change — check the linked repos for the latest.*
