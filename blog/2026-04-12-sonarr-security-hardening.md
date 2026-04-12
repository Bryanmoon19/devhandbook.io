---
layout: post.njk
title: "Sonarr Security Hardening: How to Block Malicious Downloads at the Source"
date: 2026-04-12
description: "Stop .exe, .rar, and junk files from ever reaching your *arr stack. A practical guide to Sonarr release profiles, indexer restrictions, and torrent client blocks."
tags: ["sonarr", "radarr", "lidarr", "security", "arr-stack", "homelab", "self-hosted", "torrent"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/sonarr-security-hardening"
---

Every few weeks, someone on r/sonarr asks the same question: *"How do I stop Sonarr from downloading .exe files disguised as TV episodes?"* It's a real problem. Malicious release groups occasionally package malware inside fake media releases, and without the right safeguards, your automation will grab them before you ever see what's inside.

The good news: you can block most of this junk **before it hits your disk**. This guide covers the three layers of defense that actually work — release profiles, indexer restrictions, and client-side blocks.

## What We're Actually Defending Against

The typical attack looks like this:
1. A release appears on your indexer with a name like `Show.S01E01.1080p.WEB-DL.x264-EVO.mkv`
2. Sonarr grabs it automatically because the name, size, and quality match your profiles
3. Inside the `.rar` or `.zip` archive is an executable, not a video file
4. If you (or a script) unpack and run it, you're compromised

These releases are usually low-seed, new accounts, and from obscure groups. The defenses below target exactly those traits.

## Layer 1: Sonarr Release Profiles (The Most Important Fix)

Release profiles let you reject downloads based on keywords, file extensions, release group names, and quality preferences. This is where the bulk of your protection lives.

### Create a "Block Malicious" Release Profile

Go to **Settings > Profiles > Release Profiles** and click the **+** icon.

**Name:** `Block Malicious Files`

**Must Not Contain:**
```
.exe
.dll
.bat
.cmd
.zip
.iso
.scr
.jar
.msi
.vbs
.ps1
```

**Preferred Words (optional scoring adjustments):**
- `-x265` or `-x264` → `+10` (legitimate codecs)
- `HEVC` → `+5`

**Must Not Contain (release group blocklist):**
```
FAKEGROUP
NEWSCENE
UNKNOWN
```
*(Update this as you find bad actors in your indexer feeds.)*

Set **Indexers** to "Any" so this applies globally.

### Enable "Must Not Contain" for File Extensions in Releases

Sonarr's "Must Not Contain" field checks the release **name**, not the actual file contents. That's usually enough — malicious releases often include `.exe` or `.rar` right in the title. But for an extra layer, you can also reject releases that mention archive formats commonly used to hide malware:

```
.part1.rar
.rar
.7z
.zip
```

Yes, some legitimate releases are compressed. But in 2026, most reputable indexers and release groups distribute raw `.mkv` or `.mp4` files. If you're on Usenet, `.rar` is more common — adjust this list based on your setup.

### Restrict Unknown Release Groups

Add a second release profile called `Require Known Groups`:

**Must Contain (optional, if you want to be aggressive):**
```
-NTb
-SCENE
-ROBOTS
-GLHF
-KOGi
-SPKED
-NTG
-SRG
-T6D
-ION10
-FLUX
```

This is aggressive — it will reject anything not from a known group. Only use this if your indexers are clean enough that you won't miss out on legitimate content.

A safer middle ground: **remove the `Must Contain` list and instead boost known groups with Preferred Words (+25 each)** while keeping the `Must Not Contain` blocks above.

## Layer 2: Indexer Restrictions and Categories

Some indexers support category filtering and minimum seed requirements. Use both.

### Require Minimum Seeds/Peers

In **Settings > Indexers**, edit each indexer and look for **Minimum Seeders** or **Minimum Peers**. Set it to at least `1` (obviously) but ideally `3–5`. Malicious releases often have zero or one seeder.

If your indexer doesn't expose this in Sonarr, check whether your indexer supports it in their web UI and filter there.

### Stick to Trusted/Verified Categories

If your indexer has categories like `TV-HD`, `TV-SD`, and `TV-UK`, great. If it has a `XXX` or `Other` category, make sure Sonarr isn't searching it accidentally.

In Sonarr's indexer settings:
- **Anime Categories** → Only anime-specific categories
- **Categories** → Only TV categories (`5000`, `5030`, `5040`, etc. from the Newznab standard)

Don't leave categories as "All."

### Enable Indexer-Specific RSS Sync Delays

Under each indexer, set a small **RSS Sync Delay** (5–15 minutes). This gives other users time to report bad releases before your automation grabs them. Most good indexers have community reporting systems that nuke malicious uploads within minutes.

## Layer 3: Torrent Client Blocks (The Safety Net)

If something slips past Sonarr, your torrent client is the last line of defense.

### qBittorrent: Block Common Malicious Extensions

qBittorrent doesn't have built-in extension blocking, but you can approximate it with **categories** and **automated management** — or use a post-download script.

A simpler approach: configure qBittorrent to **not automatically run downloaded files**, and set your unpacker (like ExtractNow or UnRAR) to never execute files.

### Deluge: Use the Blocklist Plugin

Deluge has plugins like **Blocklist** that can filter by IP, but not by file extension. For extension blocking, use a post-processing script.

### rtorrent/rutorrent: Auto-Stop by Extension

In `.rtorrent.rc`, you can set a completion handler that inspects file extensions:

```bash
method.set_key = event.download.finished,check_ext,"branch=d.custom1=,\"execute=bash,-c,\\\"find \(rTorrent download directory\) -name '*.exe' -delete\\\"\""
```

This is hacky but effective — it auto-deletes any `.exe` found in a completed download.

### The Nuclear Option: Containerized Downloads

Run your torrent client in a Docker container with a read-only downloads volume and no execution privileges. Even if malware downloads, it can't run inside the container. Your media server (Plex, Jellyfin) mounts the same path read-only. Extraction happens in a separate, minimal tool container.

This is overkill for most users, but it's how the paranoid do it.

## A Practical Sonarr Security Checklist

Use this as your baseline:

- [ ] Create a "Block Malicious" release profile with `.exe`, `.dll`, `.bat`, `.scr`, `.jar`, `.msi`, `.vbs`, `.ps1`
- [ ] Apply that profile to all indexers
- [ ] Set minimum seeders to `3+` on every indexer
- [ ] Limit categories to TV-only (Newznab `5000` series)
- [ ] Add an RSS sync delay of `5–15` minutes
- [ ] Avoid unknown release groups (boost known groups, block suspicious ones)
- [ ] Ensure your torrent client does **not** auto-execute downloaded files
- [ ] (Optional) Run a post-download script to delete blocked extensions
- [ ] (Optional) Containerize your download client

## What About Radarr and Lidarr?

Everything in this guide applies to the entire *arr stack. Radarr especially benefits from release profile blocks — movie releases are a bigger target for malware disguised as cam rips or "early leaks." Lidarr sees less of this, but the same principles work.

Copy your release profile settings across all your *arr apps for consistent protection.

## Bottom Line

Sonarr automation is one of the best parts of a self-hosted media stack — but it only works safely if you filter the fire hose of releases coming from public and semi-private indexers. A few minutes configuring release profiles saves you from the nightmare of malware on your NAS or media server.

You don't need to be a security expert. You just need to be slightly more paranoid than the average downloader.

---

*Inspired by the r/sonarr community discussion on [blocking malicious downloads](https://www.reddit.com/r/sonarr/s/nkfzDyau1o).*
