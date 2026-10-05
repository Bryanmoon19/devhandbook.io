---
layout: post.njk
title: "Self-Hosted This Week: Local Control Goes All the Way Down — September 28–October 5, 2026"
date: 2026-10-05
description: "A 125B frontier model runs on an RTX 4090, Apprise hits 2.0 with 160 notification services, a robot vacuum cuts its cloud, Dockhand quietly moves its license goalposts, and Reddit kills RSS. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "llm", "apprise", "roborock", "licensing", "rss", "federation"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-10-05"
---

There's a theme running through this week's stories, and it isn't subtle: **"local control" keeps reaching further down the stack.** We're no longer just self-hosting apps — we're running frontier AI on a single gaming GPU, yanking a robot vacuum off its manufacturer's cloud, and pushing back the moment a project tries to move the licensing goalposts. The self-hosted community isn't just growing; it's getting more militant about who actually owns the things in its house.

Here's what caught my eye from September 28–October 5, 2026.

---

## 1. Strata: A 125B Frontier Model on a Single RTX 4090

**What it is:** [Strata](https://github.com/Niko1221/Strata) is a project that runs Qwen 3.8 Flash Next (a 125-billion-parameter model) on consumer hardware — a single RTX 4090 — at a claimed 100 tokens per second. It hit the top of Hacker News this week with over 700 points.

**Why it matters:** A year ago, running a 100B+ parameter model meant renting cloud GPUs or dropping five figures on a workstation. Now the frontier is showing up on a card you can buy at retail. The technique leans on aggressive quantization, offloading, and speculative decoding — the same "make big models fit in small boxes" engineering that's been quietly shrinking the entire self-hosted AI barrier to entry. When a 125B model runs on consumer silicon, the argument for sending your data to a hosted API gets noticeably weaker.

**The takeaway:** If you've been treating "frontier AI" and "self-hosted AI" as two different things, Strata is the week's clearest evidence they're converging. Your homelab GPU might be more capable than you think.

[**Strata on GitHub →**](https://github.com/Niko1221/Strata)

---

## 2. Apprise 2.0: The Notification Switchboard Grows Up

**What it is:** [Apprise](https://github.com/caronc/apprise) is the self-hosted "notification hub" — your scripts, cron jobs, containers, and Home Assistant send one notification to Apprise, and it fans it out to Discord, Telegram, Matrix, Gotify, email, SMS, and about 155 other services.

**Why it matters:** Apprise 2.0 landed this week after years of slow accretion, and it's a genuine milestone: 160 supported notification services, optional authentication on the API, template variables so secrets stay out of your config, priority-based escalation, smarter retries, and live delivery logs. The developer's framing is the real story though — instead of scattering your Discord webhooks, SMTP passwords, and Telegram tokens across a dozen containers, they all live in *one* place. That's the self-hosted ethos distilled: centralize the control, keep the data yours. 17K stars and ~9M PyPI downloads a month suggest a lot of homelabs already agree.

**The takeaway:** If your notification setup is a tangle of hardcoded webhooks, Apprise 2.0 is a clean, self-hosted excuse to consolidate it. Note the breaking changes in the Python library if you embed it directly.

[**Apprise v2.0 →**](https://github.com/caronc/apprise/releases/tag/v2.0.0)

---

## 3. Self-Host Your Roborock Cloud Without Rooting the Vacuum

**What it is:** [local_roborock_server](https://github.com/Python-roborock/local_roborock_server) recreates Roborock's backend stack (MQTT + REST) so a robot vacuum can run entirely against your own server — no root, no hardware modification, just a few onboarding tricks to point the vacuum at your URL.

**Why it matters:** This is the exact kind of project the self-hosted movement exists for. A robot vacuum is a camera, a microphone, and a detailed floor plan of your house, all phoning home to a company's cloud by default. The maintainer — a co-maintainer of python-roborock — spent years on the goal of cutting that tether, and it runs in Docker or as a Home Assistant addon. It's a preview of where the broader "de-cloud your IoT" push is heading: not just smart plugs and lights, but the genuinely sensitive devices in your home.

**The takeaway:** If a vacuum with a camera and a map of your house bothers you, this is the first real path to running it fully local. The technical writeup is a great read even if you don't own a Roborock.

[**local_roborock_server →**](https://github.com/Python-roborock/local_roborock_server)

---

## 4. Dockhand Quietly Moves Its License Goalposts

**What it is:** [Dockhand](https://github.com/Finsys/dockhand) — a Docker management tool — changed its Business Source License terms this week, and r/selfhosted noticed.

**Why it matters:** The original deal was "BSL now, converts to Apache 2.0 on January 1, 2029." This week's commit rewrote that to "converts to Apache 2.0 *four years after each version is released*" — meaning the clock never actually runs out — while also tightening "internal business use" into "any production use by a company requires a commercial license." When a maintainer says "no worries, it converts in 2029" and then deletes the comment, the self-hosted community reads it as a trust signal, and not a good one. It's a reminder that "open source eventually" licenses are only as good as the maintainer's word.

**The takeaway:** This is why license terms matter more than feature lists. If you're evaluating Dockhand (or any BSL tool) for anything beyond personal use, read the license — and don't bank on the conversion date.

[**The discussion →**](https://www.reddit.com/r/selfhosted/comments/1wwl40o/dockhand_changed_its_license_model_instead_of/)

---

## 5. Reddit Is Killing Its RSS Feeds — Again

**What it is:** Following the API shutdown, Reddit announced this week that its RSS feeds will also be shut off on November 13th.

**Why it matters:** For a self-hoster, RSS is the quiet backbone of everything — your feed reader, your automations, your monitoring. r/selfhosted's top thread this week was the community asking, semi-seriously, whether it's finally time to leave the platform behind entirely. It's the same pattern as the API-pocalypse: a platform that grew on open access gradually ratcheting it shut, and a community of people who run their own infrastructure asking why they're still lending their content to a walled garden. The proposed fix — a "Discord Relay" — is its own kind of irony.

**The takeaway:** If any of your workflows depend on Reddit RSS, you have until mid-November to find an alternative. The broader lesson: every third-party dependency is a future migration.

---

## 6. Self-Hosted HTTP Tunnels with Nothing but SSH + Nginx

**What it is:** A [writeup by Vincent Bernat](https://vincent.bernat.ch/en/blog/2026-http-over-ssh) on building HTTP tunnels using only OpenSSH's reverse forwarding plus Nginx — no cloudflared, no frp, no rathole — trended on Hacker News this week.

**Why it matters:** It landed the same week we published our own [zero-dependency tunnel guide](/blog/2026-10-05-expose-homelab-without-cloudflare-ssh-nginx) on this exact theme, which is a nice signal that the "de-Cloudflare" impulse has gone mainstream. The appeal is the same in both cases: two tools you already run, no third party sitting in your request path, no new daemon to trust and patch. The whole alternative-tunnel space has been exploding, but the simplest answer is often the one hiding in software you installed years ago.

**The takeaway:** Before you reach for a dedicated tunnel tool, check whether plain SSH reverse forwarding already does what you need. It usually does.

[**Read the writeup →**](https://vincent.bernat.ch/en/blog/2026-http-over-ssh)

---

## Honorable Mentions

- **Your Proxmox boot drive is dying faster than you think** — an [XDA piece](https://www.xda-developers.com/my-proxmox-host-was-writing-hundreds-of-gigabytes-a-day-to-an-ssd-that-barely-stores-anything/) on a Proxmox host writing hundreds of gigabytes a day to a tiny SSD, sparking a useful round of "what's writing to my boot drive?" introspection.
- **Jellyfin OIDC on hold** — the long-awaited SSO pull request is [complete but shelved](https://www.reddit.com/r/selfhosted/comments/1wstzj4/jellyfin_oidc_on_hold_despite_complete_pr_being/), with the team preferring to redesign auth first. Realistic project stewardship, but a bummer if you were waiting on it.
- **Self-Hosting on the Dark Web** — a [thoughtful HN-front-page piece](https://david.alvarezrosa.com/posts/self-hosting-on-the-dark-web/) on running services over Tor, worth a read if you're exploring the privacy end of self-hosting.
- **mariushosting's "running in circles" post** — a veteran reviewer arguing the scene is saturated with photo managers and dashboards and calling for "magic apps" in astronomy, biology, and other specialized fields. Fair critique, and a fun thought experiment.

---

## Closing Thought

The through-line this week is that **"self-hosting" stopped being a category of software and became a stance.** A 125B model on a gaming card. A vacuum that doesn't phone home. A license change that the community treats as a breach of trust. A platform quietly killing RSS and a community quietly asking why it's still there. None of these are about installing a Docker container anymore — they're about who controls your hardware, your data, and your attention.

That's the part that keeps surprising people. The tools keep getting better, sure. But what's really growing is the *conviction*. The more capable a homelab gets, the less anyone wants to hand the keys back to a company that can move the goalposts, kill the feed, or change the terms overnight.

What's landing in your homelab this week? Drop a comment if something caught your eye.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
