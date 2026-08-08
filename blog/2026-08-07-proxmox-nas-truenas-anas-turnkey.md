---
layout: post.njk
title: "Self-Hosted NAS on Proxmox: TrueNAS vs ANAS vs TurnKey (2026)"
date: 2026-08-07
description: "Compare three ways to add NAS storage to Proxmox — TrueNAS Scale, the new ANAS plugin, and TurnKey File Server. Real trade-offs, setup complexity, and which one fits your homelab."
tags: ["proxmox", "nas", "truenas", "anas", "turnkey", "self-hosted", "storage", "zfs", "homelab"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/proxmox-nas-truenas-anas-turnkey"
---

# Self-Hosted NAS on Proxmox: TrueNAS vs ANAS vs TurnKey (2026)

Proxmox is a fantastic hypervisor. It's free, it runs everything, and the web UI is the best in class for a homelab platform. But there's one thing Proxmox has always been bad at: **file sharing**.

Out of the box, Proxmox doesn't give you a sane way to spin up a CIFS/SMB share, an NFS export, or a ZFS pool that you can manage from the GUI. You can do it from the CLI. You can do it with enough `apt` and `systemd` hacking. But it's never felt native — and for years, the answer has been "just run TrueNAS in a VM."

That answer still works. But in 2026, you have a third option that didn't exist six months ago, and it changes the calculus. Today there are three real paths to NAS on Proxmox:

1. **[TrueNAS Scale](https://www.truenas.com/truenas-scale/)** — the heavyweight, full-OS storage appliance running in a VM
2. **[ANAS](https://github.com/ccebelenski/anas)** — the newcomer, a ZFS manager that lives inside the Proxmox web UI
3. **[TurnKey File Server](https://www.turnkeylinux.org/fileserver)** — the lightweight, pre-built LXC container that's "good enough" in 2 minutes

Each one has a different philosophy. Here's what actually works, what doesn't, and which one to pick.

## The Contenders

### TrueNAS Scale (Community Edition)

TrueNAS Scale is the safe, mature choice. It's a full Debian-based Linux distro with a ZFS-first storage stack, a polished web UI, and an app catalog that lets you run Docker workloads alongside your storage. You run it as a VM inside Proxmox and pass your HBA (or individual drives) through via PCIe passthrough so TrueNAS can manage them directly.

**Pros:**
- Battle-tested ZFS management — pools, datasets, snapshots, replication, scrubs, the works
- Mature SMB, NFS, iSCSI, and S3 support
- TrueNAS Apps (the new Docker-based catalog) is genuinely good
- Huge community, ten years of documentation, every edge case is in a forum post somewhere

**Cons:**
- Resource-heavy. The official minimum is 8 GB of RAM (and they really mean it — ZFS loves RAM for ARC caching)
- VM overhead and a separate management plane. You have two web UIs: Proxmox at `:8006` and TrueNAS at `:81` (or `:443`)
- PCIe passthrough is finicky. IOMMU groups, ACS overrides, kernel parameters, and you better have a second GPU or a working virtual console for when things go sideways
- Updates require coordinated reboots of Proxmox and the TrueNAS VM
- You're managing a whole separate OS, not just storage

**Best for:** Dedicated NAS builds, large storage arrays (8+ drives), people who want a full storage appliance and don't mind the operational tax.

### ANAS — A New Challenger

[ANAS](https://github.com/ccebelenski/anas) (Advanced NAS) launched in July 2026 and it does something nobody has done before: it gives you a TrueNAS-style ZFS management experience **inside the Proxmox web UI**. No separate VM. No separate login. No second OS to patch.

You install ANAS as a plugin on the Proxmox host itself, and it shows up at `https://your-pve:8006/anas` as a native PVE extension. It manages ZFS pools on the host, then exports them over SMB and NFS to your network.

**Pros:**
- Native PVE integration — the ANAS interface is just another tab in the Proxmox UI
- Zero overhead. It's a Node.js service, ~256 MB of RAM, no VM
- **AHR (Advanced Hybrid RAID)** — this is the killer feature. ANAS supports Synology-SHR-style hybrid pools, so you can mix 12 TB, 8 TB, and 4 TB drives in the same pool and use *all* the space. Expand one disk at a time
- "Guest" philosophy — ANAS doesn't shadow your ZFS state. It reads what's on disk, it doesn't maintain a separate database. So if you blow away the ANAS install, your pools are still there, intact
- Surgical config editing — you can drop down to raw ZFS commands, edit `/etc/samba/smb.conf` directly, and ANAS sees the change on the next scan. No "config drift" errors
- Single management plane. One web UI. One set of credentials. One place to check.

**Cons:**
- Pre-1.0. Interfaces may change. APIs may break. If you're risk-averse, wait
- Requires Node.js ≥ 20 on the Proxmox host
- AGPL-3.0 license — fine for homelab use, but if you're packaging ANAS into a commercial product, read the source-available clauses
- Smaller community than TrueNAS (obviously — it's been out for weeks, not a decade)
- No Docker app catalog (use the Proxmox host's container/VM ecosystem instead)

**Best for:** Proxmox users who want NAS features without leaving the Proxmox ecosystem. Anyone with a mixed collection of old drives. Homelabbers who want ZFS management but not a second OS.

### TurnKey File Server

[TurnKey Linux](https://www.turnkeylinux.org/fileserver) is the old guard of pre-built server appliances. The File Server template is a Debian LXC image with Samba, NFS, WebDAV, SFTP, and rsync already configured. You download it, create a container, and you've got a working file share in two minutes.

**Pros:**
- Stupid simple. `pveam update` → download template → create CT → start → done
- 512 MB of RAM is all it needs
- No PCIe passthrough, no HBA, no IOMMU headaches
- Web-based file manager included (FileBrowser, mounted at `/files`)
- 15 years of TurnKey stability — these templates are boring in the best way

**Cons:**
- No ZFS management. If you want ZFS, you're managing it on the Proxmox host via CLI and then mounting datasets into the TurnKey container
- Limited to file sharing — no Docker, no apps, no plugins
- Basic Samba config. The default is fine, but tweaking it is on you
- Web UI is utilitarian, not pretty

**Best for:** Quick SMB/NFS shares. Media server backends. Anyone who just needs `\\server\share` to work and doesn't care about ZFS, snapshots, or hybrid RAID.

## Comparison Matrix

| Feature | TrueNAS Scale | ANAS | TurnKey FS |
|---|---|---|---|
| Type | Full OS (VM) | PVE plugin | LXC container |
| RAM minimum | 8 GB | ~256 MB | 512 MB |
| Setup time | 1–2 hours | 10 minutes | 2 minutes |
| ZFS management | ✅ Full GUI | ✅ Full GUI | ❌ Host CLI only |
| Hybrid RAID (mixed drives) | ❌ | ✅ AHR | ❌ |
| SMB / NFS | ✅ | ✅ | ✅ |
| Docker / apps | ✅ TrueNAS Apps | ❌ (use PVE) | ❌ |
| Snapshots | ✅ | ✅ | ❌ |
| Web UI | Separate (`:81` / `:443`) | PVE `:8006/anas` | Separate (port 80/443) |
| Maturity | 10+ years | Pre-1.0 (July 2026) | 15+ years |
| License | Free (Community) | AGPL-3.0 | GPL |

## Decision Framework

**Pick TrueNAS if:**
- You're building a dedicated NAS with 4+ drives and want it to be the storage brain of your homelab
- You want TrueNAS Apps (their Docker catalog is genuinely good)
- You're comfortable with PCIe passthrough and managing a VM alongside Proxmox
- You need iSCSI, Active Directory integration, or S3-compatible object storage

**Pick ANAS if:**
- You already run Proxmox and don't want a second OS to manage
- You have a junk drawer of mixed-size drives (AHR turns that into usable storage)
- You want a single web UI for everything
- You're okay running pre-1.0 software that's actively developed and dogfooded by its author

**Pick TurnKey if:**
- You just need a quick SMB or NFS share, right now, in 5 minutes
- You're resource-constrained (512 MB of RAM is all it needs)
- You don't need ZFS, snapshots, or hybrid RAID
- You want something boring and reliable that's been around forever

## Bryan's Take

I've been running Proxmox on my Venus host (192.168.7.134) since 2023. For bulk storage, I actually run a **UNAS Pro** mounted to Proxmox via CIFS — it's a 4-bay unit with 4× 8 TB drives, and it handles the heavy lifting for media, backups, and the *arr stack. Proxmox itself runs off NVMe for VMs and containers, with the UNAS Pro providing the cold/warm storage layer via a network mount.

So my Proxmox box doesn't need its own big ZFS array. But a lot of homelabbers are starting fresh with a single Proxmox host and a stack of drives they want to use — and that's where these three options come in.

Here's my honest take:

- **For homelabbers starting fresh, ANAS is the most exciting option.** The hybrid RAID alone is worth it. Being able to throw whatever drives you have into a redundant pool — and expand one disk at a time as you buy more — is exactly what homelabbers need. TrueNAS makes you commit to a vdev layout upfront. ANAS lets you evolve.
- **TrueNAS is overkill for most homelab use cases** unless you're building a dedicated storage server. The 8 GB RAM floor, the PCIe passthrough dance, the second OS — it's a lot of moving parts for what most people actually need.
- **TurnKey is the unsung hero.** I've used it for ad-hoc shares, scratch space for VMs, and quick file drops for friends. It's never let me down, it never breaks, and it never gets in the way.

The real answer, though, is that **you'll probably end up using two of these.** ANAS for your main ZFS pools, TurnKey for quick SMB shares that don't need ZFS. That's the stack I'd build today.

## Setup Quick-Start

### TrueNAS Scale (5 steps)

1. Download the TrueNAS Scale ISO from truenas.com
2. Create a VM in Proxmox with 8 GB+ RAM, 2 vCPUs, and a 32 GB virtual disk for the OS
3. Pass your HBA or individual drives through via PCIe passthrough (set the VM to use `host` CPU type, configure IOMMU on the host first)
4. Boot the ISO, install to the virtual disk, configure pools and datasets via the TrueNAS web UI
5. Mount the TrueNAS shares on your Proxmox host or other VMs via CIFS/NFS

### ANAS (3 steps)

1. Download the latest release from [github.com/ccebelenski/anas](https://github.com/ccebelenski/anas) and unpack it: `tar xzf anas-<version>.tar.gz && cd anas-<version>`
2. Install dependencies and the service: `sudo ./install.sh --install-deps`
3. Open `https://your-pve:8006/anas` in your browser — it's there, no extra config needed

### TurnKey File Server (2 steps)

1. Refresh the template list and grab the File Server template: `pveam update && pveam available | grep fileserver`, then `pveam download local <template-name>`
2. Create a CT from the template, start it, and visit the web UI at the container's IP (TurnKey shows the URL in the console output on first boot)

## The Bottom Line

**ANAS is the most exciting thing to happen to Proxmox storage since Proxmox.** It fills the one gap the platform has always had: first-class ZFS management without leaving the PVE web UI. The hybrid RAID support is a genuine game-changer for homelabbers who accumulate drives like I do.

**TrueNAS is the safe choice** if you need a full storage appliance, you want the apps catalog, and you don't mind the operational overhead of a second OS.

**TurnKey is the "I need this working in 5 minutes" choice.** It will never let you down. It will never surprise you. It will never be exciting. Sometimes that's exactly what you want.

For most homelabbers in 2026, my recommendation is: **start with ANAS for your ZFS pools, add TurnKey for quick shares when you need them.** Skip TrueNAS unless you have a specific reason to need it. The future of Proxmox storage is native to Proxmox, and ANAS is the first real step in that direction.

---

*Running Proxmox and want to talk storage? Hit me up — I'm always interested in what setups other homelabbers are running, especially weird ZFS topologies and AHR pool configurations. The ANAS project is moving fast and the maintainer is actively taking feedback from real-world deployments.*
