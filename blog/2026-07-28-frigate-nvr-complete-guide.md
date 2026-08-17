---
layout: post.njk
title: "Frigate NVR Complete Guide 2026: Build a Privacy-First Security Camera System"
date: 2026-07-28
description: "Tired of cloud cameras uploading your porch to someone else's server? Build a self-hosted Frigate NVR with a Coral TPU for $200 — no subscriptions, real object detection, full Home Assistant integration."
tags: ["frigate", "nvr", "home-assistant", "self-hosted", "homelab", "security-cameras", "coral-tpu"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/frigate-nvr-complete-guide"
---

Last year, Eufy got caught sending unencrypted camera thumbnails to the cloud — even when users had "local-only" mode enabled. Ring has been sued for letting employees peek at customer footage. Nest now requires a subscription to unlock the features that used to be free.

I've been running Frigate in my own homelab for two years across six cameras. It costs me $0/month, never phones home, and detects a person walking up my driveway with less than 200ms of latency — all on a $60 USB stick. This guide is everything I wish I'd known before I started: hardware, cameras, the Coral TPU debate, Docker Compose, Home Assistant integration, and the gotchas that will eat your weekend if you don't know about them.

If you want to skip the YAML headache, I built a free [Frigate Config Builder](https://devhandbook.io/tools/frigate-config-builder/) that generates your `config.yml` in about 5 minutes. Drop in your cameras, pick your Coral, and you get a production-ready file. We'll reference it throughout this guide.

## What Is Frigate?

Frigate is an open-source NVR (network video recorder) built specifically for real-time AI object detection. Unlike ZoneMinder or Blue Iris, Frigate was designed from the ground up around machine learning inference — it uses TensorFlow Lite to detect people, cars, animals, packages, and dozens of other object types *on every frame* without melting your CPU.

The killer feature is the architecture. Most NVRs decode each camera stream once for recording and again for motion detection. Frigate decodes once and runs everything — recording, motion zones, object detection, even MQTT events — off the same decoded frames. On my 6-camera setup, this keeps CPU usage under 15% on a modest Intel N100.

**What Frigate actually does:**

- Detects 80+ object types (COCO dataset) with sub-300ms latency
- Records continuously, on motion, or on object detection
- Runs object detection on a Coral TPU for ~5W of additional power draw
- Streams to Home Assistant via MQTT with rich metadata (bbox, score, label)
- Exposes a clean web UI for live view, timeline, and event review
- Supports RTSP, RTMP, and HTTP/HLS camera streams
- Integrates with Home Assistant's `camera`, `motioneye`, and `frigate` integrations
- Ships with a built-in recording database (SQLite + MariaDB option)

**What Frigate doesn't do:**

- It's not a VMS with multi-user permissions, audit logs, or enterprise features
- There's no native mobile app (use the companion app, or HA's camera tile)
- Multi-server clustering is limited — one Frigate instance handles ~20 cameras comfortably

For homelab use, none of those limitations matter. For a 50-camera commercial install, look at Milestone or Genetec instead.

## Why Frigate Beats Cloud Cameras

The cloud camera market is a slow-motion privacy disaster. Here's what you're actually buying when you pay $10/month for a Ring or Nest subscription:

| What you get | What you give up |
|---|---|
| 30-60 days of cloud storage | Your footage lives on Amazon/Google servers |
| "Smart" person detection | Subject to model updates you don't control |
| Mobile push notifications | Subscription required for basic features |
| Easy multi-user sharing | EULA allows vendor access to your streams |
| Works without port forwarding | Vendor can disable your cameras remotely |

Frigate flips this. Every byte of footage stays on your hardware. Detection runs locally. MQTT events trigger your automations locally. The only network traffic is the initial RTSP handshake to your cameras and your remote access (Tailscale, Cloudflare Tunnel, WireGuard — your choice).

**The real benefit is integration.** When Frigate detects a person at my front door, it triggers:

- A Telegram snapshot to my phone (only if no one is home)
- A 10-second clip saved to /mnt/surveillance/front-door/
- The porch light to turn on at 30% brightness
- The Home Assistant alarm to arm "Stay" mode automatically
- A log entry in Loki tagged with confidence score

You cannot build this with Ring. You can build it in an afternoon with Frigate + Home Assistant + Node-RED.

## Hardware Requirements: The Real Numbers

Let's skip the "minimum requirements" marketing and talk about what actually works.

### The Server

Frigate runs anywhere Docker runs. The Coral TPU offloads object detection, so CPU requirements are modest.

| Server | RAM | Cameras | Notes |
|---|---|---|---|
| **Raspberry Pi 4 (8GB)** | 8GB | 1-2 | Marginal. CPU struggles at >1080p |
| **Raspberry Pi 5 (8GB)** | 8GB | 2-4 | Solid for low-FPS setups |
| **Intel N100 mini PC** | 16GB | 4-8 | Sweet spot. My current setup |
| **Intel N305 / i5-1240P** | 16GB+ | 8-16 | Overkill unless you're recording 4K |
| **Old desktop with GPU** | 16GB+ | 8-20 | Use NVIDIA GPU for detection instead of Coral |

**My actual setup:** A Beelink EQ14 (Intel N100, 16GB RAM, 500GB NVMe) running Proxmox. Frigate runs in an LXC container with 4GB RAM and 4 cores. Six 1080p cameras record continuously to a 2TB NVMe mirror. Coral USB attached via passthrough. Total idle CPU: 8%. Peak during person detection: 35%.

### The Coral TPU: USB vs M.2 vs PCIe

This is the decision that confuses everyone. Let me make it simple.

**Google Coral USB Accelerator (~$60)**

The easiest entry point. Plugs into any USB 3.0 port. Runs MobileNet-SSD at ~10ms per frame. This is what 90% of homelab users should buy.

**Google Coral M.2 Accelerator (~$60)**

Same chip as the USB version, but in M.2 form factor. Needs an M.2 A+E or B+M key slot. Slightly lower latency than USB due to PCIe. Good if your motherboard has a free slot.

**Google Coral M.2 Accelerator with Dual Edge TPU (~$120)**

Two TPUs on one board. Effectively 2x detection throughput. Useful if you're running 10+ cameras or pushing 4K streams. Otherwise overkill.

**PCIe Coral (out of production)**

Hard to find in 2026. Skip.

**NVIDIA GPU (alternative)**

If you already have a CUDA-capable GPU, Frigate supports OpenVINO and TensorRT for detection. An RTX 3060 handles 20+ cameras at 1080p. But the power draw (150W+) makes the Coral a no-brainer for most setups.

**My recommendation:** Start with the **USB Coral**. If you outgrow it, add a second one or move to the dual M.2. Don't buy the PCIe version unless you're scavenging eBay.

### Storage

A single 1080p camera at 15 FPS generates ~6 GB/day when recorded continuously with H.265. Six cameras for 30 days: ~1.1 TB. Use H.265-capable cameras and configure Frigate's `record` retention wisely.

For most homes, a 2TB NVMe SSD or a 4TB surveillance-rated HDD is plenty. I use a Seagate SkyHawk 4TB — they're rated for 24/7 write workloads and cost ~$90.

### Cameras: What Actually Works

Frigate speaks RTSP, so almost any IP camera works. But some cameras are dramatically better than others for AI detection.

**Tier 1 — What I actually recommend:**

- **Reolink RLC-810A / RLC-520A** — $50-80, 4MP/5MP, H.265, RTSP, ONVIF, PoE. The default recommendation in r/selfhosted for good reason.
- **Reolink Doorbell (PoE version)** — $150, integrates beautifully with Frigate, RTSP support, no subscription required.
- **Amcrest IP5M-T1179E** — $80, 5MP, vandal-rated, great low-light. ONVIF compliant.

**Tier 2 — Solid alternatives:**

- **Hikvision DS-2CD2xxx series** — Excellent image quality, cheap on eBay, but disable Hik-Connect cloud features.
- **Dahua IPC-HDW2xxx series** — Same OEM lineage as Hikvision, slightly different firmware. Same advice: disable cloud.

**Avoid:**

- **Wyze, Eufy, Aqara, Ring, Nest, Arlo** — Cloud-dependent, no real RTSP, or RTSP locked behind subscriptions. The opposite of what you want.
- **"Smart" Wi-Fi cameras** — Cloud AI features mean nothing if Frigate can't access the stream.
- **Reolink Argus / battery cameras** — Battery-powered means Frigate can't stream continuously. Use them only for spots without power.

**Affiliate disclosure:** Some links in this section are Amazon affiliate links. If you buy through them, I earn a small commission at no cost to you. I only link to cameras I've actually tested or that have proven track records in the Frigate Discord and r/selfhosted communities.

**Camera placement tips:**

- Mount cameras 8-10 feet high, angled slightly downward
- Avoid direct sunlight — IR detection at night is useless if the lens is blown out during the day
- Use PoE wherever possible (one cable for power + data, more reliable than Wi-Fi)
- Configure a static IP for each camera outside your DHCP range

## Installation: Two Real Options

You have two production-ready paths: Docker Compose (anywhere Docker runs) or the Home Assistant add-on (tightest HA integration). Pick one.

### Option A: Docker Compose

This is the most flexible setup. Works on bare metal, VMs, Proxmox LXC (with nesting), and even Synology/QNAP.

Create `/opt/frigate/docker-compose.yml`:

```yaml
name: frigate

services:
  frigate:
    container_name: frigate
    privileged: true  # Required for Coral USB passthrough
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "512mb"  # Increase if you have many cameras
    ports:
      - "5000:5000"   # Frigate web UI
      - "8554:8554"   # RTSP re-stream for HA
    volumes:
      - ./config:/config
      - ./storage:/media/frigate
      - /etc/localtime:/etc/localtime:ro
    devices:
      - /dev/bus/usb:/dev/bus/usb  # Coral USB passthrough
    environment:
      - FRIGATE_RTSP_PASSWORD=your-secure-password
```

Then:

```bash
cd /opt/frigate
docker compose up -d
```

The web UI is at `http://your-server:5000`. The first start downloads the detection model (~30MB) and warms up the Coral. Give it 2 minutes before you panic.

### Option B: Home Assistant Add-on

If you're already running Home Assistant OS or HA Supervised, the add-on is the path of least resistance.

1. Add `https://github.com/blakeblackshear/frigate-hass-addons` as a custom repository in the Add-on Store
2. Install "Frigate" (the full version with MQTT broker, or use your existing one)
3. Configure via the add-on's UI tab
4. Install the "Frigate" Home Assistant integration via HACS

This is what I run in production. The HA integration auto-discovers cameras, creates entities for each object type, and exposes the RTSP re-stream directly. Zero reverse proxy configuration needed.

## Configuration: A Real `config.yml`

Here's a stripped-down but production-ready config for a 2-camera setup with a Coral USB:

```yaml
{% raw %}
mqtt:
  enabled: true
  host: 192.168.1.46  # Your MQTT broker (Home Assistant Mosquitto)
  port: 1883
  topic_prefix: frigate
  client_id: frigate
  stats_interval: 60

detectors:
  coral:
    type: edgetpu
    device: usb  # or 'pci' for M.2/PCIe

cameras:
  front_door:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.1.51:554/h264Preview_01_main
          roles:
            - detect
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
      fps: 5  # 5 FPS is plenty for detection; full FPS comes from record
    record:
      enabled: true
      retain:
        days: 14
        mode: motion  # 'all', 'motion', or 'active_objects'
      events:
        retain:
          default: 30
          mode: active_objects
    objects:
      track:
        - person
        - car
        - package
      filters:
        person:
          min_score: 0.6
          threshold: 0.7
    zones:
      porch:
        coordinates: 0,720,1280,720,1280,100,0,100
        objects:
          - person

  driveway:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://admin:password@192.168.1.52:554/h264Preview_01_main
          roles:
            - detect
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
        - car
        - truck
{% endraw %}
```

Save this as `/opt/frigate/config/config.yml` (or `/config/frigate/config.yml` for the HA add-on). Restart Frigate and check `http://your-server:5000` — you should see both cameras streaming live.

**Don't want to write YAML by hand?** The [Frigate Config Builder](https://devhandbook.io/tools/frigate-config-builder/) generates this file from a form. Pick your cameras, your Coral type, your detection zones, and download a ready-to-deploy `config.yml`.

### Key Configuration Concepts

These four sections cover 90% of what you'll touch:

**`detectors`** — Defines your inference hardware. `edgetpu` is the Coral; `cpu` falls back to ONNX/CPU (slow). You can run multiple detectors and split cameras between them.

**`cameras`** — One block per camera. Each has `ffmpeg.inputs` (stream URLs), `detect` (resolution + FPS for inference), and `record` (what gets saved). Lower detect resolution = less CPU; lower detect FPS = less Coral load.

**`objects.track`** — Which COCO classes to track. Tracking all 80 classes is wasteful. Track what matters: `person`, `car`, `dog`, `cat`, `package`, `truck`. Use `objects.filters.<class>.min_score` and `.threshold` to cut false positives.

**`zones`** — Polygon regions inside a camera frame. A "porch" zone might be the area where packages get delivered. You can scope detection per zone — useful for ignoring cars on the street while catching people in the yard.

## Home Assistant Integration

Frigate was built for Home Assistant. The integration is the best part of the whole stack.

### Install via HACS

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add the Frigate integration: HACS → Integrations → search "Frigate"
3. Restart Home Assistant
4. Settings → Devices & Services → Add Integration → Frigate
5. Point it at your Frigate URL (`http://frigate:5000` if HA add-on, or your server IP)

### What You Get

After setup, HA creates:

- A `camera.<name>` entity per Frigate camera (live view + object overlay toggle)
- `binary_sensor.<name>_<object>` for each tracked object type per camera
- `sensor.<name>_person` with count, last seen, and confidence
- The `frigate` integration card for the Lovelace UI

### Automations That Actually Help

Here's a real automation I run:

```yaml
{% raw %}
automation:
  - alias: "Front Door Person Detection"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door_person
      to: "on"
    condition:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "disarmed"
    action:
      - service: telegram_bot.send_photo
        target:
          entity_id: camera.front_door
        data:
          caption: "Person at front door ({{ now().strftime('%H:%M') }})"
      - service: light.turn_on
        target:
          entity_id: light.porch
        data:
          brightness_pct: 30
{% endraw %}
```

When a person appears, the porch light turns on and I get a Telegram snapshot. No cloud involved. Latency from object detection to HA automation: ~400ms.

### Performance Tip: Use the Re-stream

Frigate's `8554:8554` RTSP port lets you re-stream each camera through Frigate instead of HA connecting directly to the camera. This decouples HA from camera credentials and adds a clean buffer. Enable `rtsp` in the Frigate HA integration config.

## Troubleshooting: The Gotchas That Will Eat Your Time

Here are the issues I see in the Frigate Discord weekly, in order of frequency.

### 1. "Coral Not Detected"

Check `lsusb` on the host. You should see `Google, Inc. Coral Edge TPU`. If you don't:

- Try a different USB port (USB 3.0 blue ports, not 3.2)
- Replace the cable (some USB-C docks don't supply enough power)
- Add `udev` rules: `echo 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a6e", ATTRS{idProduct}=="089a", MODE="0666"' | sudo tee /etc/udev/rules.d/71-edgetpu.rules && sudo udevadm control --reload-rules`
- If running in Proxmox LXC, add `lxc.cgroup2.devices.allow: c 189:* rwm` to the container config

### 2. "High CPU Usage, Detection Lag"

Lower `detect.fps` from 10 to 5. Lower `detect.width`/`detect.height` from 1920×1080 to 1280×720. Detection scales with pixel count, not stream count.

### 3. "Too Many False Positives"

Add object filters. A `person` filter with `min_score: 0.6` and `threshold: 0.7` cuts most trees-shaded-as-people issues. Create a zone that excludes public walkways if your camera sees the street.

### 4. "Recordings Not Saving"

Check the `record.retain.days` value vs. disk space. Frigate uses ~70% of available storage by default. On the HA add-on, recordings live at `/media/frigate/clips/` — make sure your storage backend is mounted.

### 5. "Home Assistant Can't Connect"

Check that the Frigate container's hostname resolves from HA. If using Docker Compose on a separate host, point HA at the server IP (`http://192.168.1.20:5000`). If using HA add-on, use `http://ccab4aaf-frigate:5000` (replace the prefix with your add-on slug).

### 6. "Notifications Fire Constantly"

You forgot `threshold`. Without it, Frigate fires on every frame a person appears in. Set `threshold: 0.7` (the score needed across N frames before triggering) to suppress flicker.

## What I'd Build Next

Frigate is the centerpiece of a privacy-first security stack. Add these and you've replaced Ring Protect:

- **Tailscale** for remote access (no port forwarding, no Cloudflare middleman)
- **Scrypted** if you have any HomeKit cameras you want Frigate to consume
- **Paperless-ngx** for OCR-ing license plates from `car` events
- **Node-RED** for complex automations beyond HA's YAML reach
- **MinIO** if you want off-site encrypted backup of critical clips

I've been running this stack for two years. Zero cloud dependencies. Zero monthly fees. When my internet went down for 6 hours last winter, the cameras kept recording, the automations kept firing locally, and I got a Telegram snapshot the moment the UPS kicked in. That's the whole point.

## Try the Config Builder

If you've read this far and are about to spin up Frigate, save yourself an hour. The [Frigate Config Builder](https://devhandbook.io/tools/frigate-config-builder/) walks you through the same fields covered in this post and spits out a tested `config.yml` you can drop straight into `/config/`. It handles the Coral selection, camera RTSP URLs, zone polygons, object filters, and record retention. No YAML knowledge required.

Once you're running Frigate, drop a comment on the [r/selfhosted Frigate megathread](https://www.reddit.com/r/selfhosted/) with your setup. The community is genuinely helpful and your config questions will get answered within hours. Or if you run into something not covered here, hit me on the [devhandbook.io Discord](https://discord.gg/devhandbook) — I monitor the #frigate channel.

Now stop renting your own security footage. Build it once, own it forever.