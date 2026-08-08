---
layout: post.njk
title: "Self-Hosted This Week: Docker Alternatives and Homelab Security — August 2-8, 2026"
date: 2026-08-08
tags: [selfhosted, weekly, homelab, roundup]
---

# Self-Hosted This Week: Docker Alternatives and Homelab Security

Welcome back to another week in self-hosting! This week brought some exciting developments in containerization, security tools, and quality-of-life improvements for homelab enthusiasts. Let's dive into what's been making waves in the community.

## 1. Podman 5.3 Drops with Major Docker Compose Improvements

**What it is:** Podman, the daemonless container engine from Red Hat, released version 5.3 this week with significant improvements to Docker Compose compatibility.

**Why it matters:** For self-hosters looking to move away from Docker's daemon architecture, Podman continues to close the gap. The new version brings better support for Compose V2 specifications, improved volume handling, and native systemd integration that makes running containers as system services even smoother. If you've been waiting to make the switch, this might be your moment.

🔗 [Podman 5.3 Release Notes](https://podman.io/releases/)

## 2. Immich Adds Multi-User Shared Albums

**What it is:** Immich, the popular self-hosted photo backup solution, shipped multi-user shared albums in their latest release.

**Why it matters:** This has been one of the most requested features for Immich. Families and couples can now easily share photo collections without workarounds. Combined with continued mobile app improvements and faster backup speeds, Immich solidifies its position as the leading Google Photos alternative for self-hosters.

🔗 [Immich Release v1.118.0](https://github.com/immich-app/immich/releases)

## 3. New Homelab Security Checklist Goes Viral

**What it is:** A comprehensive homelab security checklist published on GitHub has gained significant traction this week, covering everything from network segmentation to secrets management.

**Why it matters:** As homelabs grow more complex (and expose more services to the internet), security often takes a backseat to functionality. This checklist provides practical, actionable steps for common setups: reverse proxy hardening, fail2ban configurations, proper VLAN isolation, and when to use Tailscale vs. traditional VPNs. Worth bookmarking even if you're security-conscious already.

🔗 [Homelab Security Checklist](https://github.com/homelab-security/checklist)

## 4. Umbrel OS 1.3 Beta Introduces Custom App Sources

**What it is:** Umbrel OS, the user-friendly homelab OS, entered beta for version 1.3 with support for custom app stores.

**Why it matters:** Previously limited to Umbrel's curated app store, users can now add third-party app sources. This opens the door for community-maintained apps, enterprise tools, and niche services that didn't make it into the main store. It's a balance between Umbrel's walled-garden simplicity and the flexibility power users crave.

🔗 [Umbrel OS 1.3 Beta Announcement](https://umbrel.com/blog/umbrel-os-1-3-beta)

## 5. Frigate 0.15 RC Adds AI Person Detection Improvements

**What it is:** Frigate, the NVR solution for self-hosted security cameras, released a release candidate for version 0.15 with enhanced AI detection models.

**Why it matters:** The new models reduce false positives significantly (no more alerts because a tree looked suspicious) while improving detection accuracy for people and vehicles. For those running Frigate with Coral TPUs, the performance gains are noticeable. The RC is reported stable by early testers, making it worth considering for new installations.

🔗 [Frigate 0.15 RC Release](https://github.com/blakeblackshear/frigate/releases)

## 6. TrueNAS SCALE 25.04 "Dragonfish" EOL Notice

**What it is:** iXsystems announced that TrueNAS SCALE 25.04 will reach end-of-life next month, with recommendations to upgrade to 25.10.

**Why it matters:** If you're running SCALE on older hardware, now's the time to test your upgrade path. The jump to 25.10 brings Kubernetes improvements, better Docker integration (via Docker Compose app), and ZFS 2.3 enhancements. Several users reported smooth upgrades, but as always: backup your config and test first.

🔗 [TrueNAS SCALE Release Notes](https://www.truenas.com/docs/scale/25.10/)

## 7. Community Spotlight: Home Assistant + TeslaMate Integration Guide

**What it is:** A detailed guide for integrating TeslaMate with Home Assistant gained attention this week, covering MQTT setup, dashboard creation, and automation ideas.

**Why it matters:** For the EV-curious homelabbers, this integration unlocks powerful automations: pre-conditioning when you're almost home, charging alerts when electricity rates drop, battery level monitoring alongside your other dashboards. The guide includes ready-to-import Lovelace cards and automation templates.

🔗 [TeslaMate + HA Integration Guide](https://community.home-assistant.io/t/teslamate-complete-integration-guide/)

---

## Closing Thoughts

This week showed the maturity of the self-hosted ecosystem. We're past the point of just replicating cloud services—tools like Podman and Immich are innovating in ways that make self-hosting genuinely better than managed alternatives. The security checklist going viral also signals a community growing up: we're thinking harder about doing this _right_, not just doing it.

What are you running this week? Any upgrades planned? Drop your homelab updates in the comments.

---

_Found this useful? Share it with someone who's still paying for cloud storage. See you next week!_
