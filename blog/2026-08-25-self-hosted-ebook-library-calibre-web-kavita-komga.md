---
layout: post.njk
title: "Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga vs Bookshelf (2026)"
date: 2026-08-25
description: "You already self-host your audiobooks with Audiobookshelf — now do the same for your ebooks. A 2026 comparison of Calibre-Web, Kavita, Komga, and the new object-storage-native Bookshelf, with a decision matrix for books vs comics vs audiobooks and copy-paste Docker Compose for each."
tags: ["ebooks", "calibre-web", "kavita", "komga", "bookshelf", "self-hosted", "homelab", "reading", "opds", "docker", "kindle", "kobo", "comics", "manga"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga"
affiliate: false
cta: true
---

# Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga vs Bookshelf

A few weeks ago I wrote the [complete guide to self-hosting your audiobooks with Audiobookshelf](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/). The response made one thing obvious: a lot of you had already ditched Audible, and the very next question was always the same.

*"Okay, but what about my ebooks?"*

It's a fair question, and it exposes a weird asymmetry in the self-hosting world. We've spent years building excellent tools for *listening* to our own media — Audiobookshelf for audiobooks, Navidrome for music, Jellyfin for video. But the *reading* side has been stuck in a strange limbo. Calibre is a desktop app that's brilliant at managing a library but was never meant to be a server. The web front-ends built on top of it have been, frankly, a mess of forks and half-maintained projects.

That's finally changing. In 2026 there are four serious contenders for the "self-hosted eBook library" crown, and they're aimed at four genuinely different use cases. This post is the comparison I wish I'd had before I spent a weekend trying all of them.

Here's the short version, then we'll go deep.

| Tool | Best for | Native format | Standout feature |
|------|----------|---------------|------------------|
| **Calibre-Web** | Existing Calibre users, metadata nerds | EPUB, MOBI, PDF | Best metadata + send-to-Kindle |
| **Kavita** | Comics, manga, and mixed libraries | CBZ, CBR, EPUB, PDF | Best comic/manga reader |
| **Komga** | Comics/manga purists, OPDS-first | CBZ, CBR | Cleanest OPDS + Tachiyomi sync |
| **Bookshelf** | Object-storage natives, minimalists | EPUB, PDF | Runs on S3/MinIO, zero DB |

---

## The Problem: Reading Is the Last Un-Self-Hosted Media

Let me name the actual pain, because it's not "I can't find an app." It's that **reading is the one media type where the default answer is still a proprietary cloud.**

- **Music?** Navidrome, Jellyfin, Plex — solved years ago.
- **Video?** Jellyfin, Plex, Emby — solved.
- **Audiobooks?** Audiobookshelf — solved (I wrote the guide).
- **Ebooks?** ...Kindle, Kobo, Apple Books, Google Play Books. All of them lock your purchases to their app and their cloud.

The irony is that ebooks are the *easiest* media to self-host. An EPUB is a tiny file — a few megabytes at most. A thousand books is a few gigabytes. You don't need transcoding, you don't need GPU acceleration, you don't need a beefy server. A Raspberry Pi can serve your entire library to every device you own.

The reason it's been hard is purely a *software* gap, not a hardware one. And that gap is closing.

---

## The Four Contenders

### 1. Calibre-Web — The Metadata Powerhouse

**What it is:** A web front-end for an existing [Calibre](https://calibre-ebook.com/) library. It reads the `metadata.db` file Calibre maintains and exposes it as a clean, modern web UI.

**Why you'd pick it:** You already use Calibre to manage your books on a desktop, and you want to browse and read them from anywhere. Calibre-Web inherits Calibre's legendary metadata handling — covers, tags, series, custom columns, the works.

**The killer feature:** **Send-to-Kindle.** Calibre-Web can email books directly to your Kindle's `@kindle.com` address, converting formats on the fly. If you're trying to *leave* the Kindle ecosystem, this is the bridge that lets you keep using the hardware while owning the files.

**The catch:** It's a front-end, not a standalone server. You need a Calibre library somewhere (a mounted folder with a `metadata.db`), and Calibre-Web is read-mostly — heavy library *editing* still happens in desktop Calibre. The project has also had a turbulent history of forks and maintainer drama, so pin your version.

**Docker Compose:**

```yaml
services:
  calibre-web:
    image: lscr.io/linuxserver/calibre-web:latest
    container_name: calibre-web
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
      - DOCKER_MODS=linuxserver/mods:universal-calibre
    volumes:
      - ./config:/config
      - /path/to/calibre/library:/books
    ports:
      - "8083:8083"
    restart: unless-stopped
```

---

### 2. Kavita — The Comic & Manga Specialist

**What it is:** A self-hosted reading server built from the ground up for comics and manga, with first-class support for EPUB and PDF too.

**Why you'd pick it:** Your library is mostly comics, manga, or graphic novels — or you want one server that handles *everything* (books + comics + manga) with a genuinely good reading experience for each. Kavita's reader is the best in the game: it handles right-to-left manga, double-page spreads, and webtoon-style vertical scrolling natively.

**The killer feature:** **Smart collections and reading lists.** Kavita automatically groups series, detects reading order, and tracks your progress across devices. It also has a built-in OPDS feed so any OPDS-compatible reader (like the excellent [Panels](https://panels.app/) on iOS) can pull from it.

**The catch:** Kavita is opinionated about folder structure. It wants `Author/Series/Volume/` layouts and will re-scan aggressively. If your files are a flat mess, expect some manual reorganization. It's also heavier than the others — a real database (SQLite by default, but it wants more RAM than Calibre-Web).

**Docker Compose:**

```yaml
services:
  kavita:
    image: jvmilazz0/kavita:latest
    container_name: kavita
    volumes:
      - ./kavita/config:/kavita/config
      - /path/to/books:/books
    ports:
      - "5000:5000"
    restart: unless-stopped
```

---

### 3. Komga — The OPDS Purist

**What it is:** A comics/manga server with a laser focus on doing one thing well: serving a clean, standards-compliant OPDS feed.

**Why you'd pick it:** You want your library to be *consumed* by other apps, not just read in a browser. Komga's OPDS support is the most complete and reliable of the four, which makes it the best backend for [Tachiyomi](https://tachiyomi.org/) (Android manga reader), Panels, and other OPDS clients. If you read comics on a tablet, Komga + Tachiyomi is the gold-standard combo.

**The killer feature:** **Tachiyomi/Mihon sync.** Komga is the de-facto standard backend for the Android manga-reading community. Point Tachiyomi at your Komga server and you get a native, offline-capable reading experience that syncs progress back.

**The catch:** It's comics/manga only — no EPUB book support worth mentioning. If you want a single server for novels *and* comics, Komga isn't it. It's also the most "developer-y" of the four in terms of setup and configuration.

**Docker Compose:**

```yaml
services:
  komga:
    image: gotson/komga:latest
    container_name: komga
    volumes:
      - ./komga/config:/config
      - /path/to/comics:/data
    ports:
      - "25600:25600"
    restart: unless-stopped
```

---

### 4. Bookshelf — The Object-Storage Native

**What it is:** The newcomer. Bookshelf is a self-hosted eBook library that runs directly on **object storage** (S3, MinIO, Backblaze B2, R2) instead of a local filesystem and a database.

**Why you'd pick it:** You already run [MinIO for object storage](/blog/2026-08-23-s3-at-home-minio/) (or you want to), and you like the idea of a stateless server that can be rebuilt in seconds because all your data lives in a bucket. Bookshelf is the "cloud-native" answer to the eBook problem — no SQLite file to back up, no volume to migrate, just a bucket full of EPUBs and a tiny config.

**The killer feature:** **Zero local state.** Point it at a bucket, and your entire library — books, covers, metadata, reading progress — lives in object storage. Back up the bucket, and you've backed up everything. This ties directly into the object-storage stack I've been writing about, and it's the most "2026" architecture of the four.

**The catch:** It's new, so the ecosystem is thin. Fewer integrations, fewer community guides, and the feature set (while clean) is smaller than Calibre-Web or Kavita. If you need send-to-Kindle or comic-specific reading modes, look elsewhere. It's also the least battle-tested for very large libraries.

**Docker Compose (with MinIO):**

```yaml
services:
  bookshelf:
    image: bookshelf/bookshelf:latest
    container_name: bookshelf
    environment:
      - S3_ENDPOINT=http://minio:9000
      - S3_BUCKET=books
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
    ports:
      - "8084:8084"
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - ./minio/data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    restart: unless-stopped
```

---

## The Decision Matrix

Here's the honest "which one should I run" answer, based on what you actually have.

| Your situation | Pick | Why |
|----------------|------|-----|
| You already use Calibre on a desktop | **Calibre-Web** | Zero migration — it reads your existing library |
| Mostly comics/manga, want a great reader | **Kavita** | Best reading experience, handles everything |
| Comics on Android, want Tachiyomi sync | **Komga** | The OPDS/Tachiyomi standard |
| You run MinIO/S3 and want stateless | **Bookshelf** | Cloud-native, zero local state |
| Books + comics + audiobooks, one server | **Kavita** (books/comics) + **Audiobookshelf** (audio) | Two servers, but each is best-in-class |

**My honest recommendation for most people:** If you're starting from scratch and want *one* server for reading, **Kavita** is the best all-rounder — it handles novels, comics, and manga in a single clean UI, and its reader is genuinely excellent. If you already live in Calibre, **Calibre-Web** is the zero-friction choice. And if you've been following my object-storage series, **Bookshelf** is the most interesting thing to watch — it's the direction the whole space is heading.

---

## The "One Library for Everything" Question

The dream is a single self-hosted server that handles books, comics, manga, *and* audiobooks. Here's the reality in 2026:

- **Audiobookshelf** is still the undisputed king of audio — nothing else comes close for audiobooks and podcasts.
- **Kavita** is the best for visual reading (comics/manga) and does a solid job with EPUB novels.
- **Calibre-Web** is the best for metadata-heavy book management and Kindle bridging.

So the "one library" is really **two servers**: Audiobookshelf for your ears, Kavita (or Calibre-Web) for your eyes. That's not a failure of the ecosystem — it's a sign that reading and listening are genuinely different experiences that deserve different tools. The good news is both are lightweight, both run in Docker, and both can point at the same underlying files if you organize them well.

---

## Getting Your Books Out of the Walled Garden

The elephant in the room: **how do you get your existing purchases out of Kindle/Kobo/Apple Books?**

The short answer is that it's a legal gray area that depends on where you live, but the *technical* path is well-trodden:

1. **Download your purchases** from the platform (Kindle lets you download to a registered device; Kobo lets you download DRM-free EPUBs for most books).
2. **Strip the DRM** using the well-known Calibre plugins (the `DeDRM` plugin is the standard tool — I won't link it directly, but it's trivial to find).
3. **Import into Calibre**, clean up the metadata, and let Calibre-Web or Kavita serve the result.

This is the same "take ownership back" argument I made in the Audiobookshelf guide. You paid for the book. You should be able to read it on whatever device you want, forever, without asking permission.

---

## The Bottom Line

Self-hosting your ebooks is the last piece of the "own your media" puzzle, and it's finally as easy as the rest of the stack. Whether you pick Calibre-Web for its metadata, Kavita for its reader, Komga for its OPDS purity, or Bookshelf for its cloud-native architecture, the important thing is that you're no longer renting your own library.

Your audiobooks are self-hosted. Your music is self-hosted. Your video is self-hosted. It's time your ebooks were too.

## Related Posts

- [Self-Hosted Audiobookshelf: The Complete 2026 Guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) — The natural prequel to this post, and the tool Bookshelf is modeled on
- [Self-Hosted Music Streaming: Navidrome Setup Guide](/blog/2026-05-16-self-hosted-music-navidrome-soulseek/) — Same ownership philosophy, different media
- [Jellyfin Ecosystem: The Complete Self-Hosted Media Stack](/blog/2026-08-10-jellyfin-ecosystem-stack/) — Where video fits into the picture
- [Immich: Self-Hosted Photo Management for Your Homelab](/blog/2026-06-17-immich-photo-management-homelab/) — Photos, the other media you should own
- [Self-Hosted S3 at Home with MinIO](/blog/2026-08-23-s3-at-home-minio/) — The object-storage stack Bookshelf runs on

## Resources & Links

- [Calibre-Web GitHub](https://github.com/janeczku/calibre-web)
- [Kavita GitHub](https://github.com/Kareadita/Kavita)
- [Komga GitHub](https://github.com/gotson/komga)
- [Bookshelf GitHub](https://github.com/bookshelfapp/bookshelf)
- [Calibre (desktop app)](https://calibre-ebook.com/) — The desktop manager Calibre-Web is built around
- [OPDS specification](https://opds.io/) — The standard protocol all these tools speak

*This is part of my ongoing self-hosting series. If you found it useful, the [Audiobookshelf guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) and the [MinIO object-storage guide](/blog/2026-08-23-s3-at-home-minio/) are the natural next reads.*
