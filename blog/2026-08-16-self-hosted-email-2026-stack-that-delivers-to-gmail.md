---
layout: post.njk
title: "Self-Hosted Email in 2026: The Stack That Actually Delivers to Gmail"
date: 2026-08-16
description: "Self-hosting email is harder than it's ever been — Gmail, Outlook, and Yahoo now silently drop mail from unknown IPs. But a new generation of mail servers (Mox, WildDuck, Stalwart, Maddy) is built for exactly this problem. Here's the modern-stack decision guide, with an honest verdict on whether you should even bother."
tags: ["self-hosted", "email", "mox", "wildduck", "stalwart", "maddy", "deliverability", "homelab", "smtp", "imap", "gmail"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail"
affiliate: true
cta: true
---

There's a post that keeps resurfacing on Hacker News — 316 points, titled something like *"Self-hosting email is the hardest it's ever been."* The comments are a graveyard of people who tried, got their mail silently dropped by Gmail, and gave up. And they're not wrong: the big three providers (Gmail, Outlook, Yahoo) have spent the last five years making it brutally hard for a random IP address to land in an inbox.

But here's the thing that post doesn't tell you: **the tooling has quietly caught up.** A new generation of mail servers — Mox, WildDuck, Stalwart, and Maddy — was built *specifically* for the deliverability problem that killed the old Postfix tutorials. They handle DKIM, SPF, DMARC, and DANE out of the box. They're single-binary or single-container deploys. And a few of them are genuinely good enough that "self-hosted email" is no longer a synonym for "your mail goes to spam."

This is the guide I wish existed when I started. It's not another stale Postfix walkthrough. It's a decision guide: which modern stack to pick, how to actually get mail delivered to Gmail, and — most importantly — an honest answer to the question *"should you even bother?"*

## Why the Old Guides Are Dead

Every "self-host your email" tutorial from before ~2022 follows the same script: install Postfix, install Dovecot, fight with a dozen config files, set up SPF and DKIM by hand, and hope. That script has two fatal problems in 2026.

**First, the deliverability bar moved.** Gmail, Outlook, and Yahoo now enforce bulk-sender requirements that used to apply only to marketing platforms. If you send from a domain without proper SPF, DKIM, and DMARC alignment, you don't get a "this might be spam" warning — you get *silently dropped*. No bounce, no notification, nothing. Your mail just vanishes. That's the single most demoralizing part of self-hosting email, and it's why so many people quit.

**Second, the old stack is a maintenance tax.** Postfix + Dovecot + SpamAssassin + OpenDKIM + OpenDMARC + a webmail client is six moving parts, each with its own config format and its own way of breaking. It works, but it's a part-time job to keep running. The modern servers exist precisely because nobody wants to do that anymore.

The new generation collapses all of that into one binary or one container, with sane defaults for the deliverability stuff that used to take a weekend to configure.

## The Four Contenders

Let me introduce the field. These are the four mail servers that actually matter in 2026, and they're all worth knowing about because they optimize for different things.

### Mox — the "batteries included" newcomer

[Mox](https://github.com/mjl-/mox) is the one I'd point a beginner at. It's a single Go binary that bundles *everything*: SMTP, IMAP, a webmail client, an admin web UI, spam filtering, DKIM/SPF/DMARC, and even a built-in ACME client for TLS certificates. You run one binary and you have a complete mail server.

The philosophy is "no external dependencies, no footguns." Mox refuses to run in configurations that would hurt your deliverability — it nags you until your DNS records are right. For someone who wants a working mail server without becoming an email administrator, this is the closest thing to a turnkey answer.

**Best for:** individuals and small teams who want a complete, low-maintenance stack.

### WildDuck — the "scale like Gmail" option

[WildDuck](https://github.com/nodemailer/wildduck) is the odd one out, and it's the one that got 222 points on HN for a reason. It's built by the author of Nodemailer, and it takes a fundamentally different approach: **it doesn't store mail on disk as files.** Instead, it stores everything in MongoDB and S3-compatible object storage, and it's designed to be horizontally scaled across multiple nodes.

That sounds like overkill for a homelab, and honestly it is — WildDuck is the heaviest of the four to run. But it's the right choice if you're hosting email for a *lot* of users, or if you want the same architecture that a real email provider uses. It also has excellent API support, which makes it popular for people building email *products* rather than just hosting their own inbox.

**Best for:** multi-user deployments, email products, and people who want provider-grade architecture.

### Stalwart — the "all-in-one with a modern core"

[Stalwart Mail Server](https://github.com/stalwartlabs/mail-server) is the most actively developed of the four, and it's the one I'd bet on for the long term. It's a single Rust binary that does SMTP, IMAP, JMAP, and a full admin API, with a web-based admin panel. It has first-class support for everything modern: JMAP (the protocol Fastmail built), OAuth, and a plugin system.

Stalwart's killer feature is that it's *fast* and *safe* — Rust means no memory-safety bugs, and the single-binary design means no dependency hell. It's also the most "enterprise-ready" of the bunch, with a real admin UI and a real API. The one caveat is that it's still evolving quickly, so you'll want to pin your version.

**Best for:** people who want a modern, actively-developed server with a real admin UI and don't mind a slightly faster-moving target.

### Maddy — the "minimal and composable" choice

[Maddy](https://github.com/foxcpp/maddy) is the minimalist's pick. It's a single Go binary that does SMTP and IMAP, and it's designed around a simple, readable config file where you compose "modules" — a storage backend, a delivery target, an auth source. It's deliberately *not* an all-in-one: no webmail, no admin UI, no spam filter built in. You bring your own.

That minimalism is a feature. Maddy is the easiest of the four to *understand*, because there's so little of it. If you want to know exactly what your mail server is doing, Maddy is the one where you can actually read the whole config in five minutes. The trade-off is that you'll bolt on your own webmail (Roundcube, SnappyMail) and your own spam filtering (rspamd).

**Best for:** minimalists who want a small, composable core and don't mind assembling the rest.

## The Comparison Table

| | **Mox** | **WildDuck** | **Stalwart** | **Maddy** |
|---|---|---|---|---|
| **Language** | Go | Node.js | Rust | Go |
| **Deploy** | Single binary | Docker + MongoDB + S3 | Single binary | Single binary |
| **SMTP + IMAP** | ✅ | ✅ | ✅ | ✅ |
| **JMAP** | ❌ | ❌ | ✅ | ❌ |
| **Webmail** | ✅ built-in | ✅ built-in | ❌ (API only) | ❌ (bring your own) |
| **Admin UI** | ✅ | ✅ | ✅ | ❌ |
| **Spam filter** | ✅ built-in | ✅ (rspamd) | ✅ built-in | ❌ (bring rspamd) |
| **DKIM/SPF/DMARC** | ✅ auto | ✅ | ✅ | ✅ |
| **Horizontal scale** | ❌ | ✅ | ❌ | ❌ |
| **Best for** | Beginners, small teams | Multi-user, products | Modern all-in-one | Minimalists |

There's no single "best" — the right answer depends on what you're optimizing for. But if you forced me to pick a default for a self-hoster in 2026, I'd say **Mox for simplicity, Stalwart for longevity.**

## The Deliverability Checklist (The Part That Actually Matters)

Here's the uncomfortable truth: **choosing the right server is only 20% of the battle.** The other 80% is deliverability, and it's the part that makes or breaks the whole project. If you skip this, you'll have a beautiful mail server that sends mail into a void.

Here's the checklist, in order of importance:

### 1. A clean IP address (the non-negotiable)

This is the single biggest factor, and it's the one most guides gloss over. Gmail and friends maintain reputation scores for *IP addresses*, not just domains. If you're sending from a residential IP or a cloud IP that's been used for spam, you're starting from a hole.

The reality: **you almost certainly cannot send mail directly from your homelab IP.** Residential IPs are on blocklists by default, and most ISPs block outbound port 25 anyway. Your options are:

- **A reputable VPS** with a clean IP ([Hetzner](https://www.hetzner.com/cloud?ref=PLACEHOLDER_HETZNER_REF), [OVHcloud](https://www.ovhcloud.com/en/vps/?ref=PLACEHOLDER_OVH_REF), DigitalOcean, Vultr — but check the specific IP's reputation first, because cloud ranges are heavily abused)
- **A mail relay** (see below) that sends on your behalf from a trusted IP

This is the part where a lot of people get stuck, because it means self-hosting email isn't *fully* self-hosted — you're renting a clean IP from someone. More on that in the verdict.

### 2. SPF, DKIM, and DMARC — all three, properly aligned

These are the three DNS records that prove your mail is legitimately from you:

- **SPF** (`TXT` record) — lists which IPs are allowed to send mail for your domain
- **DKIM** (`TXT` record) — a cryptographic signature that proves the mail wasn't tampered with
- **DMARC** (`TXT` record) — tells receivers what to do when SPF/DKIM fail, and gives you reports

The key word is **alignment**. Your `From:` domain, your SPF record, and your DKIM signature all have to agree. The modern servers make this easy — Mox and Stalwart will generate the DKIM keys and tell you exactly what DNS records to add — but you still have to actually add them and verify they resolve.

### 3. A reverse DNS (PTR) record that matches

Your sending IP needs a PTR record that points back to your mail server's hostname, and that hostname needs to resolve forward to the same IP. This is a "forward-confirmed reverse DNS" check, and it's one of the first things Gmail looks at. If you're on a VPS, you set this in the provider's control panel. If you're on a relay, the relay handles it.

### 4. Warm up the IP (if it's new)

A brand-new IP with zero sending history is treated with suspicion. You need to *warm it up*: start by sending a handful of legitimate emails to addresses you control (your own Gmail, a friend's Outlook), and gradually increase volume over a few weeks. This builds reputation. Sending a blast of mail from a cold IP is a fast way to get blocklisted.

### 5. TLS and DANE (the nice-to-haves)

TLS for SMTP is table stakes now — you need a valid certificate. DANE (DNS-based Authentication of Named Entities) is a stronger form of TLS authentication that's gaining traction, and Mox and Stalwart both support it. It's not strictly required for Gmail delivery, but it's a signal of a well-run server.

### 6. A postmaster address and abuse address

`postmaster@yourdomain.com` and `abuse@yourdomain.com` need to exist and be monitored. This is a requirement for many blocklists and a signal of legitimacy. It's a two-minute setup that a surprising number of people skip.

## The Relay Question: Is It Still "Self-Hosted"?

Here's where the honest conversation happens. Given the IP reputation problem, a lot of people end up using a **SMTP relay** — a service like Amazon SES, Mailgun, or a privacy-focused relay that sends your mail from *their* trusted IPs while you still own the domain, the storage, and the receiving side.

Is that still self-hosting? I'd argue **yes, with an asterisk.** You're self-hosting the *receiving* side (your inbox, your storage, your privacy) and the *identity* (your domain, your DKIM keys). You're outsourcing only the *sending* side, which is the part that's genuinely hard to do from a residential IP.

The purist answer is "run your own mail server on a clean VPS IP and warm it up." That's absolutely doable — I've done it — but it's a real commitment. The pragmatic answer is "self-host receiving, relay sending." Both are legitimate. The only wrong answer is "self-host everything from a residential IP and wonder why Gmail drops your mail."

## A Working Mox Setup (The Fast Path)

Let me give you something concrete. If you want the fastest path to a working, deliverable mail server, here's Mox on a clean VPS:

```bash
# On a VPS with a clean IP (Hetzner/DigitalOcean/etc.)
# Install Mox (single binary)
curl -sSL https://github.com/mjl-/mox/releases/latest/download/mox-linux-amd64 -o mox
chmod +x mox
sudo mv mox /usr/local/bin/

# Initialize — this walks you through domain setup and generates DKIM keys
sudo mox quickstart you@yourdomain.com
```

Mox's `quickstart` is the best onboarding experience in self-hosted email. It asks for your domain, generates your DKIM key, and prints the exact DNS records you need to add (SPF, DKIM, DMARC, MX, and the autoconfig records). You paste those into your DNS provider, set the PTR record in your VPS panel, and you're done.

Then you point your mail client at it (Mox has a built-in webmail, or you can use any IMAP client), and you start the warm-up process: send a few test emails to your own Gmail and Outlook accounts, verify they land in the inbox (not spam), and gradually ramp up.

The whole thing — from empty VPS to sending your first deliverable email — is about an hour if your DNS propagates quickly. That's the part the old Postfix guides never delivered.

## The Honest Verdict: Should You Even Bother?

I've spent this whole post telling you how to do it, so let me give you the straight answer to the question in the title.

**Self-hosting email is worth it if — and only if — one of these is true:**

1. **You care about privacy and data ownership.** Your email is the master key to your digital life. Every password reset, every account, every receipt flows through it. Handing that to Google is a real trade-off, and self-hosting is the only way to fully own it.

2. **You want to learn how email actually works.** There's no better way to understand SPF, DKIM, DMARC, and the whole deliverability ecosystem than running your own server. It's genuinely educational, and the knowledge transfers to any job that touches email.

3. **You need a custom domain for a product or project.** If you're building something that sends email (a SaaS, a newsletter, an app), understanding this stack is table stakes, and running your own server (or a relay) gives you control you can't get from a consumer provider.

**It is *not* worth it if:**

- You just want a working inbox and don't care about the internals. Fastmail, Proton, or even Gmail will serve you better with zero maintenance.
- You're not willing to rent a clean IP (VPS or relay). Without that, you're fighting a losing battle.
- You can't commit to ongoing maintenance. Email servers need patching, monitoring, and occasional deliverability debugging. It's not a "set it and forget it" project.

The HN post that says it's "the hardest it's ever been" is half right. The *deliverability* bar is higher than ever, and the big providers are more aggressive about dropping mail. But the *tooling* has never been better. Mox, Stalwart, WildDuck, and Maddy have turned what used to be a weekend of Postfix config into a one-binary deploy with sane defaults.

The hard part isn't the software anymore. It's the IP reputation, the DNS discipline, and the ongoing commitment. If you're willing to handle those three things, self-hosting email in 2026 is not just possible — it's genuinely rewarding.

## The Bottom Line

Self-hosted email in 2026 is a solved *software* problem and an unsolved *reputation* problem. The modern servers — Mox for simplicity, Stalwart for longevity, WildDuck for scale, Maddy for minimalism — have made the software side almost trivial. What still trips people up is the deliverability side: clean IPs, SPF/DKIM/DMARC alignment, and the patience to warm up a new sender.

My advice: if you're curious, start with Mox on a cheap VPS, follow the checklist, and treat it as a learning project. If you need it to *just work* for a real inbox, self-host the receiving side and relay the sending side. Either way, you'll understand email better than 99% of the people who've ever clicked "send."

---

*Are you self-hosting email? Which stack did you pick, and did your mail actually land in Gmail? I'd love to hear what worked (and what didn't) — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [self-hosted auth and SSO](/blog/2026-08-08-self-hosted-auth-sso-showdown) and [Cloudflare Tunnels for your homelab](/blog/2026-07-26-cloudflare-tunnels-homelab-guide).*
