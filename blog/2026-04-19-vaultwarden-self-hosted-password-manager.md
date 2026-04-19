---
layout: post.njk
title: "Self-Hosted Password Management with Vaultwarden"
date: 2026-04-19
description: "A complete guide to running Vaultwarden — the lightweight Bitwarden alternative — in your homelab. Family passwords, secure sharing, and zero subscription fees."
tags: ["vaultwarden", "bitwarden", "password-manager", "security", "self-hosted", "homelab", "docker", "proxmox"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/vaultwarden-self-hosted-password-manager"
---

When 1Password announced their price hike in early 2026, a 128-upvote thread on r/selfhosted lit up with the same question: "What's the alternative?" The answer, for anyone with a homelab, is Vaultwarden — a Rust reimplementation of Bitwarden that runs on a fraction of the resources and doesn't charge per family member.

I've been running Vaultwarden for two years. It stores 400+ passwords, handles TOTP codes, manages secure notes, and syncs across five family devices. Total cost: $0. This guide covers the full setup — Docker deployment, reverse proxy configuration, family organization, and mobile app integration.

## What Is Vaultwarden?

Vaultwarden is an unofficial Bitwarden server implementation written in Rust. It's API-compatible with Bitwarden, meaning the official clients (iOS, Android, browser extensions, desktop apps) all work seamlessly.

**Why not just use Bitwarden?**

| Feature | Bitwarden Cloud | Vaultwarden Self-Hosted |
|---------|----------------|------------------------|
| **Cost** | $10-40/year | Free |
| **Family members** | 6 max on family plan | Unlimited |
| **Attachments** | 1GB limit | As much storage as you give it |
| **2FA (TOTP)** | Premium feature | Included |
| **Emergency access** | Premium feature | Included |
| **Server resources** | N/A (they host) | ~100MB RAM |

The tradeoff: you manage the server. For homelab operators, that's not a tradeoff — that's Tuesday.

## Prerequisites

- A server running Docker (or Docker Compose)
- A reverse proxy with HTTPS (Nginx Proxy Manager, Traefik, or Caddy)
- A domain or subdomain pointed at your server
- 10 minutes

## Step 1: Deploy Vaultwarden

Vaultwarden runs as a single container with SQLite by default. No separate database required.

```yaml
# docker-compose.yml
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=true
      - ADMIN_TOKEN=${ADMIN_TOKEN}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_FROM=${SMTP_FROM}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_SECURITY=${SMTP_SECURITY}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./vw-data:/data
    ports:
      - "80:80"
      - "3012:3012"  # Websocket for live sync
```

Create a `.env` file:

```bash
ADMIN_TOKEN=$(openssl rand -base64 48)
SMTP_HOST=smtp.gmail.com
SMTP_FROM=vaultwarden@yourdomain.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Notes:**
- `ADMIN_TOKEN` enables the admin panel at `/admin`
- `SIGNUPS_ALLOWED=true` lets you create accounts. Set to `false` after setup.
- SMTP is optional but recommended for email verification and notifications

Start the container:

```bash
docker compose up -d
```

## Step 2: Reverse Proxy Configuration

Vaultwarden requires HTTPS. The WebSocket connection for live sync also needs proper forwarding.

### Nginx Proxy Manager

1. Add a proxy host for `vaultwarden.yourdomain.com`
2. Forward to `http://vaultwarden:80`
3. Enable **Websocket Support**
4. Request an SSL certificate

### Traefik

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.vaultwarden.rule=Host(`vaultwarden.yourdomain.com`)"
  - "traefik.http.routers.vaultwarden.tls.certresolver=letsencrypt"
  - "traefik.http.services.vaultwarden.loadbalancer.server.port=80"
  - "traefik.http.routers.vaultwarden.service=vaultwarden"
  
  # WebSocket support
  - "traefik.http.routers.vaultwarden-ws.rule=Host(`vaultwarden.yourdomain.com`) && Path(`/notifications/hub`)"
  - "traefik.http.routers.vaultwarden-ws.tls.certresolver=letsencrypt"
  - "traefik.http.routers.vaultwarden-ws.service=vaultwarden-ws"
  - "traefik.http.services.vaultwarden-ws.loadbalancer.server.port=3012"
```

### Caddy

```
vaultwarden.yourdomain.com {
    reverse_proxy localhost:80
    
    # WebSocket for live sync
    @ws {
        path /notifications/hub
    }
    reverse_proxy @ws localhost:3012
}
```

## Step 3: Initial Setup

1. Visit `https://vaultwarden.yourdomain.com`
2. Click **Create account**
3. Use a strong master password — this is the only password you'll need to remember

**Critical:** Your master password cannot be recovered. If you forget it, your vault is permanently inaccessible. Store it in a physical safe or password manager escrow.

## Step 4: Admin Panel Configuration

Access the admin panel at `https://vaultwarden.yourdomain.com/admin` using your `ADMIN_TOKEN`.

**Recommended settings:**

- **General Settings:**
  - Disable signups after creating your accounts
  - Set `INVITATIONS_ALLOWED=true` to invite family members manually
  - Enable `SHOW_PASSWORD_HINT=false` for security

- **SMTP Settings:**
  - Verify email verification is enabled
  - Test with the "Send test email" button

- **Security:**
  - Set `KDF_ITERATIONS=600000` (OWASP recommended minimum)
  - Enable `REQUIRE_EMAIL_2FA=true` for admin accounts

## Step 5: Family Organization Setup

Vaultwarden supports organizations for secure password sharing.

### Creating a Family Organization

1. In the web vault, click **New Organization**
2. Name it "Family" or similar
3. Choose the free plan (all features are unlocked in Vaultwarden)

### Collections and Access Control

Collections are folders within an organization. Create collections like:

- **Home** — WiFi, smart home accounts, utilities
- **Finance** — Banking, investment, tax software
- **Shared** — Netflix, Spotify, Amazon
- **Emergency** — Insurance, medical, estate documents

**Access levels:**
- **Owner:** Full control, can delete organization
- **Admin:** Manage users and collections
- **User:** Access assigned collections
- **Manager:** Manage users within specific collections

### Inviting Family Members

1. Go to **Organization → People → Invite**
2. Enter their email
3. Assign to appropriate collections
4. They'll receive an email to join

## Step 6: Client Setup

### iOS / Android

1. Download the official Bitwarden app
2. Tap **Settings → Self-hosted Environment**
3. Enter `https://vaultwarden.yourdomain.com`
4. Log in with your credentials

### Browser Extensions

1. Install the Bitwarden extension
2. Click **Settings → Self-hosted Environment**
3. Set server URL
4. Log in

### Desktop Apps

Same process — all official Bitwarden clients support self-hosted instances.

## Step 7: Migrating from Another Password Manager

### From 1Password

1. In 1Password, go to **File → Export → All Items**
2. Choose `.1pif` or `.csv` format
3. In Vaultwarden web vault: **Tools → Import Data**
4. Select 1Password format and upload

### From Bitwarden Cloud

1. Bitwarden web vault: **Tools → Export Vault**
2. Choose `.json` (encrypted) or `.csv`
3. Vaultwarden: **Tools → Import Data → Bitwarden**

### From Chrome / Edge

1. Chrome: **Settings → Passwords → Export passwords**
2. Vaultwarden: Import as Chrome CSV

## Advanced: Security Hardening

### Fail2Ban

Protect against brute force attempts:

```ini
# /etc/fail2ban/jail.d/vaultwarden.conf
[vaultwarden]
enabled = true
port = http,https
filter = vaultwarden
logpath = /path/to/vw-data/vaultwarden.log
maxretry = 5
bantime = 3600
```

```ini
# /etc/fail2ban/filter.d/vaultwarden.conf
[Definition]
failregex = ^.*Username or password is incorrect\. Try again\. IP: <ADDR>.*$
ignoreregex =
```

### Backup Strategy

Your password vault is critical infrastructure. Back it up:

```bash
#!/bin/bash
# /opt/backup-vaultwarden.sh

BACKUP_DIR="/backups/vaultwarden"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop container for consistent backup
docker stop vaultwarden

# Backup data directory
tar -czf "$BACKUP_DIR/vaultwarden_$DATE.tar.gz" /path/to/vw-data

# Restart container
docker start vaultwarden

# Keep only last 30 days
find "$BACKUP_DIR" -name "vaultwarden_*.tar.gz" -mtime +30 -delete
```

Add to crontab for daily backups:

```bash
0 2 * * * /opt/backup-vaultwarden.sh
```

### Offsite Backup with Rclone

```bash
# Sync to S3-compatible storage
rclone sync /backups/vaultwarden remote:password-backups
```

## Troubleshooting

### "Websocket connection failed"

Check your reverse proxy WebSocket configuration. The client needs access to `/notifications/hub` on port 3012.

### "SMTP test failed"

- Gmail requires an App Password, not your regular password
- Check firewall rules for outbound port 587
- Verify `SMTP_FROM` matches the authenticated user

### Slow sync on mobile

- Enable WebSocket support in your reverse proxy
- Check that `WEBSOCKET_ENABLED=true` is set
- Verify mobile client is set to your self-hosted URL

### Forgot master password

There is no recovery. This is by design. Export your vault regularly as a backup.

## When to Use Bitwarden Cloud Instead

Consider Bitwarden's official service if:

- You don't want to manage a server
- You need guaranteed 99.99% uptime
- You want official support
- Compliance requirements mandate SOC2/ISO27001

For personal and family use, Vaultwarden provides the same security with more control.

## Conclusion

Vaultwarden turns your homelab into a secure password management platform. For the cost of a few hundred megabytes of RAM, you get unlimited family members, unlimited attachments, and full control over your most sensitive data.

The 30 minutes you spend setting it up pays for itself in the first month of not paying subscription fees. And when the next password manager price hike hits, you'll be glad you made the switch.

**Resources:**
- [Vaultwarden GitHub](https://github.com/dani-garcia/vaultwarden)
- [Bitwarden Client Downloads](https://bitwarden.com/download/)
- [Vaultwarden Wiki](https://github.com/dani-garcia/vaultwarden/wiki)

---

*Running Vaultwarden in your homelab? Have a clever backup or integration setup? Share it in the [Discord](https://discord.gg/selfhosted) — always curious how people are securing their digital lives.*
