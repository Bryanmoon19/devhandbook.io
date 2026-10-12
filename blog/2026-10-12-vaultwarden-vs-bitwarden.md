---
layout: post.njk
title: "Vaultwarden vs Bitwarden: Which Self-Hosted Password Manager Should You Run?"
date: 2026-10-12
description: "A practical comparison of the official Bitwarden self-hosted stack and the lean Rust Vaultwarden rewrite — feature parity, resource footprint, setup, migration, and backup. Plus where Bitwarden's new dual-license model tips the scales."
tags: ["vaultwarden", "bitwarden", "password-manager", "self-hosted", "homelab", "security", "docker", "sqlite", "2fa", "privacy"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-12-vaultwarden-vs-bitwarden/"
affiliate: false
cta: true
---

Let's be honest: trusting every password you've ever created to a cloud service you don't control is... a choice. For the privacy-conscious, the homelab enthusiast, or anyone who's just tired of subscription fatigue, self-hosting a password manager is one of the most empowering moves you can make.

> **Note:** This comparison got sharper in October 2026, when Bitwarden announced its app-store builds would move to a dual-license model with future components "evaluated on a case-by-case basis." I wrote a dedicated decision tree for that news — [Bitwarden's Dual-License Change: Should You Migrate to Vaultwarden Now?](/blog/2026-10-11-bitwarden-dual-license-vaultwarden-migration/) — and this guide is the evergreen companion to it.

You get:

- **Full data ownership**: Your vault lives on your hardware, not someone else's server.
- **No subscription fees**: (Well, mostly. We'll get to that.)
- **Custom integrations**: Tie it into your existing infrastructure.
- **Paranoid-level peace of mind**: You're the only one with the keys. Literally.

But which tool do you choose? The official Bitwarden stack is robust, battle-tested, and resource-hungry. Then there's Vaultwarden: a lean, unofficial Rust rewrite that fits on a Raspberry Pi and still talks to the official mobile apps.

This guide breaks down both, shows you how to set them up, and helps you pick the right one for your stack.

---

## What Are Bitwarden and Vaultwarden?

### Bitwarden (Official)

Bitwarden is the open-source password manager you probably already know. The official self-hosted version is called **Bitwarden Unified** or the older **bitwarden/server** deployment. It's a .NET-based monolith (or set of containers) backed by MSSQL, offering every feature the cloud version has.

- **Language**: C# / .NET
- **Database**: Microsoft SQL Server (or Postgres in Unified)
- **Resource footprint**: Heavy. Expect 2GB+ RAM.

### Vaultwarden (Unofficial)

Vaultwarden is a third-party, unofficial Rust implementation of the Bitwarden server API. It's API-compatible, meaning the official Bitwarden apps (desktop, mobile, browser) connect to it seamlessly.

- **Language**: Rust
- **Database**: SQLite (default), MySQL, or PostgreSQL
- **Resource footprint**: Tiny. Runs comfortably on a Pi with 256MB RAM.

> ⚠️ **Disclaimer**: Vaultwarden is not officially supported by Bitwarden. It's community-driven, incredibly popular, and well-maintained—but it's still an unofficial project.

---

## Detailed Comparison

| Feature | Bitwarden (Official) | Vaultwarden |
|---------|---------------------|-------------|
| **Password Vaulting** | ✅ Full feature set | ✅ Full feature set |
| **TOTP (2FA Codes)** | ❌ Paid license only | ✅ Free |
| **Passkeys (FIDO2/WebAuthn)** | ✅ Yes | ✅ Yes (recent versions) |
| **Organizations/Sharing** | ✅ Yes | ✅ Yes |
| **Send (Secure file/text)** | ✅ Yes | ✅ Yes |
| **Emergency Access** | ✅ Yes | ✅ Yes |
| **SSO / Enterprise** | ✅ Full enterprise features | ❌ Not supported |
| **Resource Usage** | 2–4 GB RAM, MSSQL | ~50–150 MB RAM, SQLite |
| **Audit / Security** | SOC 2, third-party audits | Community-reviewed, no formal audit |
| **Cost (Self-Hosted)** | Free (limited) / $3–5/mo license for premium | Completely free |
| **Mobile App Sync** | Official apps | Official apps (API-compatible) |
| **Setup Complexity** | Moderate (Docker Compose) | Very Easy (single container) |

### Performance

If you're running on a homelab server with 32GB of RAM, Bitwarden's footprint won't matter. But if you're squeezing services onto a Raspberry Pi 4 or a low-spec VPS, Vaultwarden is the clear winner. It starts in seconds, uses minimal CPU, and doesn't require a heavy database engine.

### Security

Bitwarden has the edge in formal security posture: SOC 2 compliance, regular third-party penetration tests, and a bug bounty program. Vaultwarden relies on community scrutiny and the inherent safety of Rust's memory model. The cryptography is the same (both use AES-256 and PBKDF2/Argon2), so your vault's encryption is equally strong on both—assuming your server itself is secure.

### Cost

Bitwarden self-hosted is free for basic features, but premium features (TOTP, emergency access, advanced 2FA) require a license starting around $3–4/month. Vaultwarden includes all these features for free, since it's not bound by Bitwarden's licensing.

### License Certainty

Bitwarden's October 2026 dual-license announcement — where *new components may ship only in the commercial build* — is the wildcard. Vaultwarden is AGPLv3 and community-driven, with no corporate roadmap deciding which future feature lands in a paid build. If you care about a predictable, fully-free feature set, that difference matters more than it did a year ago.

---

## Step-by-Step: Vaultwarden Setup with Docker Compose

Vaultwarden is the easiest self-hosted password manager you'll ever deploy.

### Docker Compose File

Create a directory and a `docker-compose.yml`:

```yaml
# ~/docker/vaultwarden/docker-compose.yml
version: "3.8"

services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=false        # set to true temporarily for first account
      - INVITATIONS_ALLOWED=false
      - ADMIN_TOKEN=${ADMIN_TOKEN}   # strong random string for /admin
    volumes:
      - ./vw-data:/data
    ports:
      - "80:80"
      - "3012:3012"  # websocket for live sync
```

### Environment File

Create `.env`:

```bash
# ~/docker/vaultwarden/.env
ADMIN_TOKEN=$(openssl rand -base64 48)
```

### Start It

```bash
cd ~/docker/vaultwarden
docker compose up -d
```

### First Setup

1. Visit `http://your-server-ip`.
2. Create your account. If `SIGNUPS_ALLOWED=false`, temporarily set it to `true`, restart, create your account, then disable it again.
3. Access the admin panel at `http://your-server-ip/admin` with your `ADMIN_TOKEN`.

### Reverse Proxy (Nginx / Nginx Proxy Manager)

Add a proxy host pointing to `http://vaultwarden:80`. Enable websockets support. For HTTPS, add your certificate or use Let's Encrypt.

Example Nginx snippet:

```nginx
location / {
    proxy_pass http://vaultwarden:80;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /notifications/hub {
    proxy_pass http://vaultwarden:3012;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Step-by-Step: Official Bitwarden Self-Hosted Setup

Bitwarden's official server is more involved but gives you the "real thing."

### Prerequisites

- Docker & Docker Compose
- At least 2GB RAM available
- Domain name (for HTTPS)

### Install

Bitwarden provides an installation script:

```bash
curl -Lso bitwarden.sh https://go.btwrdn.co/bw-sh \
  && chmod 700 bitwarden.sh
./bitwarden.sh install
```

The script will prompt you for:

- Domain name (e.g., `bitwarden.yourdomain.com`)
- Let's Encrypt email
- SSL choice (Let's Encrypt or custom)

### Configure

Edit `./bwdata/env/global.override.env`:

```bash
# Required
globalSettings__baseServiceUri__vault=https://bitwarden.yourdomain.com
globalSettings__baseServiceUri__api=https://bitwarden.yourdomain.com/api

# Optional: disable signups after first user
globalSettings__disableUserRegistration=true
```

### Start

```bash
./bitwarden.sh start
```

### Updating

```bash
./bitwarden.sh updateself
./bitwarden.sh update
```

> Note: Bitwarden's MSSQL container alone can use 1–1.5GB RAM at idle. Plan accordingly.

---

## Migration Guide

### Bitwarden Cloud → Vaultwarden (or Self-Hosted Bitwarden)

1. **Export your vault** from the cloud web UI:
   - Settings → Export Vault → Choose `.json` (encrypted) or `.csv` (plaintext—less safe)
2. **Set up your self-hosted instance** (Vaultwarden or Bitwarden).
3. **Import** via the web UI: Tools → Import Data → Select format → Upload file.
4. **Re-enable 2FA** on your new instance and regenerate TOTP codes if needed.
5. **Update all clients** to point to your new server URL.

### Vaultwarden ↔ Official Bitwarden

Since both use the same data format, you can export/import JSON backups freely. If you want to migrate the raw database (Vaultwarden's SQLite to Bitwarden's MSSQL), it's more complex—stick to JSON exports for simplicity.

For a full end-to-end migration walkthrough triggered by the license change, see the [Bitwarden → Vaultwarden decision tree](/blog/2026-10-11-bitwarden-dual-license-vaultwarden-migration/).

---

## Mobile App Setup and Sync

### For Vaultwarden

1. Install the official **Bitwarden** app (iOS / Android).
2. Before logging in, tap the **gear icon** (Settings).
3. Set **Server URL** to your Vaultwarden instance: `https://vault.yourdomain.com`
4. Log in with your self-hosted credentials.
5. Enjoy full sync, autofill, and TOTP generation.

### For Official Bitwarden Self-Hosted

Same process—the official app talks natively to the official server. Just point it at your domain.

---

## Backup Strategies

Your password vault is one of the worst things to lose. Back it up. Now.

### Vaultwarden Backups

The entire state lives in `./vw-data`. Back that up:

```bash
# Daily cron job
rsync -avz ~/docker/vaultwarden/vw-data/ /mnt/backups/vaultwarden/
```

Or, for a database dump:

```bash
docker exec vaultwarden sqlite3 /data/db.sqlite3 ".backup /data/db-backup.sqlite3"
```

### Bitwarden Backups

Back up the `./bwdata` directory. For MSSQL, also dump the database:

```bash
docker exec bitwarden-mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P '$SA_PASSWORD' \
  -Q "BACKUP DATABASE [vault] TO DISK = '/backups/vault.bak'"
```

### General Rules

- **3-2-1 rule**: 3 copies, 2 media types, 1 offsite.
- **Encrypt your backups** if they leave your home.
- **Test restores**. A backup you can't restore is just wishful thinking.

---

## Which One Should You Choose?

| You Should Pick... | If... |
|-------------------|-------|
| **Vaultwarden** | You want a lightweight, free, feature-complete server. You run a Pi or a small VPS. You don't need enterprise SSO. |
| **Official Bitwarden** | You want formal security audits, SOC 2 compliance, or enterprise features. You have the RAM to spare and prefer "officially supported." |

For 95% of homelabbers, **Vaultwarden is the pragmatic choice**. It's fast, free, and fully compatible with the official clients. The only reason to run the official server is compliance, enterprise requirements, or personal preference for the "real thing."

Bitwarden's move toward a dual-license model — with future features potentially gated to the commercial build — only strengthens that default. When the roadmap of your password manager is subject to "case-by-case" licensing decisions, the community-run, AGPL-licensed option starts to look like the safer long-term bet.

---

## Conclusion

Self-hosting your password manager is a rite of passage in the homelab world. Whether you choose the lean efficiency of Vaultwarden or the enterprise pedigree of official Bitwarden, you're taking control of one of the most sensitive pieces of your digital life.

Start with Vaultwarden if you're unsure. It's low-risk, low-resource, and high-reward. You can always migrate later if your needs grow.

Now go forth and stop reusing passwords.

---

*Got questions or a setup tip? Drop them in the comments—or keep them in your password vault, encrypted at rest, on your own hardware, where they belong.*
