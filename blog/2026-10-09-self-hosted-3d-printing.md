---
layout: post.njk
title: "Self-Hosted 3D Printing: The Complete OctoPrint, Klipper, and Home Assistant Stack"
date: 2026-10-09
description: "Your printer is a Linux server you've been ignoring. Here's the full self-hosted stack — OctoPrint, Klipper + Moonraker, and Home Assistant integration — for turning a dumb 3D printer into a remote-controlled, monitored, automatable part of your homelab."
tags: ["3d-printing", "octoprint", "klipper", "moonraker", "home-assistant", "self-hosted", "homelab", "maker", "iot"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-3d-printing"
affiliate: true
---

I've written a lot on this site about the self-hosted stack — the media server, the LLM rig, the monitoring dashboard, the whole homelab. But there's one device sitting in most makers' homes that almost nobody thinks of as a server, even though it is one: **the 3D printer.**

Most printers ship as dumb appliances. You slice a file, copy it to an SD card, walk it over, and babysit the print for eight hours because you can't see it from your desk. But under the hood, a modern 3D printer is a Linux-capable microcontroller with USB, a serial console, and a job queue — and there's a mature, thriving ecosystem for putting it *on your network* and controlling it like any other self-hosted service.

This is a greenfield topic for me. I own the hardware, I've been running parts of this stack, and I've never written about it. So this is the deep-dive: OctoPrint for the plug-and-play route, Klipper + Moonraker for the performance route, and how to wire it all into Home Assistant so your printer becomes just another sensor in the house.

## Why Self-Host Your Printer at All?

The pitch is the same one that drives every other self-hosted project: **you own the hardware, so you should own the control plane.**

When you run a print through the manufacturer's cloud or a commercial slicer's remote queue, you're handing over a live video feed, your print job history, and your g-code to someone else's server. That's a camera pointed at your desk, phoning home. The self-hosted alternative keeps the feed, the queue, and the telemetry on a Raspberry Pi in your closet.

Beyond privacy, the practical wins are immediate:

- **Remote control** — start, pause, cancel, and monitor prints from anywhere on your LAN (or through a tunnel when you're out).
- **A camera + timelapse** — a live view and automatically assembled timelapses of every print, so you can see a spaghetti failure the moment it starts instead of six hours later.
- **Telemetry and history** — temperature curves, layer times, filament usage, and a searchable history of every job you've run.
- **Automation** — Home Assistant can pause the printer when the smoke alarm triggers, notify you when a print finishes, or turn on an enclosure fan based on chamber temperature.
- **Better firmware** — Klipper moves motion planning off the printer's weak MCU onto a real computer, which is a genuine quality-and-speed upgrade, not just a convenience feature.

If you already run a homelab, a 3D printer slots in naturally. It's a Linux box with a job queue and a sensor array — you already know how to run those.

## The Two Stacks, and Which One You Want

There are two mainstream approaches, and they answer different questions.

### OctoPrint: The Plug-and-Play Route

[OctoPrint](https://octoprint.org) is the original self-hosted printer server. It's a Python web app (with a plugin system) that runs on a Raspberry Pi, talks to your printer over USB serial, and gives you a web UI, a camera feed, g-code upload, and a REST API.

**Choose OctoPrint if:**
- You want the shortest path from "unboxed printer" to "controlled from my browser."
- You're happy with your printer's existing firmware and just want remote control + monitoring.
- You value the plugin ecosystem — OctoPrint has hundreds of plugins for filament tracking, octolapse timelapses, notifications, and integrations.

**The catch:** OctoPrint doesn't change how your printer *moves*. It feeds g-code to the stock firmware, so print quality and speed are whatever the manufacturer shipped.

### Klipper + Moonraker: The Performance Route

[Klipper](https://www.klipper3d.org) flips the architecture. Instead of letting the printer's tiny MCU do motion planning, Klipper runs the math on a real computer (again, a Raspberry Pi) and sends only the low-level step commands to the printer board. The MCU becomes a dumb actuator, and the Pi — with orders of magnitude more compute — does the heavy lifting.

**Choose Klipper if:**
- You want faster, higher-quality prints (input shaping and pressure advance are Klipper's killer features).
- You're willing to replace your printer's firmware (it's a well-trodden path, but it *is* a firmware flash).
- You want the most granular control over every aspect of the print.

**The catch:** Klipper itself is headless — no web UI. That's where [Moonraker](https://moonraker.readthedocs.io) comes in. Moonraker is the API server and web frontend layer that sits on top of Klipper, exposing a REST/WebSocket API that clients like [Mainsail](https://docs.mainsail.xyz) and [Fluidd](https://docs.fluidd.xyz) consume.

The two stacks aren't mutually exclusive — you can run OctoPrint *on top of* Klipper if you want the plugin ecosystem and the Klipper performance. But the modern, actively-developed path for a Klipper machine is **Mainsail + Moonraker**, which is what I'll focus on below.

## The Hardware: A Raspberry Pi and a Camera

You'll need a small Linux box to act as the printer's brain. The Raspberry Pi (3, 4, or 5) is the default choice and has the best-documented setup, but any old single-board computer or thin client works — this is not a heavy workload, especially for OctoPrint.

The other essential piece is a camera. Any USB webcam or the official Raspberry Pi Camera Module works. The camera is what turns "I can send g-code" into "I can *see* my print from bed," which is the difference between a convenient tool and a genuinely useful one.

**The minimum shopping list:**
- Raspberry Pi 4 (or better) + power supply + microSD card
- USB cable to connect the printer (check your printer's port — most use USB-B or USB-C)
- A USB webcam or Pi Camera Module
- Optional: a relay module if you want to cut printer power programmatically

## Setting Up the Stack

Here's the practical path. I'm going to give you the shape of it and point you at the canonical installers, because the exact steps drift with releases and the official docs are excellent.

### 1. Flash the Base OS

For Klipper-based setups, the community standard is **MainsailOS** — a pre-built Raspberry Pi OS image with Klipper, Moonraker, and Mainsail already installed and configured. Flash it to your SD card with Raspberry Pi Imager, boot the Pi, and you have a working Klipper web UI at `http://<pi-ip>/` with zero manual service setup.

For a pure OctoPrint install, flash **OctoPi** — the official OctoPrint image — the same way.

Both images do the "SSH enabled, Wi-Fi configured, service running" dance for you, which is 90% of the friction removed.

### 2. Flash Klipper Firmware to Your Printer

This is the one step that scares people, and it's the one that's actually well-documented. The short version:

1. In Mainsail, navigate to the config section and build the Klipper firmware for your specific printer board (it's a menu-driven config — select your MCU, build, and download a `.bin` file).
2. Put that `.bin` on an SD card and insert it into the printer — it flashes on boot, the same way you'd update stock firmware.
3. Add your printer's config file (there's a huge library of community-tested configs for almost every common printer).

The Klipper docs and the Mainsail docs both have step-by-step guides, and the printer-specific configs in the [Klipper sample configs](https://github.com/Klipper3d/klipper/tree/master/config) repository cover the popular models.

### 3. Configure Moonraker and Mainsail

If you flashed MainsailOS, this is already done. The key files live in `~/printer_data/config/`:

- `printer.cfg` — the main Klipper config (your printer's pins, geometry, and kinematics)
- `moonraker.conf` — the Moonraker API server config (auth, update management, webcam setup)

The two things you'll definitely want to configure are **authentication** (don't expose an unauthenticated printer control API, even on your LAN — a stuck print or a thermal runaway is a real hazard) and the **webcam**, so Mainsail shows a live feed and can assemble timelapses.

### 4. Dial In Input Shaping and Pressure Advance

This is where Klipper earns its keep. **Input shaping** cancels the vibration (ringing) in your prints by measuring your printer's resonant frequency with an accelerometer and compensating in firmware. **Pressure advance** tunes how the extruder handles the pressure at the nozzle, eliminating blobs and under-extrusion at corners.

Both require some calibration — print a test tower, measure, tweak a value — but the result is a printer that runs meaningfully faster *and* cleaner. This is the reason people put up with the firmware flash in the first place.

## Wiring It Into Home Assistant

Now the fun part: making your printer a first-class citizen of your smart home.

Home Assistant has official integrations for both stacks:

- **OctoPrint integration** — exposes the printer's state (printing, paused, idle), temperatures, progress, and lets you start/pause/cancel jobs. It also pulls in the camera feed.
- **Moonraker integration** — the Klipper equivalent, exposing the same state plus more granular telemetry (bed/nozzle temp, print speed, layer progress, print status).

Once integrated, your printer shows up as an entity with attributes like current temperature, target temperature, print progress percentage, and a "time remaining" estimate. From there, it's just Home Assistant — and this is where self-hosting the printer gets *interesting*.

### Automations Worth Building

**1. The "print finished" notification.** The canonical first automation. When the Moonraker state changes to `complete`, send yourself a notification (through Apprise, Gotify, or plain Home Assistant notifications) with the print name and time. No more wandering over to check if the bed's done.

**2. The smoke/fire safety kill-switch.** A 3D printer running unattended overnight is, frankly, a small fire risk. Wire a relay into the printer's power and add an automation: if the smoke detector triggers (or a temperature sensor near the printer spikes), cut power to the printer and notify you loudly. This is the single highest-value automation you can build around a printer.

**3. Enclosure temperature control.** If you print ABS or other temperature-sensitive filaments, an enclosure with a heater and fan — driven by Home Assistant based on a chamber temperature sensor — automates the part of printing that's otherwise fiddly manual work.

**4. Filament dry-box monitoring.** A cheap humidity sensor in your filament storage, surfaced in Home Assistant, tells you when your filament has absorbed too much moisture and needs drying. Wet filament is the most common cause of mysterious print quality problems.

**5. The "pause on door open" safety.** If your printer is in an enclosure with a door sensor, pause the print when the door opens mid-job (for some printers and some prints, this is a real safety and quality concern).

The through-line is the same as every Home Assistant project: once the printer exposes its state as entities, *everything* you already know how to do in Home Assistant becomes available to it.

## Security: Don't Expose Your Printer Blindly

This deserves its own section, because it's the part people get wrong.

A 3D printer is **not** a low-stakes device to expose to the network. Klipper and Moonraker can control a heated bed and a hotend — a misconfigured or malicious command can overheat the hotend and start a fire. The firmware has thermal-runaway protection, but you should treat printer access the way you'd treat access to a space heater you can trigger remotely.

**The rules:**

1. **Enable authentication.** Both Moonraker and OctoPrint support auth. Turn it on, and use a strong password. Never expose an unauthenticated printer API.
2. **Keep it on your LAN by default.** Don't forward the printer's port to the internet. If you need remote access, go through a tunnel (Cloudflare Tunnel, Tailscale, or WireGuard) so you get authentication and encryption for free.
3. **Separate the control plane from the physical device where you can.** A relay that can cut printer power is worth more than any password — it's a physical off switch.
4. **Update it.** Klipper, Moonraker, and OctoPrint are all actively developed and push security fixes. Moonraker in particular has an update manager built into Mainsail that makes this one click.

The same discipline you apply to your other homelab services applies here — arguably more, given the thermal element.

## The New-School Angle: Where This Is Heading

There's a newer signal worth paying attention to: the self-hosted 3D printing niche is spawning its own tooling. Projects like [prettypleaseprint](https://github.com/) — a fresh GitHub tool in the print-queue/automation space — are a sign that the ecosystem is maturing beyond the two big platforms. As Klipper's Moonraker API becomes the de facto standard, a whole generation of smaller tools is building on top of it: queue managers, fleet dashboards, AI print-failure detection, and multi-printer orchestrators.

That's the pattern that should look familiar if you've watched the rest of the self-hosted world grow. First the big, general platform (OctoPrint), then the high-performance core (Klipper + Moonraker), then a wave of specialized tools on top. The 3D printing stack is going through the same lifecycle the media-server stack and the LLM stack already went through — and it's a good time to get in.

## The Bottom Line

Your 3D printer is a server you've been treating like an appliance. The self-hosted stack — OctoPrint or Klipper + Moonraker + Mainsail — turns it into a remote-controlled, monitored, automatable part of your homelab, and Home Assistant makes it a sensor in your house like any other.

The split is simple: **OctoPrint** if you want the shortest path to remote control without touching firmware, **Klipper + Moonraker** if you want the performance upgrade (input shaping, pressure advance) and are willing to flash. Either way, put a camera on it, wire it into Home Assistant, and build the safety kill-switch *first* — everything else is gravy.

I'm going to be writing more about this as I build out my own setup — the specific configs, the input-shaping calibration, the automations that actually pay off. If you run a self-hosted print stack, I'd love to hear what's working for you. Find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.

---

*If you found this useful, you might also like my posts on [self-hosting an Immich photo library](/blog/2026-06-17-immich-photo-management-homelab/), the [Home Assistant local AI guide](/blog/2026-04-12-home-assistant-local-ai-agents/), and my [self-hosted weekly roundup](/blog/selfhosted-weekly-2026-10-05/).*
