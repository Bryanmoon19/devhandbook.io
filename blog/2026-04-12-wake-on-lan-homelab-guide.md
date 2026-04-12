---
layout: post.njk
title: "Wake On LAN: The Homelab Power Button You Didn't Know You Needed"
date: 2026-04-12
description: "Set up Wake On LAN for your Proxmox server, NAS, or workstation. Complete guide to BIOS config, magic packets, network setup, and Home Assistant integration."
tags: ["wake-on-lan", "proxmox", "homelab", "home-assistant", "networking", "power-management", "self-hosted"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/wake-on-lan-homelab-guide"
---

Leaving your homelab server running 24/7 is expensive and loud. But shutting it down remotely means driving home, plugging in a monitor, and pressing a power button like it's 2003.

**Wake On LAN (WOL) fixes this.** Send a "magic packet" from your phone, Home Assistant, or another machine on your network, and your sleeping server boots back up. No physical access required. This guide covers the full stack: BIOS configuration, OS-level network tuning, Proxmox-specific quirks, router setup, and Home Assistant automation.

## What Wake On LAN Actually Does

WOL works at the hardware level. When a machine is powered off (but still plugged in), its network interface stays in a low-power state listening for a specific broadcast frame — the **magic packet**. This packet contains the target device's MAC address repeated 16 times. When the NIC sees its own address, it signals the motherboard to power on.

**Requirements:**
- Motherboard and NIC must support WOL (almost everything made in the last 15 years does)
- Ethernet connection (Wi-Fi WOL exists but is inconsistently supported)
- The machine must be in soft-off state (S5) or sleep (S3), not fully unplugged

## Step 1: Enable WOL in BIOS/UEFI

Every motherboard calls this something slightly different. Reboot and enter your BIOS setup (`Del`, `F2`, or `F10` depending on board).

Look for one or more of these options:
- **Wake On LAN** → Enabled
- **Power On By PCI-E Devices** → Enabled
- **Resume by LAN** → Enabled
- **ERP Ready** / **EuP 2013** → **Disabled** (this power-saving mode often cuts NIC standby power)

On Gigabyte boards, it's usually under `Settings > Platform Power > Wake On LAN Control`. On ASUS, check `Advanced > APM Configuration > Power On By PCI-E`. On Supermicro server boards, it's typically `Advanced > ACPI Settings`.

Once enabled, save and exit.

## Step 2: Enable WOL in the Operating System

Even with BIOS support, the OS network driver needs to grant the NIC permission to stay awake.

### Linux (Proxmox / Debian / Ubuntu)

Identify your ethernet interface:

```bash
ip link show
# usually enp3s0 or eth0
```

Check current WOL status:

```bash
ethtool <interface> | grep Wake-on
```

If it shows `Wake-on: d` (disabled), enable it:

```bash
ethtool -s <interface> wol g
```

To make this persistent across reboots, create a systemd service:

```bash
sudo nano /etc/systemd/system/wol.service
```

```ini
[Unit]
Description=Enable Wake On LAN
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/ethtool -s <interface> wol g

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wol.service
```

### Proxmox-Specific Note

If you're passing through a physical NIC to a VM, WOL won't work for that VM — the VM doesn't own the NIC's power-management functions. For WOL on a VM, use a virtual NIC on a bridge attached to a WOL-capable host interface, or run a WOL proxy script on the Proxmox host itself that starts the VM when it receives a magic packet.

Proxmox forum user `Dante' has a popular [WOL-for-VMs tutorial](https://forum.proxmox.com/threads/wake-on-lan-wol-for-vms-and-containers.143879/) that uses `tcpdump` + `qm start` to proxy magic packets to VMs.

### Windows

Open Device Manager, expand **Network adapters**, right-click your ethernet adapter → **Properties** → **Power Management**. Check:
- Allow the computer to turn off this device to save power → **Unchecked** (or carefully configured)
- Allow this device to wake the computer → **Checked**
- Only allow a magic packet to wake the computer → **Checked**

Then go to the **Advanced** tab and enable **Wake on Magic Packet**.

## Step 3: Test WOL From Another Machine

Install a WOL tool and send a test packet:

```bash
# macOS / Linux
wakeonlan <MAC_ADDRESS>

# Or with Python
python3 -c "import socket; \
mac=bytes.fromhex('<MAC_ADDRESS>'.replace(':','')); \
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); \
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1); \
s.sendto(b'\\xff'*6+mac*16, ('<BROADCAST_IP>', 9))"
```

Get your target's MAC address with:

```bash
ip link show <interface>
# or on another machine:
arp -a | grep <target_ip>
```

The broadcast IP is usually `192.168.1.255` — replace the last octet with `255`.

If the machine powers on, WOL is working locally.

## Step 4: Make It Work From Outside Your Network

Magic packets are Layer 2 broadcasts. They don't cross routers. To wake a machine remotely — from a café, a VPN, or Home Assistant Cloud — you need one of these strategies:

### Option A: Send From a Device Already on Your Network

The simplest approach. A Raspberry Pi, always-on NAS, or your router itself can send the magic packet. Home Assistant running locally can trigger WOL directly without any port forwarding.

### Option B: VPN Into Your Network First

Connect to your home network via WireGuard or Tailscale, then send the magic packet from inside the LAN. This is the safest remote option — no port forwarding required.

### Option C: Port Forward UDP 9 to the Broadcast Address

**Less secure, but direct.** Forward UDP port 9 on your router to `192.168.1.255` (your LAN broadcast). Then send a WOL packet to your public IP on port 9 from anywhere.

**Caveat:** Some routers refuse to forward to broadcast addresses. If yours does, forward to a specific IP instead and assign that device a static DHCP lease. Or run an always-on WOL relay (like a Pi) that receives the packet and rebroadcasts it locally.

## Step 5: Add Wake On LAN to Home Assistant

Home Assistant has a built-in WOL integration. Add it via **Settings > Devices & services > Add Integration > Wake on LAN**.

You'll need:
- The MAC address of the target machine
- (Optional) A broadcast address if HA isn't on the same subnet

This creates a **button entity** you can press to wake the device.

### Make It a Switch With State Awareness

A button only wakes. To build a proper switch that knows whether the machine is on or off, combine WOL with a [ping sensor](https://www.home-assistant.io/integrations/ping/):

```yaml
# configuration.yaml
binary_sensor:
  - platform: ping
    host: 192.168.1.50
    name: "proxmox_server_online"
    count: 2
    scan_interval: 30
```

Then create a [template switch](https://www.home-assistant.io/integrations/template/#switch):

{% raw %}
```yaml
switch:
  - platform: template
    switches:
      proxmox_server:
        value_template: "{{ states('binary_sensor.proxmox_server_online') == 'on' }}"
        turn_on:
          - service: button.press
            target:
              entity_id: button.wake_on_lan_proxmox_server
        turn_off:
          - service: shell_command.shutdown_proxmox
```
{% endraw %}

For the shutdown side, you can SSH into the server and run `systemctl poweroff`, or use Proxmox's API if you're waking a VM.

## Step 6: Automate It

### Auto-Wake When VPN Connects

If you connect to your home VPN, probably you want your server on:

```yaml
automation:
  - alias: "Wake server when VPN user connects"
    trigger:
      - platform: state
        entity_id: device_tracker.your_phone
        to: "home"
    action:
      - service: button.press
        target:
          entity_id: button.wake_on_lan_proxmox_server
```

### Auto-Shutdown When Idle

Use the [Hass Agent](https://github.com/hass-agent/HASS.Agent) or a simple Linux cron job to shut down when CPU has been idle for an hour. Or call the shutdown service from Home Assistant when no one is home and no critical services are active.

## Troubleshooting Checklist

| Symptom | Fix |
|---------|-----|
| WOL works locally but not remotely | Use a VPN or forward UDP 9 to broadcast. Check router settings. |
| NIC shows `Wake-on: d` after reboot | Create the systemd service above, or use `networkd-dispatcher`. |
| Machine wakes randomly | Disable "Wake on Pattern Match" and "Wake on Magic Packet" only in OS. |
| Proxmox VM won't wake | WOL is for physical NICs. Use a host-side WOL proxy for VMs. |
| Wi-Fi WOL doesn't work | Most Wi-Fi chipsets don't support WOL reliably. Use ethernet. |

## Bottom Line

Wake On LAN is one of those homelab essentials that's trivial once set up and frustrating until it is. The payoff: a server that sleeps when you don't need it, wakes on demand, and never requires you to physically touch it. Combine it with Home Assistant and you've got a genuinely smart power-management system.

---

*Inspired by [Jim's Garage WOL tutorial on YouTube](https://www.youtube.com/watch?v=uH-BZQriQ4U).*
