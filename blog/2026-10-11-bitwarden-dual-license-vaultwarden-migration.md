---
layout: post.njk
title: "Bitwarden's Dual-License Change: Should You Migrate to Vaultwarden Now?"
date: 2026-10-11
description: "Bitwarden announced app-store builds will be commercially licensed starting next release. Here's what the dual-license actually means for free users and self-hosters — and a concrete decision tree for migrating to Vaultwarden."
tags: ["bitwarden", "vaultwarden", "password-manager", "self-hosted", "homelab", "security", "open-source", "gpl", "privacy", "migration", "2fa"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-11-bitwarden-dual-license-vaultwarden-migration/"
affiliate: false
cta: true
---

## The News, Stated Plainly

On October 9, 2026, Bitwarden posted a short notice to its community forums: **starting with the next release, the Bitwarden apps published to app stores will be the commercially licensed builds.** The GPLv3 open-source version keeps getting published on GitHub, but the two builds are now on separate tracks.

The announcement is deliberately low-key, and the headline facts are reassuring on their face. Here's exactly what was committed:

| Question | Bitwarden's answer |
|----------|-------------------|
| Is Bitwarden going closed-source? | No — "Bitwarden is not going closed-source" |
| Can you still fork it? | Yes |
| Does self-hosting change? | No — the license change "affects those who are repackaging and reselling Bitwarden" |
| Are current features available in both? | Yes, all current features exist in both builds |
| Is the free plan staying? | Yes — "the free plan is here to stay permanently" |

So far, so good. But buried in the Q&A is the sentence that has the self-hosting community paying attention:

> **"Some future components will be published under the commercial license and will exist only in that build. Newly developed features will be evaluated on a case-by-case basis for which license applies to them."**

That's the whole story in one sentence. Nothing changes today — but the *direction of travel* has changed.

---

## What a Dual License Actually Is (and Isn't)

Before anyone panics, it's worth being precise, because "dual license" is doing a lot of rhetorical work in that thread.

**Dual licensing** means the same codebase is available under two terms: a copyleft license (GPLv3) for the community and a separate commercial license for partners. This is a standard, legitimate model — companies like MySQL and Qt have run it for decades.

**What Bitwarden is doing is slightly different and worth watching closely.** They're not licensing the *same* code two ways. They're signaling that *new components may only ship in the commercial build*. That's not classic dual licensing — it's closer to the "open core" model where the free version gradually becomes the community edition while the paying version accumulates the new work.

The difference matters:

- **Classic dual license** — same features everywhere, just different legal terms.
- **Open core** — free version is a subset; the paid version is strictly more capable over time.

Bitwarden's forum language ("evaluated on a case-by-case basis") places them somewhere in between, with the door open to drift toward open core. It's the *ambiguity itself* that people are reacting to, not any specific missing feature.

---

## Why Self-Hosters Are Nervous (and Rightly So)

The community reaction in the thread is telling. The highest-voted concern comes from a user who names the pattern directly:

> "It feels like the standard Open Source → Semi Opensource → Open Source discontinued rugpull quite a few companies have been doing lately. I especially got hit by this with MinIO."

Another commenter invokes the recent Coinkite fiasco as the cautionary tale. The anxiety isn't invented — it's pattern recognition. Over the last few years, several beloved open-source projects have walked a path that starts with "the license is changing for *commercial* reasons, but nothing changes for *you*," and ends with a materially different free product.

The self-hosting crowd isn't worried about Bitwarden *today*. They're worried about the **third move** — the one that's easy to see coming once the first two are in place. When you self-host a password manager, you're not a customer on a monthly plan; you're someone running infrastructure whose roadmap you don't control. Trust is the entire product, and trust is exactly what a license change like this quietly erodes.

---

## The Real Question: Does This Affect You?

Let's be concrete, because most readers don't need the full drama — they need to know whether *they* should act.

### If you're a free-tier Bitwarden **cloud** user

Probably not, at least not yet. Bitwarden has explicitly said the free plan is permanent and current features stay in both builds. If you're happy on the cloud and don't self-host anything, there's no fire to run toward.

### If you **self-host official Bitwarden**

Nothing breaks today. Self-hosting is explicitly unaffected by the license change — it targets repackagers and resellers, not people running their own server. But you now have a reason to watch the roadmap more closely: if future features land in the commercial build only, your self-hosted "official" stack may quietly become the lagging version.

### If you're **deciding between Bitwarden and Vaultwarden right now**

This is where the news genuinely moves the needle. The license change doesn't make Bitwarden worse — but it makes the *case for Vaultwarden stronger*, because Vaultwarden's entire value proposition is "the full Bitwarden protocol, self-hosted, free, forever, under a clear open license."

---

## Vaultwarden: The Decision Tree

I've written before about [self-hosting Vaultwarden](/blog/2026-04-19-vaultwarden-self-hosted-password-manager/) and [migrating from 1Password to Vaultwarden](/blog/2026-09-04-migrate-1password-to-vaultwarden/). Here's the updated read, in the context of this license change.

**Choose Vaultwarden if any of these are true:**

- You self-host and want **feature parity for free** — Vaultwarden includes TOTP (2FA codes), organizations, Send, and emergency access at no cost, where official Bitwarden gates several of those behind a paid license.
- You run on a **Pi, small VPS, or modest homelab box** — Vaultwarden runs comfortably in ~50–150 MB RAM on SQLite, versus Bitwarden's 2 GB+ .NET/MSSQL footprint.
- You care about **license certainty** — Vaultwarden is AGPLv3, community-driven, and not subject to a corporate "we'll evaluate each new feature's license on a case-by-case basis" roadmap.
- You want the **official apps to keep working** — Vaultwarden is API-compatible, so the official Bitwarden desktop/mobile/browser clients connect to it unchanged.

**Stay on official Bitwarden if:**

- You need **formal audits / SOC 2 / enterprise SSO** — Vaultwarden is community-reviewed but not formally audited.
- You want the vendor's own support and don't mind paying for premium features.
- You don't self-host and are content on the cloud free/premium plan.

For the overwhelming majority of homelabbers, the answer is the same one it's been for years — and the license change tips it further: **Vaultwarden is the pragmatic choice.**

---

## The Migration Path, Step by Step

If the news tips you toward moving, the mechanics are genuinely easy. Here's the whole thing.

### 1. Export from Bitwarden (cloud or self-hosted)

Web vault → **Settings → Export Vault** → choose **`.json` (encrypted)** or `.csv`. The encrypted JSON is safer if the file will touch disk at all; the CSV is plaintext and should be deleted immediately after import.

### 2. Stand up Vaultwarden

```yaml
# ~/docker/vaultwarden/docker-compose.yml
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=true    # temporarily, for first account
      - ADMIN_TOKEN=${ADMIN_TOKEN}
    volumes:
      - ./vw-data:/data
    ports:
      - "127.0.0.1:80:80"
```

```bash
cd ~/docker/vaultwarden
ADMIN_TOKEN=$(openssl rand -base64 48)
docker compose up -d
```

Then visit `http://your-server-ip`, create your account, and set `SIGNUPS_ALLOWED=false` before restarting. Put it behind your reverse proxy with HTTPS (Vaultwarden refuses to serve secrets over plaintext for good reason).

### 3. Import and re-point your clients

Web vault → **Tools → Import Data** → select "Bitwarden (json)" → upload. Then update every client (mobile, desktop, browser extension) to point at your new server URL — on mobile, tap the gear icon and set **Server URL** before logging in.

### 4. Re-enable 2FA and test

Re-generate TOTP codes and re-enable any WebAuthn/passkeys on the new instance, then test a full sync and autofill on at least two devices before you decommission anything.

### 5. Back it up (non-negotiable)

Your entire Vaultwarden state lives in `./vw-data`. Back it up daily and test a restore:

```bash
rsync -avz ~/docker/vaultwarden/vw-data/ /mnt/backups/vaultwarden/
```

A password vault is the one thing you cannot afford to lose. If you don't have off-site backups, stop and fix that before you migrate anything.

---

## The Bottom Line

Bitwarden's dual-license change is, on its own, not a rugpull and not an emergency. But it's a legitimate signal, and signals matter when the asset in question is your password manager — the highest-trust piece of software most people run.

For self-hosters, the calculus hasn't fundamentally changed: Vaultwarden was already the lean, free, feature-complete choice, and a license model that reserves the right to route new features to a commercial build only makes the "who controls my vault's roadmap?" question easier to answer.

You don't need to migrate today. But if you were ever on the fence, this is as good a nudge as any to take control of the one thing you really shouldn't leave to someone else's roadmap.

*Source: Bitwarden's official community announcement, ["Published version update in app stores"](https://community.bitwarden.com/t/published-version-update-in-app-stores/102750) (RyanL, Oct 9, 2026), and the [Hacker News discussion](https://news.ycombinator.com/item?id=50033407).*
