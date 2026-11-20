---
layout: post.njk
title: "Homelab Diagram-as-Code: The 1.4k-Star Tool That Turns Your YAML Into an r/homelab Network Diagram"
date: 2026-11-20
description: "homelab-diagram turns a YAML inventory of your network into the clean, r/homelab-style SVG/PNG diagram you've always wanted — and nobody is covering it. Here's how it works, why diagram-as-code beats drag-and-drop tools like draw.io and Excalidraw for your infrastructure, and how to make it work for your own lab (including our free generator for the layout you don't want to hand-place)."
tags: ["homelab-diagram", "diagram-as-code", "network-diagram", "homelab", "yaml", "svg", "infrastructure-as-code", "documentation", "self-hosted", "draw-io", "network-topology", "devops", "developer-tools"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-20-homelab-diagram-as-code/"
affiliate: false
cta: true
---

# Homelab Diagram-as-Code: The 1.4k-Star Tool That Turns Your YAML Into an r/homelab Network Diagram

Every homelabber has hit the same wall. You've got a Proxmox host running a dozen containers, a NAS with pools and vdevs, a switch with VLANs trunked across ports, a firewall, and a pile of devices hanging off it all. You know exactly how it fits together — until someone asks you to *draw it*, and you're staring at a blank draw.io canvas at 1 AM trying to drag boxes around a grid and making your network look like a ransom note.

Then you see the diagrams on r/homelab. Clean. Labeled. The line *width* literally encodes the link speed. Trunks drawn as white cables with dark cores. VLAN tags rendered as little bars on each switch port. And you think: *I want one of those. How hard can it be?*

Turns out the answer, in late 2026, is "about as hard as writing a YAML file." A project called **[homelab-diagram](https://github.com/Goblinmine/homelab-diagram)** — by `Goblinmine` — has blown past **1,400 GitHub stars in under two weeks** (created November 7th, 2026), and it's exactly what it sounds like: a tool that renders a beautiful, r/homelab-style network diagram from a YAML inventory. And despite "homelab diagram" autocompleting richly in search, almost *nobody* has written a self-hoster's guide to it yet. So here it is.

---

## What homelab-diagram Actually Is

The pitch, straight from the README: it's the script behind the network diagram the author posted on r/homelab. It takes a `inventory.yaml` file describing your lab and turns it into a big SVG (and PNG) in the style of the diagrams you see on that subreddit every day.

What it draws, specifically:

- **The full path from the internet** through the ISP router (with its real ports) and the firewall to the core switch.
- **Every switch port with its VLANs**, where a tall bar is an untagged VLAN and short bars are tagged.
- **Cables whose line width is the negotiated link speed** — 10G, 2.5G, 1G, 100M — with trunks drawn as a white cable with a dark core.
- **Every device** with name, type, model, IP · hostname, and OS.
- **The Proxmox host** with its hardware, the VMs/CTs outside the DMZ, the TrueNAS pools (disks, vdevs, usage), and every DMZ container with its CT ID, IP, and hostname.
- **Multi-app containers** rendered as one card with a row per app.
- **What's exposed to the internet**, a legend, a networks table, and even a small "media pipeline" explainer.

That's not a generic "boxes and arrows" tool. That's a diagram with *semantic density* — the kind that actually tells you something about your infrastructure, not just what's plugged into what.

And the kicker, the thing that makes it feel like a magic trick:

```yaml
# inventory.yaml — everything the picture shows
vlans:
  - name: "LAN"
    id: 10
    color: "#4e9a06"
devices:
  - name: "firewall"
    type: "OPNsense"
    model: "Protectli VP2420"
    ip: "10.0.0.1"
    hostname: "fw"
    os: "FreeBSD"
# ... switches, ports, hardware, pools, containers
```

```bash
uv sync                       # once: install PyYAML + Pillow
uv run fetch_icons.py         # download the service icons (once)
uv run build.py               # → out/homelab.svg + out/homelab.png
uv run build.py --unredacted  # private version with real values
```

That's it. YAML in, diagram out.

---

## Diagram-as-Code vs. Drag-and-Drop: Why This Matters

The reason homelab-diagram got 1.4k stars in two weeks isn't that it draws pretty pictures — plenty of tools do that. It's that it sits on the right side of the diagramming divide that's been slowly resolving in infrastructure's favor for years:

**Drag-and-drop tools (draw.io, Excalidraw, Lucidchart)** are great for a one-off sketch. You drag boxes, you label them, you screenshot it, you never update it again. Six months later, the diagram shows a switch you replaced, a VLAN you deleted, and a NAS that's now a different NAS, and nobody trusts it anymore. The diagram *drifts from reality* because the diagram and the system it describes live in two different places, maintained by two different levels of effort.

**Diagram-as-code** flips that. Your diagram is a text file. It lives in the same git repo as everything else about your lab. It's diffable, reviewable, and — critically — *re-renderable*. When you add a container or re-trunk a port, you change a line in `inventory.yaml`, re-run the build, and your diagram is accurate again in ten seconds. The diagram stops being a thing you *drew once* and becomes a thing your infrastructure *generates*.

This is the same arc infrastructure went through with Terraform (config-as-code beats clicking in a console), with Docker Compose (declarative beats `docker run` ad-hoc flags), and with Kubernetes manifests. The diagram is one of the last artifacts still being hand-drawn, and it's finally catching up.

There's a deeper point here too. A YAML inventory is *machine-readable documentation*. The same file that renders your diagram could, in principle, drive monitoring, provisioning, or a topology check. The diagram becomes a *view* onto a source of truth, not the source of truth itself. That's the difference between a picture and an artifact.

---

## The Honest Catch (and Why It's Not a Dealbreaker)

Here's the part every breathless "check out this tool!" post would skip, and it's the most important thing to know before you commit an evening to it. The README says it in a big "IMPORTANT" callout, and I'm going to repeat it because it changes your expectations:

> **This is not a general tool.** The *content* comes from `inventory.yaml`, but the *layout* — where every box, port, and cable goes — is hand-placed in `build.py` for exactly *the author's* network. If you want to use it for yours, expect to move coordinates around in the code.

In other words: homelab-diagram gives you a *brilliant* example of the finished product and the exact technique to reproduce it, but it is not "drop in your YAML and get a perfect diagram of *your* network." The semantic data model (VLANs, devices, ports, pools, containers) is yours to fill in, but the *geometry* is hardcoded for a specific topology.

Why that's not a dealbreaker:

1. **The layout is the hard-won part.** The author spent ~60 rounds of render-and-check iteration with Claude Code getting the folder-shaped device cards, the line-width-encodes-speed convention, the trunk rendering, and the badge fitting to look right. That design knowledge is *in the code*, and it's worth more than the tool itself.
2. **It's a starting point, explicitly.** The README says so, and the repo ships a [`CLAUDE.md`](https://github.com/Goblinmine/homelab-diagram/blob/main/CLAUDE.md) with everything an AI agent needs to adapt it to *your* lab: how the code is structured, which layout bits are hardcoded, the questions to ask about your network, and the render-and-check loop.
3. **The diagram is AI-native.** The author built it *with* Claude Code — described what they wanted, gave feedback on every render, and Claude wrote the code. That means the whole workflow is designed to be extended the same way: clone it, open it with Claude Code, say "help me make this diagram for my homelab," and it interviews you about your network, rewrites `inventory.yaml`, adapts `build.py`, and iterates.

So the realistic framing: **homelab-diagram is the reference implementation and the design language for homelab diagram-as-code.** You're not adopting a finished product; you're adopting a *technique* with a stellar example. For a lot of people, that's better — you get the design conventions without inheriting someone else's topology as a straitjacket.

---

## Making It Work For Your Lab

Here's the pragmatic path, whether you're adapting homelab-diagram directly or just stealing its ideas.

### If you want the exact look, adapt the repo

The requirements are modest: Python 3.11+ with PyYAML and Pillow, `rsvg-convert` (librsvg) for PNG export, and the Fira Sans / Fira Code fonts. On most systems:

```bash
# Arch/CachyOS
pacman -S python-yaml python-pillow librsvg ttf-fira-sans ttf-fira-code
# Debian/Ubuntu
apt install python3-yaml python3-pil librsvg2-bin fonts-firacode
# macOS
brew install librsvg
brew install --cask font-fira-code font-fira-sans
```

Then clone, fill in your `inventory.yaml`, and start the render-and-check loop. The layout coordinates live in `build.py` (the README points you to `fy, fh`, `ox, oy`, `bx, by`, `DY`, `MAD = …`), and that's where you'll spend most of your time making boxes fit *your* topology.

A genuinely nice touch: **redaction is built in.** By default the tool replaces your real domain with `redacted.com` and gives SSIDs generic names, so you can post the PNG to r/homelab without leaking your internal naming. Run `build.py --unredacted` for the private version with real values. That's a small feature that shows the author *thought about the actual workflow* — you want to show this off, not dox yourself.

### If you want the look without the geometry fight

The hand-placed-coordinates model is honest but labor-intensive. If your goal is "a clean r/homelab-style diagram of *my* network, today, without editing Python," that's the gap we've been filling with our own **[Homelab Diagram Generator](https://devhandbook.io/homelab-diagram-generator/)** — a free, in-browser tool that takes a plain-text inventory of your router, switch, NAS, Proxmox host, and clients and auto-layouts them into an SVG you can export. It's the same *idea* (text in, diagram out) with the *layout* automated, and nothing leaves your browser.

The two tools are complementary, not competing: homelab-diagram gives you the full-fidelity, hand-tuned, every-VLAN-bar-and-TrueNAS-vdev diagram for when you want to impress the subreddit; the generator gives you the 30-second diagram for when you just need to see your topology. Different jobs, same philosophy.

---

## The Bigger Picture: Your Documentation Should Be Code

Zoom out and homelab-diagram is one data point in a trend that's been building for a while: **your homelab's documentation is becoming code.**

Think about what a good homelab actually is in 2026. It's a Proxmox host. A stack of containers defined in a `docker-compose.yml`. An *arr pipeline. A VPN tunnel. A pile of hardware. And increasingly, all of it — *all* of it — is describable in text files that live in git. The Compose file is text. The inventory is text. The firewall rules are text. The diagram was the last holdout, and homelab-diagram just made it text too.

The payoff compounds. Once your diagram is generated from an inventory instead of drawn by hand, you get:

- **Accuracy that survives change.** Re-render beats re-draw every time.
- **Diff history.** `git log` on your diagram is a changelog of your network.
- **Reviewability.** Someone can actually review a topology change as a PR.
- **Reuse.** The inventory that draws the diagram can drive other things — monitoring, provisioning, a topology audit.
- **Shareability.** A redacted, reproducible diagram is exactly the kind of thing r/homelab and your blog want, and you can post it without leaking your internals.

That last one is worth underlining, because it's why homelab-diagram went viral: **the artifact is inherently shareable.** A diagram that renders from a clean, redacted YAML file is *begging* to be posted. It's the self-hoster's version of "look at my setup," and the tool makes it trivially safe to do.

---

## What I'd Actually Recommend

If you've been putting off diagramming your homelab (and you have been — everyone has), here's the concrete plan:

1. **Start with a quick auto-layout** to get a sense of your topology on screen — our [Homelab Diagram Generator](https://devhandbook.io/homelab-diagram-generator/) does this in 30 seconds from a text inventory.
2. **Clone homelab-diagram** and study the `inventory.yaml` and `build.py` — even if you never ship it, the design conventions (line width = speed, VLAN bars, trunk rendering, device-card layout) are the best-documented set of homelab-diagramming rules I've seen.
3. **If you want the full-fidelity version**, adapt it — ideally with Claude Code, since the repo ships a `CLAUDE.md` purpose-built for that loop, and the author built it that way.
4. **Commit the inventory and the diagram to git.** That's the whole point. Once it's code, it stops drifting.
5. **Post the redacted render to r/homelab.** That's the fun part, and the tool is designed for exactly that.

The days of hand-drawing your homelab in draw.io are numbered, and homelab-diagram is the proof. Diagram-as-code has come for the network diagram, and — like every other corner of infrastructure it's reached — it's strictly better once you make the switch.

---

*Built a diagram of your own lab with homelab-diagram, or adapted it to a topology that fought back? I'd genuinely like to see it — find me on [GitHub](https://github.com/Bryanmoon19) or drop a comment below.*
