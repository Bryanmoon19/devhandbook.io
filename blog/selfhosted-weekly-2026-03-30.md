---
layout: post.njk
title: "Self-Hosted This Week: Update Immediately — March 24–30, 2026"
date: 2026-03-30
description: "Home Assistant gets audited backup encryption, Langflow is being actively exploited, Booklore forks multiply, Valkey dethroned Redis at AWS, and OpenAI bought your Python toolchain."
tags: ["selfhosted", "weekly", "homelab", "roundup"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-03-30"
---

This was a busy week in the self-hosted world — and not entirely in a good way. Two critical vulnerabilities, a major project implosion, and a corporate acquisition that has half the Python ecosystem watching nervously. But there's good news too: Home Assistant shipped a meaningful security upgrade, Velero found a proper home, and Valkey is quietly winning the Redis war.

Let's dig in.

---

## 1. Home Assistant 2026.4 Gets Independently Audited Backup Encryption

**What it is:** Starting April 1, Home Assistant backups will use SecureTar v3 — a purpose-built, independently audited encryption library commissioned by the Open Home Foundation. Trail of Bits reviewed the implementation, found three issues, confirmed they were fixed, and blessed the final result as best-in-class. The upgrade rolls out automatically; old backups remain readable.

**Why it matters:** Your Home Assistant backup contains your entire smart home configuration, secrets, automations, and potentially credentials. Most people back this up to cloud storage they don't control. The previous format wasn't broken, but the key derivation was aging — this upgrade brings it in line with modern cryptographic standards (think Argon2 instead of something embarrassingly dated). The fact that the Open Home Foundation *paid for an independent audit* rather than shipping and hoping is a meaningful signal about where the project's priorities lie.

**→ [Read the full announcement](https://www.home-assistant.io/blog/2026/03/26/modernizing-encryption-of-home-assistant-backups/)**

---

## 2. Langflow RCE Actively Exploited — Upgrade Now (CVE-2026-33017, CVSS 9.3)

**What it is:** Langflow, the popular open-source visual AI workflow builder, has a critical unauthenticated remote code execution vulnerability. An attacker can execute arbitrary Python on your server with a single HTTP request — no credentials needed. CISA added it to the Known Exploited Vulnerabilities catalog on March 25. Sysdig observed active exploitation within 20 hours of disclosure. The "fixed" version may still be exploitable through certain endpoints according to JFrog researchers.

**Why it matters:** Langflow is exactly the kind of tool people expose to the internet because it's "just for AI stuff." It's not just for AI stuff — it's an arbitrary code execution surface if unpatched. If you're running it: **upgrade to v1.9.0+, rotate all secrets, and put it behind a reverse proxy with authentication.** Never expose AI workflow tools directly to the internet. This isn't a drill.

**→ [CVE details and Sysdig's writeup](https://sysdig.com/)**

---

## 3. Booklore Is Gone — Fork Wars Begin

**What it is:** Booklore, a fast-growing self-hosted digital library platform that had built significant community momentum, was pulled from GitHub after developer misconduct toward contributors came to light. Days later, the developer shipped a "critical" security patch with zero transparency about what was actually fixed. The community is now rallying around forks: [Grimmory](https://github.com/grimmory-tools/grimmory) and [BookLite](https://github.com/marijnbent/booklite) are the two most active contenders emerging as potential successors.

**Why it matters:** This is the self-hosted community's recurring nightmare: a fast-growing, single-maintainer project where one person's behavior can wipe out months of user investment overnight. It's also a reminder that "just install the patch" is bad security hygiene when there's no CVE disclosure or changelog transparency. Projects live or die on governance and contributor trust. Prefer projects with multiple maintainers, clear contribution guidelines, and a track record of transparent security disclosures. The forks are promising — watch Grimmory in particular, which has picked up several of the original contributors.

**→ [r/selfhosted thread](https://old.reddit.com/r/selfhosted/comments/1rs275q/psa_think_hard_before_you_deploy_booklore/)**

---

## 4. Valkey Is Now the Default at AWS — Redis Is Losing the War

**What it is:** AWS ElastiCache flipped its default engine from Redis to Valkey this week. Google Cloud Memorystore added full Valkey support. The Redis fork — created after Redis relicensed away from open-source in 2024 — now sits at ~90% command compatibility with Redis, with divergence happening at the edges.

**Why it matters:** If you're still running `redis:latest` in Docker Compose, you should probably swap it for `valkey/valkey:latest`. It's a near-drop-in replacement for most self-hosted use cases (Authentik, Paperless-ngx, Immich, etc.), it's genuinely open-source, and the cloud provider ecosystem is now betting on it over Redis. The momentum here is real. Redis made a business decision; the open-source world made a different one. Valkey won.

**→ [Valkey on GitHub](https://github.com/valkey-io/valkey)**

---

## 5. FCC Bans Foreign-Made Consumer Routers — Your Firmware Has Never Mattered More

**What it is:** The FCC announced a ban on imports of new consumer-grade Wi-Fi routers manufactured in China, citing national security concerns. The ban targets new imports, not hardware already in the field — so your existing router is fine, but your next upgrade just got more interesting.

**Why it matters:** The immediate practical impact is limited, but the policy signal is loud: the security of your network perimeter is now a political issue, not just a technical one. For self-hosters, this is an excellent forcing function to consider running your own routing on open firmware. [OPNsense](https://opnsense.org/) on a mini PC (Topton, Beelink, or a used Protectli box) gives you a router you control entirely — no phoning home, no surprise firmware updates, no supply chain ambiguity. It's not beginner-friendly, but if you're reading a self-hosted roundup, you're probably ready.

**→ [Wired's explainer on the ban](https://www.wired.com/story/us-government-foreign-made-router-ban-explained/)**

---

## 6. OpenAI Bought Your Python Toolchain

**What it is:** OpenAI acquired Astral — the company behind `uv` (the fast Python package manager), `ruff` (the linter that replaced flake8/black for most projects), and `ty` (the new type checker). Astral's team joins the Codex AI coding division. OpenAI says everything stays open-source.

**Why it matters:** `uv` and `ruff` are embedded in an enormous number of self-hosted Python projects — Home Assistant plugins, Paperless-ngx development, anything built in the modern Python ecosystem. The tools aren't going anywhere, and relicensing would be PR suicide. But governance matters. When the company that controls your AI assistant also controls your linter and package manager, the incentive structures get complicated. The community is watching. This is one to keep an eye on.

**→ [OpenAI's announcement](https://openai.com/)**

---

## Closing Thought

Two critical CVEs, one project imploding, and a corporate acquisition with uncertain long-term implications — all in the same week. It's a useful reminder that "self-hosted" doesn't mean "immune to the chaos." It means *you're in control of your response*.

Update Langflow. Think about backup encryption. Watch the Booklore forks. And maybe finally replace that consumer router.

---

*Self-Hosted This Week is a weekly roundup published every Monday. Got a tip or project worth featuring? The best finds come from the community.*
