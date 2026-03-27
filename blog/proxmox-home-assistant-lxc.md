---
layout: post.njk
title: "Run Home Assistant in a Proxmox LXC Container"
date: 2026-03-27
description: "A step-by-step guide to running Home Assistant Container in a Proxmox LXC — lighter than a full VM, easier to manage, and just as capable."
tags: ["homelab", "proxmox", "home-assistant", "self-hosted", "lxc"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/proxmox-home-assistant-lxc"
---

If you're running a Proxmox homelab, you've probably already got a VM or two taking up RAM. Home Assistant is one of those services you want running 24/7, but dedicating a full virtual machine to it can feel wasteful — especially when a lightweight LXC container does the job just as well. This guide walks you through getting Home Assistant Container up and running inside a Proxmox LXC, from scratch.

## Why LXC instead of a VM?

The short answer: resources. A Home Assistant VM using HAOS typically needs 2–4 GB of RAM just to breathe. An LXC container running Home Assistant Container can get by on 512 MB and uses significantly less disk I/O because it shares the host kernel. You lose a bit of the "official" HAOS experience — no Supervisor, no add-on store — but most power users find the tradeoff worth it.

If you need add-ons like the Mosquitto broker or Zigbee2MQTT, you can run those separately in their own containers and integrate them via MQTT or the standard APIs.

## Step 1: Use the tteck Community Scripts

The fastest way to get started is the [tteck Proxmox helper scripts](https://tteck.github.io/Proxmox/). These community-maintained scripts handle the LXC creation, Docker installation, and Home Assistant setup for you. On your Proxmox host shell, run:

```bash
bash -c "$(wget -qLO - https://github.com/tteck/Proxmox/raw/main/ct/homeassistant-core.sh)"
```

The script will prompt you for a few choices — container ID, hostname, RAM, disk size, and whether to use the default or advanced settings. For most setups, the defaults work fine. Choose at least 1 GB RAM and 8 GB disk to give HA room to grow.

The script installs an Alpine or Debian LXC, adds Docker, pulls the Home Assistant Container image, and starts it up. The whole process takes about 3–5 minutes on a decent internet connection.

## Step 2: Set a Static IP

By default, the container grabs a DHCP address. That's fine for testing, but you want a stable IP for bookmarks and integrations. The easiest approach: set a reservation in your router's DHCP table using the container's MAC address.

Alternatively, set it statically in the container itself. If it's a Debian-based container, edit `/etc/network/interfaces`:

```ini
auto eth0
iface eth0 inet static
  address 192.168.1.50
  netmask 255.255.255.0
  gateway 192.168.1.1
```

Then restart networking: `systemctl restart networking`. Confirm with `ip addr show eth0`.

## Step 3: Access Home Assistant on Port 8123

Once the container is running, open a browser and navigate to:

```text
http://<container-ip>:8123
```

You'll be greeted with the Home Assistant onboarding screen — create your account, name your home, and set your location. From here it's standard HA setup. Give it a couple minutes on first load; it's building its initial configuration.

## Step 4: USB Passthrough for Zigbee/Z-Wave Sticks

This is where LXC gets a bit tricky compared to VMs. You need to pass the USB device through at the Proxmox host level and give the container access.

First, on your Proxmox host, find the device:

```bash
ls -l /dev/serial/by-id/
```

You'll see something like `usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_...`. Note the `/dev/ttyUSB0` or similar it points to.

Now edit the LXC config file on your Proxmox host (replace `100` with your container ID):

```bash
nano /etc/pve/lxc/100.conf
```

Add these lines:

```ini
lxc.cgroup2.devices.allow: c 188:* rwm
lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file
```

The `188` is the major device number for USB serial devices (check with `ls -l /dev/ttyUSB0`). Restart the container after editing:

```bash
pct restart 100
```

Inside HA, your Zigbee stick should now appear. If you're using Zigbee2MQTT, point it at `/dev/ttyUSB0` in its configuration.

## Step 5: Keeping Home Assistant Updated

Without the Supervisor, you update HA manually — but it's simple. SSH into the container and run:

```bash
docker pull ghcr.io/home-assistant/home-assistant:stable
docker stop homeassistant
docker rm homeassistant
docker run -d --name homeassistant --restart=unless-stopped \
  -v /root/homeassistant:/config \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Or if you used docker-compose (the tteck script sets this up), it's even easier:

```bash
cd /opt/homeassistant
docker compose pull
docker compose up -d
```

Check the current running version from HA's Settings → About page.

## Resource Comparison: LXC vs VM

Here's what you can expect in real-world usage on a Proxmox node:

| Resource | HAOS VM | HA Container (LXC) |
|---|---|---|
| RAM (idle) | ~1.2 GB | ~180 MB |
| RAM (active) | ~2.5 GB | ~400 MB |
| Disk (base install) | ~6 GB | ~1.5 GB |
| Boot time | ~45s | ~8s |
| Add-on store | ✅ | ❌ |
| Supervisor | ✅ | ❌ |

The tradeoff is clear: you give up the add-on ecosystem but gain dramatically better resource efficiency. For a homelab node that's also running other services, the LXC approach lets you do a lot more with the same hardware.

## Final Thoughts

Running Home Assistant in a Proxmox LXC container isn't officially supported by the HA team, but it's a battle-tested approach in the homelab community. The tteck scripts handle the heavy lifting, and once you're up and running, the day-to-day experience is identical to any other HA install. Just set your static IP, bookmark port 8123, and you're home.
