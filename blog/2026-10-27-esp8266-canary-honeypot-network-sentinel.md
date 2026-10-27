---
layout: post.njk
title: "Catch Intruders on Your Home Network: A $3 ESP8266 Canary Honeypot"
date: 2026-10-27
description: "A $3 ESP8266 becomes a silent, always-on sentinel for your LAN — three armed honeypot decoys (a fake terminal, a fake router, a fake camera) that trip the instant an intruder probes them, plus network-health and power-outage tracking, all wired into Home Assistant and Discord. This is the proactive half of your intrusion-detection story, and it costs less than a coffee."
tags: ["esp8266", "honeypot", "canary", "security", "intrusion-detection", "home-assistant", "mqtt", "homelab", "self-hosted", "ids", "network-monitoring", "iot", "sentinel"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-27-esp8266-canary-honeypot-network-sentinel/"
affiliate: true
cta: true
---

So far, everything I've written about securing the homelab has been *reactive* — tools that notice a problem and respond to it after it starts.

[CrowdSec vs Fail2ban](/blog/2026-09-05-crowdsec-vs-fail2ban-homelab/) is about blocking an IP *after* it misbehaves. [Sonarr security hardening](/blog/2026-04-12-sonarr-security-hardening/) is about shrinking the surface *before* someone pokes it. The [MCP attack-surface piece](/blog/2026-08-16-mcp-servers-attack-surface/) is about understanding what a new tool exposes. All of it is the same posture: watch, detect, respond.

This post is the other half. It's about **proactive detection** — planting something silent in your network that no legitimate device will ever touch, and getting an alert the *second* someone who shouldn't be there does.

Enter [ESP-Watchtower](https://github.com/prasadabhishek/esp-watchtower), a recent Show HN project that turns a **$3 ESP8266** into an always-on home network sentinel and canary honeypot. It's the cheapest, quietest tripwire you can wire into your LAN, and it pairs beautifully with the reactive stack you already run. Let me show you exactly how it works, what it costs, and how to get it shouting into Home Assistant the moment a burglar — digital or physical — brushes against your network.

## The Canary Concept (And Why It's Different)

In old coal mines, miners carried a canary in a cage. Canaries are far more sensitive to carbon monoxide than humans, so if the bird stopped singing, you knew the air was going bad *before* it killed you. The canary didn't fight the gas — it just signaled early.

A **canary honeypot** is the same idea applied to your network. You deploy a decoy — a fake service that looks real but has no legitimate purpose — and you make sure *nothing legitimate ever talks to it*. The moment anything does, you know an intruder is present. It doesn't block, it doesn't ban, it doesn't fight back. It just sings. And its silence is the proof that nothing's wrong.

This is fundamentally different from the reactive tools:

- **Fail2ban/CrowdSec** wait for a *failed login* and then block. They're reactive by design — something bad has to happen first.
- **A honeypot** sits there waiting for the *first touch* of an intruder. There's no "three strikes." One connection to a decoy, and you know someone's casing the place.

That's why a honeypot is the missing layer in a self-hosted security stack. CrowdSec catches the bot that's already hammering your SSH. The honeypot catches the person who's *just arrived* and is quietly scanning for open doors — before they find anything real.

ESP-Watchtower ships three armed decoys out of the box, each one designed to look like something an attacker would probe, and each one logging who touched it.

## What ESP-Watchtower Actually Is

It's a single Arduino/PlatformIO firmware project for the ESP8266 — the NodeMCU or the Wemos D1 Mini, the same cheap boards everyone has rattling around a drawer. Flash it, plug it into any USB charger, and it becomes a dedicated, always-on sentinel drawing **under half a watt**.

Its job breaks into three parts:

**1. Three armed honeypots (the canaries).** Each one emulates a real service and logs every interaction:

| Decoy | Port | What it pretends to be | What it catches |
|---|---|---|---|
| Door 1 | 23 | A Linux terminal (fake Ubuntu shell) | Intruder IP, usernames, brute-forced passwords |
| Door 2 | 8080 | A router admin login page | Credential-stuffing against your "gateway" |
| Door 3 | 554 | An IP security camera RTSP stream | Network scanners sniffing for video feeds |

The moment anything connects to any of these, ESP-Watchtower logs the source IP, what they tried, and fires an instant alert to Discord (and, as I'll show, into Home Assistant).

**2. Network and power health tracking.** It continuously pings your router and `1.1.1.1`, tracking latency, packet loss, and exactly how long any outage lasted. It also detects power outages — it knows the moment the house loses electricity and, on reboot, reports how long it was down. That's quietly useful: it means your sentinel doubles as an uptime monitor and a "did the breaker trip while I was out" logger.

**3. Remote operations.** It can send Wake-on-LAN magic packets (so you can wake a sleeping server from the dashboard), generate a daily 24-hour summary report, and log everything to on-board flash (`/audit.log`) so evidence survives a power cut.

All of it is served through a modern dark-mode web dashboard, and it's Tailscale-ready so you can reach it from anywhere without opening a single router port.

The whole thing is MIT-licensed, and the author even ships a host-native unit test suite (`pio test -e native`) so you can validate the logic before flashing. For a $3 board, that's a remarkably complete package.

## The $3 Parts List

This is genuinely the cheapest security device you'll ever deploy. Here's the entire bill of materials:

| Item | Spec | Cost |
|---|---|---|
| **ESP8266 dev board** | NodeMCU v2/v3 *or* Wemos D1 Mini, 4MB flash, CP2102 or CH340 USB | **~$2.50–$4.00** |
| **Micro-USB cable + charger** | Any 5V phone charger / spare USB port | $0 (you have one) |

That's it. No sensors, no shields, no monthly subscription, no cloud account. The board itself is the sensor. If you want to get fancy you can put it in a little 3D-printed case, but the bare board tucked behind a shelf works fine — it's silent, draws half a watt, and runs 24/7 off a charger you already own.

I'd recommend the **Wemos D1 Mini** if you're buying new: it's physically smaller, the USB port is sturdier, and it's the same $2.50-ish price. But a NodeMCU is equally fine and probably what's already in your parts bin.

## Flashing the Firmware

ESP-Watchtower uses PlatformIO, which is the cleanest way to flash an ESP8266 in 2026. If you don't have it, `pip install platformio` gets you there in one shot.

```bash
git clone https://github.com/prasadabhishek/esp-watchtower.git
cd esp-watchtower

# Compile and flash straight to the board
pio run -t upload
```

Connect the board over USB first, and PlatformIO will detect the port automatically. (On a Mac, the CH340 boards sometimes want the CH34x driver installed; the CP2102 boards are plug-and-play. If the upload fails with a port error, that's usually the culprit.)

Once flashed, the board boots into a **setup mode** and spins up its own temporary Wi-Fi network:

- **SSID:** `ESP-Watchtower`
- **Password:** `sentinel123`

Connect your phone or laptop to that network, open `http://192.168.4.1`, and give it your real home Wi-Fi credentials. It'll join your network and grab an IP (something like `192.168.1.150`), and from then on the dashboard lives at that address.

That's the whole install. Ten minutes, one flash, done.

## Wiring Alerts Into Discord (Native)

ESP-Watchtower's built-in alert channel is Discord webhooks, and it's worth setting up even if you also use Home Assistant, because it's dead simple and instant.

In Discord, open a channel's settings → **Integrations** → **Webhooks** → **New Webhook**, copy the URL, and paste it into the "Direct Phone Alerts" box on the ESP-Watchtower dashboard. You'll get a verification ping immediately. From then on, every honeypot trip, every outage, and the daily morning report land right in that channel.

If you're not a Discord person, don't worry — the real fun is getting this into Home Assistant, which is where your homelab actually lives.

## Getting It Into Home Assistant + MQTT

Here's the honest note up front: ESP-Watchtower's native alert path is the Discord webhook. It doesn't speak MQTT directly out of the box. But it exposes a clean **REST API** on the device, and that's your bridge into Home Assistant. Two solid approaches:

### Option A — REST sensors + automation (no extra software)

ESP-Watchtower exposes `/api/status` (live telemetry: uptime, ping, RSSI, honeypot hit count, memory) and `/api/logs` (the rolling audit log as JSON). You can poll these straight from Home Assistant using a `rest` sensor:

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "Watchtower Status"
    resource: "http://192.168.1.150/api/status"
    json_attributes:
      - uptime
      - rssi
      - trapHits
      - ping
    value_template: "{{ value_json.trapHits }}"
    scan_interval: 60
```

Then an automation watches the honeypot-hit count for any change, and fires a notification the moment it climbs:

```yaml
automation:
  - alias: "Canary tripped — network intruder"
    trigger:
      - platform: state
        entity_id: sensor.watchtower_status
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚨 Canary tripped"
          message: "Something touched a honeypot decoy. Check the Watchtower audit log."
```

Polling every 60 seconds means a worst-case minute of latency before you're notified. For a silent tripwire, that's usually fine — but if you want *instant*, Option B is the better path.

### Option B — pipe it through Node-RED / an MQTT bridge

If you run Node-RED (and if you're on Home Assistant, it's worth adding), you can hit the REST endpoints on a tight loop and publish straight to MQTT, which gives you near-instant, event-driven alerts and full MQTT-native history:

- An **inject node** polls `/api/logs` every few seconds.
- A **function node** diffs the hit count against the previous value.
- On any increase, it publishes a JSON payload to an MQTT topic like `home/canary/tripped`.

Then any MQTT subscriber — Home Assistant, your phone, a wall tablet — reacts instantly. This is also the cleanest way to fold the honeypot into a broader MQTT event bus alongside the rest of your sensors.

The same REST API also gives you `/api/send-report` (trigger the daily report on demand), `/api/test-alert` (simulate a trip to test your pipeline end-to-end), and `/api/wol` (send a Wake-on-LAN packet with a MAC address). So even without native MQTT, the surface is rich enough to wire it into whatever automation stack you run.

## Test It Before You Trust It

The cardinal rule of any tripwire is **test it, don't assume it works.** ESP-Watchtower makes this easy two ways:

1. **`/api/test-alert`** — simulates a honeypot trip, flashes the LED, and fires the alert. Run it once from curl (`curl -X POST http://192.168.1.150/api/test-alert`) and confirm the notification lands in Discord *and* Home Assistant before you walk away.

2. **Manual probe** — from another machine on your LAN, `telnet 192.168.1.150 23` and type a fake username/password. You should see the intruder (you) logged with your IP and the credentials you fed it, and an alert should fire. This is the end-to-end proof that the decoy, the logging, *and* your notification path all work.

Do both. A silent honeypot that doesn't actually alert you is worse than no honeypot at all, because it gives you false confidence.

## Where This Fits in Your Stack

Let me place it in context, because the framing matters. Your self-hosted security posture now has three layers:

1. **Shrink the surface** — the Sonarr hardening, the MCP attack-surface review, closing ports you don't need. Make less to attack.
2. **React to what gets through** — CrowdSec/Fail2ban watching for failed logins and blocking at the edge.
3. **Detect the intruder before they find anything** — the canary honeypot, sitting silently, tripping the moment anyone starts scanning.

The honeypot doesn't replace layers 1 and 2 — it fills the gap they leave. CrowdSec can't alert you to someone who hasn't made a single failed login yet, who's just quietly port-scanning your subnet looking for a misconfigured camera or an old router. The honeypot catches exactly that person.

And because it's a separate physical device on its own tiny budget of power, it keeps watching even when your main server is down, your router is rebooted, or the power's flickered and come back. It's the sentinel that never sleeps and never reboots into a broken state.

## The Bottom Line

For about **$3** and **ten minutes**, you get a dedicated, always-on canary honeypot with three armed decoys, network-health tracking, power-outage logging, and instant alerts into Discord and Home Assistant. It's the cheapest layer of your security stack by an order of magnitude, and it's the one that catches the intruder *before* they do damage rather than after.

The reactive tools I've written about are the alarm system that goes off when a door gets kicked. The canary is the tripwire on the property line — it's quiet, it's cheap, and it tells you someone's coming *before* they reach the door.

Flash one this weekend. Then run `/api/test-alert` and watch the notification land on your phone. That's the moment it stops being a $3 board and becomes the first thing in your network that will warn you when someone who doesn't belong there comes knocking.
