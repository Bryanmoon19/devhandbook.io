---
layout: post.njk
title: "Outbound Firewall for Your Homelab: See & Block Every Connection"
date: 2026-11-07
description: "Your router blocks inbound traffic. It does nothing about the dozens of devices silently phoning home. Snitch (814★) and the new wave of egress-control tools finally give homelabbers a way to see and block every outbound connection — privacy-first, local-first, no telemetry."
tags: ["snitch", "opensnitch", "egress", "firewall", "network-security", "privacy", "self-hosting", "homelab", "little-snitch", "monitoring", "security"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/outbound-firewall-homelab-snitch"
---

Every homelabber spends hours on the *inbound* side of their network. You close ports, set up Cloudflare Tunnels instead of port forwarding, bolt Tailscale onto everything, and configure fail2ban to kick brute-forcers. You've read a dozen guides on keeping the bad guys *out*.

But here's the question almost nobody asks: **what's already inside, and who is it talking to right now?**

Your router's firewall is a bouncer at the front door. It does almost nothing about outbound traffic. Every smart TV, every IoT bulb, every Docker container, every phone on your Wi-Fi — they all make outbound connections constantly. Some are legitimate. Some are telemetry you never agreed to. Some are a compromised device quietly establishing a command-and-control channel.

Inbound security tells you who's knocking. **Egress control tells you who's already inside and who they're calling.**

The good news: there's a new wave of tools built exactly for this, and the best one just crossed 800 stars. It's called **Snitch**, and it's the missing half of homelab security.

---

## The Egress Blind Spot (Why Inbound Isn't Enough)

Most homelab security is built on a single assumption: the threat is *outside*, trying to get *in*. So you harden the perimeter and call it a day.

But consider what actually happens in the real world:

- **Your smart TV ships with telemetry baked in.** It phones home with your viewing habits, and you never see it because it's outbound and your router doesn't block it by default.
- **An IoT device gets compromised** (or ships compromised, like the 400,000+ devices in one recent botnet). It doesn't need an inbound port — it makes an *outbound* connection to its controller.
- **A Docker image pulls something unexpected.** It runs fine, no ports exposed, but it's beaconing to an unfamiliar IP on a regular interval — the classic C2 signature.
- **A "free" app on your laptop** is quietly exfiltrating data. You'd never know, because outbound traffic is invisible by default.

The security industry has a word for this: **egress filtering.** Enterprise networks have done it for years. Homelabs, historically, haven't had good tools for it — which is strange, because the homelab is *exactly* the kind of heterogeneous, mixed-trust network where you most want to know what's calling home.

The tools are finally here, and they're good.

---

## Meet Snitch: The Little Snitch for Your Whole Network

[**Snitch**](https://github.com/aixisstudio/Snitch) (814★, AGPL-3.0) is an open-source application firewall and real-time network monitor. If you've used Little Snitch on macOS or OpenSnitch on Linux, you know the concept: **see every connection your machine makes — who it talks to, where they are, and which app is responsible — then block the ones you don't trust.**

The difference is that Snitch pulls it off cross-platform, fully open-source, and privacy-first to a degree that's almost refreshing to read in a README.

Here's the honest pitch from its own docs, and it matters:

> **vs Little Snitch / Lulu** — same idea, but Snitch is cross-platform, free and open-source. Blocking is orchestrated through the OS-native firewall (`netsh` / `iptables` / `pf`) — Snitch never filters in user-space.
> **vs GlassWire** — Snitch is free, open-source, requires no account and makes **no outbound calls without opt-in**; even geolocation is offline.
> **vs cloud-based monitors** — everything runs on `127.0.0.1` behind a token; your traffic data never leaves the machine.

That last point is the one that should make every homelabber sit up. Most network-monitoring tools are *themselves* a privacy problem — they ship your traffic metadata to a cloud dashboard you don't control. Snitch's entire design is built around the opposite promise: **your traffic data never leaves the machine.** No telemetry. No account. Every outbound call (threat-intel lookups, webhooks, update checks, even downloading a fresh GeoIP database) is explicitly opt-in.

For a community that just spent a decade learning to distrust cloud dependencies, that's the correct default.

---

## What You Actually See

The first time you fire it up, Snitch drops you into a **live force graph**: your machine at the center, every outbound connection rendered as a node, connected by animated arcs. It's the thing a screenshot can't quite capture — the sudden, slightly unnerving realization of *how much* your supposedly-idle machine is actually doing.

From there, the feature set is deep:

- **World map** — geolocated IPs on an interactive globe, with the catch that geolocation is *offline only* (bundled DB-IP Lite database, no network lookups).
- **Process attribution** — know *which app* generates *which* traffic, with a per-app view of destinations, volumes, and 60-minute history.
- **Anomaly detection** — flags port scans, beaconing (regular-interval C2), and potential exfiltration. It also has DNS-tunneling heuristics, cleartext-port spotting, and per-app country-baseline deviation.
- **ML anomaly scoring** — a pure-Python isolation forest over your own flows (zero dependencies), flagging outlier flows after ~400 samples.
- **Passive TLS inspection** — reads leaf-certificate metadata off the wire (issuer, self-signed, SAN/SNI mismatch). Honest about TLS 1.3 being unobservable.
- **Lockdown mode** — a panic switch that flags and blocks all public outbound traffic while keeping LAN + loopback alive.
- **Actionable alerts** — one-click Block IP / Kill / Suspend on every alert, with custom rules that auto-firewall matched hosts.

The headline feature for homelabbers is **Ask-on-Connect**, an opt-in NFQUEUE verdict mode on Linux: new flows are held until you explicitly allow or deny them, exactly like Little Snitch's prompts — except now it's available on your headless server, not just your Mac.

---

## Installing It (Mac, Linux, or Windows)

Snitch runs natively on all three platforms, plus a headless daemon for servers and VMs.

**macOS (Apple Silicon):**

```bash
brew install --cask aixisstudio/tap/snitch
```

**Linux (AppImage / deb / rpm / snap), or Docker:**

```bash
sudo docker run --network host --cap-add NET_ADMIN --cap-add NET_RAW \
  -v snitch-data:/app/data ghcr.io/aixisstudio/snitch
```

> **Note:** Docker Desktop on macOS/Windows runs inside a VM and can't capture host traffic — use the native Electron app there. On Linux, the Docker container uses `network_mode: host` so it sees real traffic.

**Headless (servers/VMs, no GUI):**

```bash
brew install aixisstudio/tap/snitch   # then run `snitchd`
```

**Windows:** A one-click NSIS installer (requires Npcap), plus a `Snitch-Lite-Setup` for a backend + browser UI.

The stack itself is worth a glance, because it's a good sign of engineering quality: `libpcap`-based capture with its own packet parser (IPv4/IPv6/TCP/UDP/DNS/TLS-SNI), a FastAPI backend with WebSockets and SQLite storage, a React 19 + D3.js front end, and an Electron desktop wrapper. Data is held in a local `snitch.db` with a 24-hour sliding retention window by default.

---

## The Egress-Control Wave (Snitch Isn't Alone)

Snitch is the newest entry in a category that's been quietly maturing for years. If you're evaluating options, here's the landscape:

| Tool | Platform | Stars | Notes |
|------|----------|-------|-------|
| **Little Snitch** | macOS | — | The original, commercial. The gold standard, but paid and Apple-only. |
| **OpenSnitch** | Linux | ~14.2k | The established FOSS Linux application firewall, inspired by Little Snitch. |
| **Lulu** | macOS | — | Free, open-source Little Snitch alternative by Objective-See. |
| **Snitch** | Cross-platform | 814 | The new one: FOSS, cross-platform, privacy-first, fleet agent. |
| **PureSnitch** | macOS | 214 | Free SwiftUI Little Snitch alternative, zero telemetry, pf-based. |

The through-line is the same across all of them: **treat your own devices as a threat surface, not a trusted zone.** The inbound-only mindset assumes everything inside your network is yours and trustworthy. Egress tools start from the opposite assumption — *verify what's actually happening, then decide what to allow.*

Snitch's specific contribution to the wave is threefold: it's genuinely cross-platform (OpenSnitch is Linux-only, Little Snitch is macOS-only), it's aggressively privacy-first (which distinguishes it from the freemium GlassWire model), and it ships a **Rust fleet agent** with optional SIEM exports — meaning you can run it across multiple machines and centralize the *alerts* without centralizing the *data* in a third party's cloud.

---

## Why Privacy-First Matters More Than Ever Here

There's a subtle irony worth naming: **a network-monitoring tool can be its own worst privacy violation.**

Think about it. A tool that sees every connection your devices make is, by definition, a tool that could *report* every connection your devices make. If that data flows to a vendor's cloud dashboard, you've solved one surveillance problem by creating another — you now have a company that knows, with perfect fidelity, everything your network does.

Snitch's answer is the right one and it's worth internalizing as a design principle, not just a feature list:

- **Loopback-only by default.** The API binds to `127.0.0.1` in every mode, behind a per-launch token.
- **Offline geolocation.** No online lookups. The GeoIP database ships with the app.
- **No telemetry.** Every outbound call — threat intel, webhooks, update checks — is opt-in, documented in `PRIVACY.md`.
- **No central server.** Even the optional IOC peer-sync exchanges *hash commitments only*, between explicitly-paired peers.

For a community that runs its own DNS (Pi-hole/AdGuard), its own VPN (WireGuard/Tailscale), and its own storage, a network monitor that phones home to someone else's cloud would have been a non-starter. Snitch gets that right out of the gate.

---

## Where It Fits in Your Homelab

Here's how I'd slot egress control into an existing homelab, in order of effort:

**1. Start with your most exposed machine.** Run Snitch on your daily-driver Mac or the box you SSH into everything from. Just *watch* for a week. You will be surprised by what phones home. This is the highest-value, lowest-effort step — visibility alone changes how you think about your network.

**2. Add the headless daemon to servers.** `snitchd` on your Proxmox host or a key LXC gives you per-app outbound visibility on machines that don't have a GUI. Combine with the opt-in syslog/SIEM export if you run Wazuh or a similar collector.

**3. Enforce, don't just observe.** Turn on Ask-on-Connect on Linux for the machines you can tolerate prompts on, or lean on the firewall orchestration — block rules for IP/CIDR/domain/process/port, applied to the OS firewall and persisted. Start with a denylist of known-telemetry hosts, then graduate to a default-deny posture on a per-machine basis.

**4. Keep Lockdown mode in your back pocket.** The day you *need* it — a suspicious beacon, a compromised container, an odd upload spike — is exactly when you'll be glad one click can flag and block all public outbound traffic while keeping LAN alive.

**5. Layer it with your existing inbound controls.** Egress visibility is *complementary* to everything you already run. Pi-hole blocks DNS lookups but won't catch a device using a hardcoded IP. A Cloudflare Tunnel protects inbound but says nothing about what your services are doing *out*. Snitch fills the gap those tools leave open.

---

## The Honest Caveats

No tool is a silver bullet, and Snitch's own docs are refreshingly candid about limits:

- **TLS 1.3 is genuinely unobservable.** Passive TLS inspection reads cert *metadata* off the wire, but the payload of modern encrypted connections is encrypted — no user-space tool can see inside it. Egress control answers *who* and *where* and *how often*, not *what* is being sent.
- **Firewall rules are best-effort.** The backend drives the OS firewall; when privileges are missing, a rule is kept for *visibility* (you'll see `BLOCKED_ATTEMPT` alerts) and marked "not applied" rather than pretending. Good engineering, but worth knowing.
- **Encrypted-looking payloads on cleartext channels** get flagged as a *heuristic*, not a verdict. The entropy-watch and anomaly scoring are signals to investigate, not proof.
- **Docker Desktop can't capture host traffic.** On macOS/Windows you want the native app; the container is a Linux-server thing.

None of these undermine the core value. They're honest boundaries on a tool that's fundamentally about *visibility first, enforcement second.*

---

## The Bottom Line

For years, homelab security has been a story about the perimeter: close the ports, tunnel the traffic, harden the reverse proxy. That work matters, and it's not done — but it's only half the picture.

The other half is the one Snitch and its peers finally make tractable: **what your own devices are doing when you're not looking.** Every smart TV phoning home, every IoT gadget beaconing, every container making a connection you never approved — visible, attributable to a specific process, and blockable with one click. All of it local, open-source, and telemetry-free.

That's the quiet promise of the egress-control wave, and it's the closest thing the homelab has to a "set it and forget it" answer to the question nobody was asking loudly enough: *who's already inside, and who are they calling?*

Install Snitch on one machine this weekend and let it watch for a week. You'll probably learn something about your network you'd rather have known.

---

**Related posts:**
- [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/cloudflare-tunnels-homelab-guide/)
- [WireGuard + Pi-hole: The Privacy Stack That Replaces Your ISP Router](/blog/wireguard-pihole-privacy-stack/)
- [Uptime Kuma vs Nezha: Homelab Monitoring Comparison](/blog/uptime-kuma-vs-nezha-monitoring-comparison/)

---

*Links: [Snitch on GitHub](https://github.com/aixisstudio/Snitch) · [Snitch docs](https://aixisstudio.github.io/Snitch/) · [OpenSnitch](https://github.com/evilsocket/opensnitch) · [Lulu](https://objective-see.org/products/lulu.html)*
