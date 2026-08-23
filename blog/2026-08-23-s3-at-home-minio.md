---
layout: post.njk
title: "S3 at Home: Self-Hosted Object Storage with MinIO — One Bucket for Every App That Wants One"
date: 2026-08-23
description: "Healthchecks.io's self-hosted object storage hit 195 points on HN this week, and it exposed a pattern hiding in plain sight: your homelab already has three apps begging for an S3 bucket — Restic, Immich, and your Docker backup stack. Instead of paying AWS or Backblaze for each one, run MinIO once and serve them all. Here's the copy-paste setup."
tags: ["minio", "s3", "object-storage", "self-hosted", "homelab", "restic", "immich", "backup", "docker", "storage", "devops"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-23-s3-at-home-minio"
---

# S3 at Home: Self-Hosted Object Storage with MinIO

Here's a pattern I keep tripping over in my own homelab, and I suspect you have too.

Every time I set up a new self-hosted app, the same line shows up in its config: **"S3-compatible storage (optional)."** Restic wants a bucket for off-site backups. Immich wants a bucket for photo storage. My Docker backup stack wants a bucket for encrypted snapshots. Healthchecks.io — which just hit the front page of Hacker News at 195 points for its self-hosted object storage — wants a bucket for its check data.

Three, four, five apps. All asking for the same thing. And the default answer everyone reaches for is to open a Backblaze B2 account, or spin up an AWS S3 bucket, and pay a few dollars a month *per app* for storage that's sitting on someone else's hardware.

But you already own the hardware. You already run Docker. The thing all these apps are asking for is just an **S3-compatible API** — and there's a single service that gives you one, for free, on your own box.

It's called [MinIO](https://min.io), and this post is the copy-paste guide to running it once and pointing every bucket-hungry app in your homelab at it.

---

## Why This Matters (The "Three Apps, One Bucket" Problem)

Let me make the case concretely, because "object storage" sounds abstract until you see the list.

Here are the apps in a typical homelab that want an S3 bucket, and what they'd do with it:

| App | What It Wants the Bucket For | What You'd Otherwise Pay |
|-----|------------------------------|--------------------------|
| **Restic** | Encrypted, deduplicated off-site backups | Backblaze B2 (~$6/TB/month) |
| **Immich** | Photo/video object storage, offloading from local disk | Cloud storage or a bigger disk |
| **Docker backup stack** (Dockstash, Fortified, backup-maker) | Encrypted volume snapshots | B2 or S3, again |
| **Healthchecks.io** (self-hosted) | Check history and ping data | Its own storage backend |
| **Nextcloud / ownCloud** | Primary or external storage backend | Local disk or S3 |
| **Anything with an "S3 endpoint" field** | Literally any S3-compatible app | Per-app cloud bills |

The point isn't that any single one of these is expensive. It's that they're **all asking for the same primitive**, and you're paying for it three or four times over — or worse, skipping the feature entirely because "I don't want to set up cloud storage."

MinIO collapses all of that into one service. You run it once, you create a bucket per app, and every app that speaks S3 now has somewhere to write. No per-app cloud accounts. No egress fees. No "your data lives on someone else's disk" asterisk.

And because MinIO speaks the **actual S3 API** — not a lookalike — anything that works with AWS S3 works with it unchanged. That's the whole trick.

---

## What MinIO Actually Is

MinIO is a high-performance, S3-compatible object storage server. It's the de facto standard for self-hosted S3, and it's what a huge chunk of the "S3-compatible" ecosystem is actually tested against.

The key facts:

- **It's a single Go binary** (or a Docker container) — no external database, no ZooKeeper, no cluster required for a single node.
- **It speaks the real S3 API**, including multipart uploads, versioning, lifecycle rules, and IAM-style access keys.
- **It stores objects as plain files on disk** — your data is just files in a directory, not a proprietary blob format. If MinIO dies tomorrow, your data is still readable.
- **It has a web console** for browsing buckets, uploading files, and managing access keys.
- **It's free and open source** (AGPLv3), with a paid enterprise tier for large-scale clusters.

For a homelab, you want the single-node, single-disk mode. It's the simplest possible deployment and it's more than enough for backups, photos, and app data.

---

## The Copy-Paste Setup (Docker Compose)

Here's the whole thing. One `docker-compose.yml`, one `.env`, and you're running S3 on your own hardware.

### 1. Create the directory and `.env`

```bash
mkdir -p ~/minio && cd ~/minio
cat > .env <<'EOF'
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=change-this-to-something-long
MINIO_DATA_DIR=./data
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
EOF
```

**Change the password.** The default `minioadmin/minioadmin` is the first thing anyone scanning your network will try. Generate something long — a password manager is your friend here.

### 2. The `docker-compose.yml`

```yaml
services:
  minio:
    image: minio/minio:latest
    container_name: minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    ports:
      - "${MINIO_PORT}:9000"        # S3 API
      - "${MINIO_CONSOLE_PORT}:9001" # Web console
    volumes:
      - ${MINIO_DATA_DIR}:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 30s
      timeout: 5s
      retries: 3
```

### 3. Bring it up

```bash
docker compose up -d
```

That's it. You now have:

- **S3 API** at `http://your-server:9000`
- **Web console** at `http://your-server:9001`

Log into the console with your root user/password, and you'll see a clean dashboard ready for buckets.

---

## Creating Buckets and Access Keys (The Part Everyone Skips)

Here's where most guides fall short. They get MinIO running and then leave you staring at the console wondering how to actually *use* it.

The pattern is: **one bucket per app, one access key per app.** Don't share a single key across everything — if one app leaks its key, you want to be able to revoke just that one.

### Option A: The Web Console

1. Log into `http://your-server:9001`.
2. Go to **Buckets** → **Create Bucket** → name it (e.g. `restic`, `immich`, `docker-backups`).
3. Go to **Access Keys** → **Create Access Key** → copy the `Access Key` and `Secret Key`.

### Option B: The `mc` CLI (scriptable, my preference)

The `mc` (MinIO Client) tool is the fastest way to do this from the command line, and it's worth installing:

```bash
# Install mc (macOS via Homebrew)
brew install minio/stable/mc

# Or download the binary directly
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc && sudo mv mc /usr/local/bin/

# Point mc at your server
mc alias set local http://your-server:9000 minioadmin 'change-this-to-something-long'

# Create buckets
mc mb local/restic
mc mb local/immich
mc mb local/docker-backups

# Create an access key for restic
mc admin user add local restic-user 'a-long-random-password'
mc admin policy attach local readwrite --user restic-user
```

Now you have a `restic-user` with read/write access, and a `restic` bucket. Repeat for each app.

---

## Wiring Up the Three Apps That Started This

Now the payoff. Here's how to point the three apps from the intro at your new MinIO instance.

### 1. Restic → MinIO

Restic has first-class S3 support. Point it at your MinIO endpoint:

```bash
export AWS_ACCESS_KEY_ID=restic-user
export AWS_SECRET_ACCESS_KEY=a-long-random-password
export RESTIC_PASSWORD=your-restic-repo-password

# Initialize the repo (once)
restic -r s3:http://your-server:9000/restic init

# Back up
restic -r s3:http://your-server:9000/restic backup /path/to/data
```

The `s3:http://` prefix tells Restic to use plain HTTP (fine on your LAN) instead of HTTPS. If you've put MinIO behind a reverse proxy with TLS, use `s3:https://` instead.

### 2. Immich → MinIO

Immich supports S3 as a storage backend. In your Immich `.env`:

```env
# Point Immich's storage at MinIO
IMMICH_STORAGE=s3
S3_ENDPOINT=http://your-server:9000
S3_ACCESS_KEY=immich-user
S3_SECRET_KEY=another-long-password
S3_BUCKET=immich
S3_REGION=us-east-1
S3_FORCE_PATH_STYLE=true
```

The `S3_FORCE_PATH_STYLE=true` is the important one — MinIO uses path-style addressing, not virtual-host style, and most S3 clients need this flag to talk to it correctly.

### 3. Docker backup stack (Dockstash / Fortified / backup-maker) → MinIO

These tools all accept an S3 endpoint. For Dockstash, it's the same Restic-style env vars:

```env
RESTIC_REPOSITORY=s3:http://your-server:9000/docker-backups
AWS_ACCESS_KEY_ID=docker-backups-user
AWS_SECRET_ACCESS_KEY=yet-another-password
RESTIC_PASSWORD=your-repo-password
```

For backup-maker (the simple tar + S3 tool), it's:

```env
S3_ENDPOINT=http://your-server:9000
S3_BUCKET=docker-backups
S3_ACCESS_KEY=docker-backups-user
S3_SECRET_KEY=yet-another-password
S3_FORCE_PATH_STYLE=true
```

The pattern is identical across all of them: **endpoint + access key + secret key + bucket + force-path-style.** Once you've done it once, you can do it for any S3-compatible app in about 30 seconds.

---

## The "But What About Off-Site?" Objection

This is the question you should be asking, so let me answer it before you do.

**"If MinIO runs on the same server as everything else, isn't that just a fancy local disk? What happens when the server dies?"**

Yes — and that's exactly the right instinct. MinIO on a single node is **not** a backup by itself. It's a *storage target*. The 3-2-1 rule still applies.

Here's how I think about it:

1. **MinIO is the "2" in 3-2-1** — a second copy of your data, on a different disk (or a different machine) than the primary. It's your on-site redundancy.
2. **Your off-site copy is still separate.** Restic pointed at MinIO is great for *fast, local, deduplicated* backups. But you should still have a second Restic repo pointed at Backblaze B2 or rsync.net for the true off-site copy.

The beauty of the setup is that **Restic doesn't care where the repo lives.** You can have one repo on MinIO (fast, local, free) and one on B2 (slow, off-site, cheap) and run the same `restic backup` command against both. MinIO doesn't replace your off-site backup — it makes the *on-site* part of 3-2-1 free and fast.

If you want MinIO itself to be redundant, you can run it in distributed mode across multiple nodes — but for a homelab, the simpler answer is: **run MinIO on a different physical machine than your primary data**, or at least on a different disk, and keep your off-site copy separate.

---

## Performance Notes (Why MinIO Is Fast)

One thing that surprises people: MinIO is *fast*. Like, genuinely fast. It's written in Go, it's designed for high-throughput object workloads, and on a single NVMe disk it'll saturate a gigabit LAN without breaking a sweat.

A few things that matter for a homelab:

- **Use a dedicated disk or directory.** Don't point MinIO at a spinning USB drive and expect miracles. An NVMe or a decent SATA SSD is the sweet spot.
- **Erasure coding is for clusters.** In single-node mode, MinIO just writes files. Don't overthink it.
- **Versioning and lifecycle rules are built in.** If you want MinIO to auto-expire old backups, set a lifecycle rule on the bucket — it's a checkbox in the console.

For backups specifically, the deduplication happens in Restic, not MinIO — so MinIO is just a fast, dumb object store, which is exactly what you want.

---

## Security Checklist (Don't Skip This)

MinIO is a network service that holds your data. Treat it like one.

- [ ] **Change the root password** from `minioadmin/minioadmin` (the #1 mistake)
- [ ] **Don't expose port 9000/9001 to the internet** — keep it on your LAN, or put it behind a reverse proxy with TLS and auth
- [ ] **One access key per app**, never share keys
- [ ] **Use `S3_FORCE_PATH_STYLE=true`** on clients (avoids a whole class of DNS/endpoint bugs)
- [ ] **Enable bucket versioning** on anything you'd be sad to lose
- [ ] **Set lifecycle rules** to expire old objects so your disk doesn't fill up
- [ ] **Back up the MinIO data directory itself** — it's just files, so your existing backup tool can grab it
- [ ] **Put MinIO on a different disk/machine** than your primary data if you want real redundancy

---

## What This Costs

| Item | Cost |
|------|------|
| MinIO (software) | Free (AGPLv3) |
| A spare disk or directory | $0 (you already have it) |
| Backblaze B2 for the *off-site* copy | ~$6/TB/month (optional) |
| **Total** | **$0, plus whatever you were already paying for off-site** |

Compare that to paying B2 or S3 for *every* app's bucket, and the savings add up fast — especially once you have three or four apps all wanting storage.

---

## The Bottom Line

Object storage isn't a cloud-only feature anymore. It's a primitive — like a database or a reverse proxy — and your homelab apps are already asking for it. Restic wants a bucket. Immich wants a bucket. Your backup stack wants a bucket. Healthchecks.io wants a bucket.

You can pay for each one, or you can run MinIO once and serve them all.

The setup is a single Docker container, a handful of buckets, and a per-app access key. Once it's running, every "S3-compatible storage (optional)" field in your homelab stops being optional — because you already have the answer.

---

## Further Reading

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html) — The definitive reference
- [MinIO Docker Quickstart](https://min.io/docs/minio/container/index.html) — Official container guide
- [Restic S3 Backend](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html#amazon-s3) — Restic's S3 setup (works with MinIO)
- [Immich S3 Storage](https://immich.app/docs/administration/remote-storage) — Immich's remote storage docs
- [Healthchecks.io Self-Hosted](https://healthchecks.io/docs/self_hosted/) — The HN post that sparked this
- [mc (MinIO Client)](https://min.io/docs/minio/linux/reference/minio-mc.html) — The CLI for scripting buckets and keys

---

*Last updated: August 23, 2026. Tools and versions change — check the linked repos for the latest.*
