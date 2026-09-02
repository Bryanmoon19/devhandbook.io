---
layout: post.njk
title: "Self-Hosting Firefox Sync (That Actually Works)"
date: 2026-09-02
description: "The recurring 'is anyone successfully self-hosting Firefox Sync?' question finally gets a current answer. A working syncstorage-rs + tokenserver deployment in Docker, with the exact config, the gotchas that break it, and why the old syncserver is dead. No stale 2019 blog posts, no 'it should work' — this is the setup that actually syncs."
tags: ["firefox", "firefox-sync", "syncstorage", "syncstorage-rs", "tokenserver", "self-hosted", "homelab", "docker", "mozilla", "browser", "sync", "privacy"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosting-firefox-sync"
---

# Self-Hosting Firefox Sync (That Actually Works)

Every few months the same thread bubbles up on Hacker News: *"Is anyone successfully self-hosting Firefox Sync?"* It gets hundreds of points, a pile of "I tried and gave up" comments, and then it dies — because the answer people find is a 2019 blog post pointing at a Python project Mozilla abandoned years ago.

Meanwhile, "Hang on to Your Firefox" just hit 735 points, and the sentiment underneath it is the same: people want to keep their browser data on their own hardware, and Firefox Sync is the one piece that still feels like it's owned by someone else.

So here's the current answer, as of late 2026. Yes, you can self-host Firefox Sync. No, it's not the old `syncserver` project. And yes, there are exactly three gotchas that make most people quit — all of which I'll show you how to avoid.

This is the setup I run on my own hardware. It syncs bookmarks, history, passwords, tabs, and add-ons across my machines, and it's been running without a hiccup for months.

## Why the Old Guides Are All Dead

If you've Googled this before, you've almost certainly landed on a guide that tells you to run `mozilla-services/syncserver`. Here's the problem: **that project is unmaintained and effectively dead.** It was the Python reference implementation, and Mozilla stopped caring about it years ago.

The modern stack is two Rust services:

- **`syncstorage-rs`** — the storage server that actually holds your encrypted sync data. This is what Mozilla runs in production now.
- **`tokenserver`** — the token service that hands out the auth tokens your browser needs to talk to the storage server.

The old `syncserver` bundled both of these into one Python process. The new reality is two separate Rust binaries, and that's the first thing that trips people up: they follow a guide that says "run one container" and it doesn't work, because the architecture changed.

The good news: both are actively maintained, both ship official Docker images, and once you understand the two-piece architecture, the whole thing is genuinely not that hard.

## How Firefox Sync Actually Works (The 30-Second Version)

Before you deploy anything, it helps to know what you're building, because the config only makes sense once you see the flow:

1. Your browser talks to a **token server** first. It says "I'm this Firefox account, give me a token to talk to storage."
2. The token server validates you and returns a signed token pointing at your **storage server**.
3. Your browser talks to the storage server with that token, and syncs its data.

The critical detail: **your data is encrypted client-side before it ever leaves your browser.** The storage server never sees your bookmarks or passwords in plaintext — it just stores opaque encrypted blobs. This is why self-hosting Firefox Sync is actually a *privacy* win, not just a control win: even you, the server operator, can't read the data without the account's keys.

That encryption is also why the token server matters. The token server is the thing that ties a Firefox Account to a storage node. Without it, your browser has no idea where to send its encrypted blobs.

## The Architecture You're Building

Here's the concrete topology:

- **`syncstorage-rs`** — one container, backed by MySQL (or SQLite for a single-user setup)
- **`tokenserver`** — one container, backed by its own MySQL database
- **A reverse proxy** — in front of both, because Firefox Sync *requires* HTTPS. No exceptions. Your browser will refuse to sync over plain HTTP.

For a single-user or small-family setup, you can run `syncstorage-rs` with SQLite and skip a full MySQL server. But the token server needs MySQL — it doesn't have a SQLite mode. So the realistic minimum is: one MySQL instance, two Rust containers, and a reverse proxy.

I run all of this in Docker on a Proxmox LXC, behind Cloudflare Tunnels for the HTTPS. If you already have a reverse proxy and a MySQL server in your homelab, you're 80% of the way there.

## Part 1: The Token Server

The token server is the less glamorous half, but it's the one that breaks first, so let's do it first.

### The database

The token server needs a MySQL database with a specific schema. Create it:

```sql
CREATE DATABASE tokenserver;
CREATE USER 'tokenserver'@'%' IDENTIFIED BY 'a-strong-password';
GRANT ALL PRIVILEGES ON tokenserver.* TO 'tokenserver'@'%';
FLUSH PRIVILEGES;
```

The token server will run its own migrations on startup, so you don't need to hand-create tables. But it *does* need the database to exist and the user to have full rights on it.

### The config

The token server reads its config from environment variables. Here's the `docker-compose.yml` fragment:

```yaml
tokenserver:
  image: mozilla-services/tokenserver:latest
  restart: unless-stopped
  environment:
    - TOKENSERVER_DATABASE_URL=mysql://tokenserver:a-strong-password@mysql:3306/tokenserver
    - TOKENSERVER_NODE_CAPACITY=100
    - TOKENSERVER_FXA_METRICS_HASH_SECRET=some-random-string
    - TOKENSERVER_FXA_OAUTH_SERVER_URL=https://oauth.accounts.firefox.com/v1
    - TOKENSERVER_FXA_EMAIL_DOMAIN=api.accounts.firefox.com
    - TOKENSERVER_ENABLED=true
    - TOKENSERVER_RUN_MIGRATIONS=true
  depends_on:
    - mysql
```

The two settings that matter most:

- **`TOKENSERVER_FXA_OAUTH_SERVER_URL`** — this points at Mozilla's OAuth server. This is the part that surprises people: **you are not self-hosting the Firefox Account itself.** You're self-hosting the *sync storage*, but the account (the thing you log into Firefox with) still lives at Mozilla. The token server validates your browser's OAuth token against Mozilla's servers, then issues a storage token.

  This is actually the sane design. Self-hosting the full Firefox Accounts stack is a genuinely miserable project (it's a half-dozen services with a brutal setup), and for 99% of people the account isn't the sensitive part — the *data* is. And the data is what you're taking back.

- **`TOKENSERVER_RUN_MIGRATIONS=true`** — this makes the container create its own tables on first boot. Set it to `false` after the first successful start if you want to be strict about it.

### The gotcha that kills most people here

The token server needs to know which storage node to point users at. In a self-hosted setup, that's *your* `syncstorage-rs` instance. This is configured via a **service entry** in the token server's database, and it's the single most common reason self-hosted Sync "just doesn't work."

The token server's `services` table needs a row that maps your storage node's URL to a service ID. If that row is missing or wrong, your browser gets a token that points at nothing, and sync silently fails.

The cleanest way to handle this is to seed it after the first boot:

```sql
-- Run this against the tokenserver database after the container has started once
INSERT INTO services (id, service, pattern)
VALUES (1, 'sync-1.5', '{node}/1.5/{uid}');
```

And then set the node URL in the token server's environment:

```yaml
    - TOKENSERVER_NODE_URL=https://sync.example.com
```

The exact column names and the seeding step vary slightly between token server versions, so if you hit a wall here, check the container logs — the token server is actually pretty good about telling you *why* it can't find a node. The error is usually "no service entry for sync-1.5," which is your cue to seed that row.

## Part 2: The Storage Server (`syncstorage-rs`)

This is the part that actually holds your data, and it's the easier of the two to get running.

### Single-user vs multi-user

`syncstorage-rs` has two modes:

- **SQLite mode** — perfect for a single user or a small family. No separate database server needed. This is what I'd recommend for most homelabbers.
- **MySQL mode** — for when you're running a real multi-user instance and need the performance and tooling.

For this guide I'll use SQLite, because it's the setup that "actually works" with the least moving parts.

### The config

```yaml
syncstorage:
  image: mozilla-services/syncstorage-rs:latest
  restart: unless-stopped
  environment:
    - SYNC_SYNCSTORAGE__DATABASE_URL=sqlite:///data/syncstorage.db
    - SYNC_SYNCSTORAGE__HOST=0.0.0.0
    - SYNC_SYNCSTORAGE__PORT=8000
    - SYNC_SYNCSTORAGE__MASTER_SECRET=a-long-random-master-secret
    - SYNC_SYNCSTORAGE__HUMAN_LOGS=1
  volumes:
    - ./syncstorage-data:/data
```

The one setting you must not skip is **`SYNC_SYNCSTORAGE__MASTER_SECRET`**. This is the secret used to sign and verify the tokens your browser presents. It has to be a long, random string, and it has to stay stable — if you change it, every client's tokens become invalid and they'll all need to re-auth.

Generate it once and keep it somewhere safe:

```bash
openssl rand -base64 48
```

### The token secret has to match

Here's the second gotcha: **the token server and the storage server have to agree on a shared secret.** The token server signs a token, and the storage server verifies that signature. If the secrets don't match, the storage server rejects every request with a 401, and your browser just shows "Sync encountered an error."

In the token server, this is the `TOKENSERVER_FXA_METRICS_HASH_SECRET` (and, depending on version, a separate node secret). In `syncstorage-rs`, it's the `MASTER_SECRET`. Make sure you understand which secret is doing the signing in your token server version and that it matches what the storage server expects.

This is the part where most "it should work" guides fall apart, because they set random values in each container and then wonder why sync fails. The secrets are *not* independent — they're a shared key between the two halves.

## Part 3: The Reverse Proxy (HTTPS Is Non-Negotiable)

Firefox will not sync over plain HTTP. Period. You need a valid TLS certificate in front of both services.

I use Cloudflare Tunnels, which handles the cert for me and means I don't have to expose any ports. If you're using a traditional reverse proxy (Caddy, Traefik, nginx), the config is the same as any other service — just make sure both the token server and the storage server are reachable over HTTPS.

The two URLs you need:

- `https://sync.example.com` → your `syncstorage-rs` container (port 8000)
- `https://token.example.com` → your `tokenserver` container

You can put them on the same host with different paths or subdomains, but subdomains are cleaner and less likely to confuse the token server's URL handling.

## Part 4: Pointing Firefox At Your Server

This is the part that's actually easy, and it's the payoff.

1. Open Firefox and go to `about:config`.
2. Search for `identity.sync.tokenserver.uri`.
3. Set it to `https://token.example.com/1.0/sync/1.5`.

That's it. Firefox will now hit *your* token server, which will point it at *your* storage server, and your data will sync to your own hardware.

To verify it's working, sign in to Firefox Sync as you normally would (with your existing Firefox Account), then check the `syncstorage-rs` logs. You should see your browser hitting the storage endpoint. If you see a stream of 401s, it's the shared-secret mismatch from Part 2 — go fix that.

### A note on the account

As I mentioned, you're still using a Mozilla Firefox Account for the login itself. If you want to go fully independent and self-host the account too, that's the full Firefox Accounts stack, and it's a different beast entirely — multiple services, a brutal setup, and very little community support. For most people, the data is the thing worth owning, and the data is now yours.

## The Three Gotchas, Summarized

If you remember nothing else, remember these three, because they're the difference between "it works" and "I gave up after a weekend":

1. **The old `syncserver` is dead.** Use `syncstorage-rs` + `tokenserver`, two separate Rust services. Following a 2019 guide will waste your time.
2. **The shared secret has to match.** The token server signs, the storage server verifies. Random values in each container = 401s forever.
3. **The service entry has to exist.** The token server needs a database row mapping your storage node to the `sync-1.5` service, or your browser gets a token that points at nothing.

Get those three right and the rest is just Docker plumbing you've done a hundred times.

## The Bottom Line

Self-hosting Firefox Sync is one of those projects that *feels* harder than it is, because the documentation is scattered and the old guides are all dead. But the modern stack is two Rust containers, a MySQL database, and a reverse proxy — and once you understand the two-piece architecture and the shared secret, it's a weekend project, not a research project.

And it's worth doing. Your bookmarks, history, passwords, and tabs are some of the most personal data you have. They're already encrypted before they leave your browser — so the only thing standing between you and full ownership is a couple of containers. Now you know how to run them.

---

*Got your own Firefox Sync instance running, or hit a wall with the token server config? I'd genuinely like to hear how it went — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*Related reading: [Self-Hosted File Sync: Nextcloud vs Seafile vs Syncthing](/blog/2026-08-30-self-hosted-file-sync-nextcloud-seafile-syncthing/), [Cloudflare Tunnels for Your Homelab](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/), and the [Self-Hosted Auth/SSO Showdown](/blog/2026-08-08-self-hosted-auth-sso-showdown/).*
