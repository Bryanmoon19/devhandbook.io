---
layout: post.njk
title: "TrueNAS Core Is Dead — Your Migration Path"
date: 2026-08-31
description: "TrueNAS Core (the FreeBSD line) is effectively end-of-life, and the community has already forked it into FreeCORE and BSDnas. If you're still running Core, here's what actually happened, what your options are, and a step-by-step migration path to Scale — or to a fork."
tags: ["truenas", "truenas-core", "truenas-scale", "freebsd", "zfs", "nas", "storage", "homelab", "self-hosted", "migration", "freecore", "bsdnas"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/truenas-core-eol-migration-path"
---

# TrueNAS Core Is Dead — Your Migration Path

If you've been running TrueNAS Core for years, you've probably felt this coming. The writing has been on the wall since iXsystems announced that TrueNAS Scale — the Debian-based line — was the future, and that Core would be put into maintenance mode. But this week, the other shoe dropped, and it dropped hard.

The short version: **TrueNAS Core is effectively dead.** The FreeBSD-based product that built the TrueNAS name is being sunset, and the community has already forked it — twice — into **FreeCORE** and **BSDnas**. A Hacker News thread on FreeCORE hit 170 points, and the autocomplete tells the rest of the story: people are searching "truenas core to scale migration," "truenas core discontinued," "truenas core eol."

If you're one of the thousands of homelabbers and small businesses still running Core, this post is for you. Here's what actually happened, what it means for your data, and a concrete migration path — whether you go to Scale or stick with a fork.

## What Actually Happened

Let me be precise, because there's a lot of panic and a lot of misinformation floating around.

TrueNAS has always shipped two products:

- **TrueNAS Core** — the original, built on FreeBSD. This is the descendant of FreeNAS, the project that started it all back in 2005. It's been the default recommendation for a decade.
- **TrueNAS Scale** — the newer line, built on Debian Linux. It started as a way to add Linux containers and scale-out storage, and over the last few years iXsystems has been pouring all its development energy into it.

For a while, iXsystems maintained both. But the roadmap has been unambiguous for years: **Scale is the future, Core is legacy.** New features landed in Scale first. Core got security patches and bug fixes, but no meaningful new development. The community read the tea leaves correctly — Core was on life support.

Then came the announcement that Core would no longer receive feature updates, and that the FreeBSD line was being wound down entirely. iXsystems' official position is that Core users should migrate to Scale. The FreeBSD codebase that Core is built on is being deprecated.

That's the "dead" part. But here's the part that makes this genuinely interesting rather than just sad: **the community didn't accept it.**

## The Forks: FreeCORE and BSDnas

When a beloved open-source project gets sunset by its corporate steward, the community usually does one of two things: it migrates, or it forks. In this case, it did both — and the forks are worth knowing about even if you plan to migrate.

### FreeCORE

[FreeCORE](https://github.com/freecore-org/freecore) is the community continuation of the FreeBSD-based TrueNAS Core. The pitch is simple: keep the FreeBSD line alive, keep it patched, keep it free, and don't force anyone to migrate to a Linux-based platform they never asked for.

The HN thread that hit 170 points was largely people who *prefer* FreeBSD for their storage. And they have real reasons:

- **ZFS is native to FreeBSD.** FreeBSD's ZFS integration is arguably the most mature in the world — it's the reference implementation that OpenZFS on Linux was ported *from*. If you want the most battle-tested ZFS, FreeBSD is still the gold standard.
- **Stability over features.** Core users tend to be the "set it and forget it" crowd. They don't want a new app catalog or Kubernetes. They want a NAS that runs for five years without a reboot.
- **No forced migration.** The whole point of a fork is that you don't have to move if you don't want to.

The catch, as with any fork, is **sustainability.** A fork is only as good as the people maintaining it. FreeCORE has momentum right now, but the long-term question — who patches it, who audits it, who keeps it secure — is the same question every fork faces. If you go this route, you're betting on the community.

### BSDnas

[BSDnas](https://github.com/bsdnas/bsdnas) is the other fork, and it's positioned slightly differently. Where FreeCORE is a straight continuation of Core, BSDnas is more of a "FreeBSD storage, reimagined" project — a cleaner, more opinionated take on what a FreeBSD-based NAS should be in 2026.

The two forks are early, and it's honestly too soon to say which (if either) will win. But their existence is the important signal: **the FreeBSD storage community is not going quietly.** If you want to stay on FreeBSD, you have options that didn't exist a month ago.

## Your Three Real Options

So here's where you actually stand. If you're running TrueNAS Core today, you have three paths:

### Option 1: Migrate to TrueNAS Scale

This is the official path, and for most people it's the right one. Scale is where the development is, where the security patches are guaranteed, and where the ecosystem is heading. It's Debian-based, so you get Linux containers, Docker, and the TrueNAS Apps catalog alongside your ZFS storage.

**Pros:**
- Actively developed, officially supported, guaranteed security patches
- Linux ecosystem — Docker, Kubernetes, the whole modern toolchain
- TrueNAS Apps (the Docker-based catalog) is genuinely good
- Your ZFS pools migrate cleanly (more on this below)

**Cons:**
- It's a different OS. FreeBSD habits don't all carry over
- Some people report Scale is heavier and more complex than Core
- The migration isn't a one-click upgrade — it's a reinstall with a config import

### Option 2: Stay on FreeBSD with a Fork

If you're philosophically committed to FreeBSD — or you just don't want to touch a working system — FreeCORE or BSDnas is your path. You keep your FreeBSD base, your ZFS stays native, and you avoid the Linux migration entirely.

**Pros:**
- No OS change, no migration risk
- Native FreeBSD ZFS, which is still the reference implementation
- Keeps the "set it and forget it" philosophy alive

**Cons:**
- Fork sustainability risk — you're betting on community maintainers
- No corporate backing, no guaranteed security SLA
- Early-stage projects; expect rough edges

### Option 3: Move Off TrueNAS Entirely

This is the nuclear option, but it's worth naming. If you're going to migrate anyway, you could migrate to something else entirely — plain Debian with ZFS, Proxmox with a NAS VM, or one of the other storage platforms. I wrote about the [Proxmox NAS options](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/) earlier this month, and there are real alternatives.

**Pros:**
- Maximum flexibility, no vendor lock-in
- You control the entire stack

**Cons:**
- You lose the TrueNAS management UI, which is genuinely good
- Most work, most risk, most to rebuild

For most people, the honest answer is **Option 1.** Migrate to Scale. It's the path of least resistance with the most long-term security. But let me walk you through how to actually do it without losing your data.

## The Migration Path: Core → Scale

Here's the thing that scares people about migrating: **your data is on those ZFS pools, and you can't afford to lose it.** The good news is that ZFS is ZFS — the on-disk format is the same whether you're on FreeBSD or Linux. Your pools will import into Scale. The bad news is that the migration is a reinstall, not an in-place upgrade, and you need to do it carefully.

### Step 0: Back Up Your Config (And Your Data)

Before you touch anything, export your TrueNAS Core configuration. In the Core UI, go to **System → General → Save Config**. This saves a `.tar` file with your users, shares, network settings, cron jobs, and everything else that isn't your actual data.

Then — and I can't stress this enough — **back up your actual data.** A config export is not a data backup. If you have irreplaceable data on those pools, make a real backup before you migrate. ZFS migrations usually go fine, but "usually" is not a guarantee, and the one time you skip the backup is the one time the import fails.

### Step 1: Install TrueNAS Scale

Download the [TrueNAS Scale ISO](https://www.truenas.com/download-truenas-scale/), write it to a USB drive, and install it on your boot device. This is a fresh install — you're replacing the Core OS, not upgrading it.

**Important:** Install Scale on a *separate* boot device if you can, or at least be prepared to lose the Core boot environment. Your data pools are on separate disks (they should be — if your data lives on the same disk as your OS, fix that first), so the OS reinstall doesn't touch your data.

### Step 2: Import Your Config

Once Scale is installed and booted, go to **System → General → Upload Config** and upload the `.tar` file you saved in Step 0. This restores your users, shares, and settings.

**Caveat:** Not everything maps 1:1 between Core and Scale. Some settings will import cleanly, some will need manual reconfiguration, and some Core-specific features (like certain jails) don't exist in Scale at all. Expect to spend some time reviewing your shares and permissions after the import.

### Step 3: Import Your ZFS Pools

This is the critical step. In Scale, go to **Storage → Import Pool** and import your existing pools. Because ZFS is ZFS, the pools should import cleanly — your datasets, snapshots, and data all come along.

**Caveat:** If your pools were created with FreeBSD-specific features or very old ZFS versions, you may need to upgrade the pool. Scale will tell you if this is the case. Read the prompt carefully — a pool upgrade is one-way, so make sure you're committed before you click.

### Step 4: Rebuild What Doesn't Transfer

Jails are the big one. TrueNAS Core used FreeBSD jails for plugins and custom services. Scale uses Docker containers instead. Your jails will **not** migrate — you'll need to rebuild them as Docker containers or TrueNAS Apps.

This is honestly the most painful part of the migration for most people. If you were running Plex, Nextcloud, or any other service as a Core jail, you'll need to set it up again in Scale. The good news is that Scale's Docker-based approach is more flexible and better documented, but it's still work.

### Step 5: Verify Everything

Before you declare victory, verify:

- Your pools are imported and healthy (`zpool status` shows no errors)
- Your shares are accessible from your clients
- Your users can authenticate
- Your snapshots and replication tasks are still configured
- Your services (rebuilt as Docker) are running

Run a scrub on your pools after the migration to confirm data integrity. It's cheap insurance.

## The Fork Path: Core → FreeCORE/BSDnas

If you're going the fork route instead, the migration is much simpler — because it's barely a migration at all. FreeCORE and BSDnas are both FreeBSD-based, so you're staying on the same OS family.

The general approach:

1. **Back up your config** (same as above — always)
2. **Install the fork** on your boot device
3. **Import your config and pools** — because it's still FreeBSD ZFS, this should be nearly seamless
4. **Verify** — same checklist as above

The risk here isn't the migration, it's the *future*. A fork is only as good as its maintainers, and you're trading iXsystems' (admittedly winding-down) support for a community project. If you go this route, keep a close eye on the fork's activity — commit frequency, release cadence, security patch responsiveness. If it stalls, you'll want to know before you're stuck on an unpatched NAS.

## What I'd Actually Do

If you're asking me for a recommendation, here it is:

**Migrate to TrueNAS Scale.** Not because Scale is perfect — it isn't — but because it's the option with the clearest long-term future. The forks are exciting, and I genuinely hope one of them thrives, but betting your primary storage on a six-month-old fork is a risk I wouldn't take with data I care about.

The migration is work, but it's *bounded* work. You do it once, you verify, and you're on a platform that's actively developed and officially supported. The alternative — staying on Core until it's genuinely unpatched and *then* scrambling — is how people lose data.

Here's my honest timeline recommendation:

- **If you're on Core now:** Start planning the migration. You don't have to do it this week, but you should do it this quarter. Core isn't going to explode tomorrow, but every month you wait is a month of unpatched risk accumulating.
- **If you're setting up a new NAS:** Don't start on Core. Go straight to Scale. There's no reason to start a new deployment on a dead platform.
- **If you're philosophically committed to FreeBSD:** Watch FreeCORE and BSDnas. They're early, but they're real. Revisit in six months and see which one has legs.

## The Bottom Line

TrueNAS Core had a great run. It was the default answer to "how do I build a serious NAS" for a decade, and it earned that position. But the FreeBSD line is ending, and pretending otherwise doesn't help anyone.

The good news is that you have options — real ones. Scale is a mature, actively-developed platform that will import your pools cleanly. The forks give you a FreeBSD path if you want it. And the ZFS format that underpins everything means your data is never actually trapped.

The bad news is that you have to *do something*. "Wait and see" is not a migration strategy, and the people who get burned by EOL announcements are always the ones who waited.

So: back up your config, back up your data, and pick a path. Your future self — the one who isn't running an unpatched NAS in 2027 — will thank you.

---

*Are you still running TrueNAS Core? Have you migrated to Scale, or are you watching the forks? I'd love to hear how it went — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [NAS options on Proxmox](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/) and the [self-hosted storage stack](/blog/2026-08-14-docker-backup-playbook-restic-dockstash/).*
