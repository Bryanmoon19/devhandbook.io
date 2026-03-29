---
layout: post.njk
title: "Run TeslaMate on Proxmox LXC: The Complete Self-Hosted Tesla Dashboard"
date: 2026-03-29
description: "Step-by-step guide to running TeslaMate in a Proxmox LXC container with Docker Compose, PostgreSQL 17, and Grafana dashboards for tracking your Tesla's battery, trips, charging, and efficiency."
tags: ["teslamate", "tesla", "proxmox", "self-hosted", "homelab", "docker", "grafana"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/teslamate-proxmox-lxc"
---

If you own a Tesla and run a homelab, you've probably opened the Tesla app, stared at the battery percentage, and thought: *"That's it? That's all the data I get?"*

The built-in app gives you the basics — current charge, location, climate controls. But it tells you nothing about your long-term battery degradation, lifetime efficiency trends, how much you've actually spent on charging, or where you've driven over the past year. That data exists. Tesla just doesn't surface it.

[TeslaMate](https://github.com/teslamate-io/teslamate) fixes that. It's an open-source, self-hosted data logger that pulls everything from the Tesla API and stores it locally in PostgreSQL. Pair it with Grafana and you get gorgeous dashboards showing trip history, charging statistics, battery health over time, vampire drain, efficiency by temperature, geofence events — the works.

Here's how to get it running on Proxmox in a lightweight LXC container. I run this on my 2016 Model S with FSD, and it's been rock solid.

## Why LXC Instead of a Full VM?

**An LXC container gives you all the isolation you need at a fraction of the resource cost.** TeslaMate is a Docker Compose stack — it doesn't need a full kernel or dedicated hardware passthrough. A VM would work, but you'd be wasting RAM on a second kernel for no reason.

LXC containers share the host kernel, boot in seconds, and use significantly less memory. For Docker-based apps like TeslaMate, they're the sweet spot between bare metal and a full VM. I run mine with 1GB of RAM and it barely breaks a sweat.

If you've followed my guide on [running Home Assistant in a Proxmox LXC](https://devhandbook.io/blog/proxmox-home-assistant-lxc/), this will feel familiar. Same concept, different stack.

## Creating the LXC Container

**You'll need an Ubuntu 24.04 container with nesting enabled — that's the key to running Docker inside LXC.** Without nesting, Docker's container runtime can't create its own namespaces and everything falls apart silently.

From the Proxmox web UI, create a new container with these specs:

- **Template:** Ubuntu 24.04
- **Disk:** 20GB (TeslaMate's database grows slowly — a few hundred MB per year of driving)
- **RAM:** 1024MB
- **CPU:** 2 cores
- **Network:** Static IP on your LAN (I use `192.168.7.201/24`)

After creation, enable nesting before starting the container. In the Proxmox shell:

```bash
pct set 1002 -features nesting=1
```

Or edit `/etc/pve/lxc/1002.conf` directly and add:

```
features: nesting=1
```

Start the container and hop in:

```bash
pct enter 1002
```

Run a quick update:

```bash
apt update && apt upgrade -y
```

## Installing Docker

**Docker installs cleanly in an Ubuntu 24.04 LXC — just use the official convenience script.** Don't bother with `docker.io` from the Ubuntu repos; it's always outdated.

```bash
curl -fsSL https://get.docker.com | sh
```

Verify it's working:

```bash
docker run --rm hello-world
```

If that prints the hello message, you're good. If it hangs or errors out, double-check that nesting is enabled — that's the usual culprit.

Install the Compose plugin (it comes with the convenience script on modern Docker, but verify):

```bash
docker compose version
```

You should see `v2.x.x`. If not:

```bash
apt install docker-compose-plugin -y
```

## The Docker Compose Stack

**This is the entire stack — TeslaMate, PostgreSQL 17, and Grafana — in one compose file.** Create a directory and drop in the config:

```bash
mkdir -p /opt/teslamate && cd /opt/teslamate
```

Create `docker-compose.yml`:

```yaml
services:
  teslamate:
    image: teslamate/teslamate:latest
    restart: always
    environment:
      - ENCRYPTION_KEY=your-secret-encryption-key
      - DATABASE_USER=teslamate
      - DATABASE_PASS=your-db-password
      - DATABASE_NAME=teslamate
      - DATABASE_HOST=database
      - MQTT_HOST=192.168.7.46
      - MQTT_PORT=1883
    ports:
      - "4000:4000"
    depends_on:
      - database
    cap_drop:
      - all

  database:
    image: postgres:17
    restart: always
    environment:
      - POSTGRES_USER=teslamate
      - POSTGRES_PASSWORD=your-db-password
      - POSTGRES_DB=teslamate
    volumes:
      - teslamate-db:/var/lib/postgresql/data

  grafana:
    image: teslamate/grafana:latest
    restart: always
    environment:
      - DATABASE_USER=teslamate
      - DATABASE_PASS=your-db-password
      - DATABASE_NAME=teslamate
      - DATABASE_HOST=database
    ports:
      - "3000:3000"
    volumes:
      - teslamate-grafana-data:/var/lib/grafana

volumes:
  teslamate-db:
  teslamate-grafana-data:
```

Replace `your-secret-encryption-key` with a random string (this encrypts your Tesla API tokens at rest) and `your-db-password` with a strong database password. The `MQTT_HOST` points to my Home Assistant instance — more on that below.

Bring it up:

```bash
docker compose up -d
```

Give it 30 seconds, then hit `http://YOUR-LXC-IP:4000` in your browser. You'll see the TeslaMate login page where you sign in with your Tesla account. Grafana lives at port `3000` — default credentials are `admin` / `admin`.

## The Gotchas (Read This Before You Debug for Hours)

**Every one of these bit me during setup — save yourself the trouble and get them right the first time.**

### PostgreSQL 17, Not 15

TeslaMate v2.2.0 and newer requires PostgreSQL 17. If you use `postgres:15` or `postgres:16`, you'll get cryptic database migration errors that don't obviously point to a version mismatch. The [TeslaMate docs](https://docs.teslamate.org/) specify this, but it's easy to miss if you're copying an older compose file from a blog post or forum thread.

If you already started with an older Postgres version and need to upgrade, you'll have to dump the database, recreate the volume with Postgres 17, and restore. There's no in-place upgrade path with Docker volumes.

### Explicit Port Mapping

Notice the `ports` section in the compose file. Without explicitly mapping `4000:4000` and `3000:3000`, the services run fine *inside* the container but aren't accessible from your LAN. This seems obvious, but if you're used to host networking mode, it's an easy miss.

### Proxmox iptables FORWARD Chain

**This is the one that'll have you pulling your hair out.** By default, Proxmox sets the iptables FORWARD chain policy to `DROP`. That means traffic can't route between your LAN and the container's Docker network, even though the ports are mapped correctly.

You'll see the symptom as: `curl` from inside the LXC works fine, but browsing from your desktop times out.

The fix — run this on the **Proxmox host** (not inside the LXC):

```bash
iptables -I FORWARD -s 192.168.7.201 -j ACCEPT
iptables -I FORWARD -d 192.168.7.201 -j ACCEPT
```

To make it persist across reboots, add those lines to `/etc/network/interfaces` under your bridge config, or drop them in a post-up script.

### MQTT Configuration

If you set `MQTT_HOST` in the compose file, TeslaMate will try to connect to that broker on startup. If the broker isn't reachable, TeslaMate still runs — but you won't get real-time data in Home Assistant.

You do **not** need a standalone Mosquitto container. If you're already running Home Assistant with the Mosquitto add-on (like I am at `192.168.7.46:1883`), just point TeslaMate at that existing broker. One broker to rule them all.

## Connecting to Home Assistant

**Once MQTT is configured, TeslaMate automatically publishes sensor data that Home Assistant picks up instantly.** Topics follow the pattern `teslamate/cars/1/battery_level`, `teslamate/cars/1/state`, `teslamate/cars/1/speed`, and dozens more.

If you have the Mosquitto add-on running in HA, you don't need to configure anything on the HA side — MQTT auto-discovery handles it. You'll see new `sensor.teslamate_*` entities appear within minutes.

I covered the full Home Assistant LXC setup in [a separate post](https://devhandbook.io/blog/proxmox-home-assistant-lxc/) if you need to get that running first. The short version: HA in its own LXC, Mosquitto add-on enabled, and TeslaMate pointed at it via `MQTT_HOST`.

## What You'll See in Grafana

**The pre-built Grafana dashboards are genuinely impressive — this is where TeslaMate earns its reputation.** Out of the box, you get:

- **Drive Details** — every trip mapped with efficiency, speed, elevation, and outside temperature
- **Charging History** — every charge session with kWh added, cost (if configured), charge rate curve, and duration
- **Battery Health** — degradation tracking over time, showing your battery's actual capacity vs. rated
- **Efficiency** — Wh/mi broken down by temperature, speed, and climate usage. You'll finally understand why winter range drops off a cliff.
- **Vampire Drain** — how much battery your car loses while parked, broken down by sentry mode, cabin overheat protection, etc.
- **Geofence Events** — set up locations (home, work, favorite supercharger) and see arrival/departure history
- **Mileage** — daily, weekly, monthly, and yearly driving stats

The dashboards are read-only by default, which is nice — you won't accidentally break them while exploring. If you want custom panels, clone an existing dashboard and modify the copy.

For a similar "lightweight containers on Proxmox" approach with another self-hosted tool, check out my guide on [running Ollama in a Proxmox LXC](https://devhandbook.io/blog/ollama-proxmox-lxc/).

## Wrapping Up

TeslaMate is one of those projects that makes you wonder why the manufacturer doesn't just build this in. The data your car generates is fascinating — and with a Proxmox LXC, Postgres, and Grafana, you can capture all of it with minimal resources.

The whole stack runs comfortably in 1GB of RAM. It logs data 24/7 with essentially zero maintenance. And once you've seen your first year of battery degradation graphed out or watched your road trip animate across the map, you'll never want to go back to the stock Tesla app.

If you run into issues or have questions, drop a comment below. And if you're building out a Proxmox homelab, check out my other LXC guides — there's a pattern here, and it works.
