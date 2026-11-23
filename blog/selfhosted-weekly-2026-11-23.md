---
layout: post.njk
title: "Self-Hosted This Week: Small Models, Sneaky Privacy Policies, and a Garage Door That Won't Stay Local — November 17–23, 2026"
date: 2026-11-23
description: "Inkling 2 Mini puts real reasoning on a laptop, Backblaze quietly rewrites its privacy terms, someone roots a MyQ garage opener to stop it phoning home, and the homelab keeps feeding the NTP Pool. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "local-ai", "backup", "right-to-repair", "privacy", "self-hosting", "router"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-11-23"
---

Last week the self-hosting crowd was busy *rebuilding the cloud* — reimplementing serverless runtimes in Rust, turning Durable Objects into a self-hosted daemon, collapsing map tiles into a single file. This week felt like the quieter, more uncomfortable counterpart: **the week the terms kept changing under your feet.**

The story wasn't a single tool. It was a *mood* — the low-level unease of realizing that even the parts of your stack you'd long since written off as "settled" can shift overnight. A small model arrived that finally makes real reasoning fit on a laptop, and the local-AI crowd had to recalibrate what "good enough" means. A backup vendor everyone trusted quietly rewrote its privacy policy. A garage door that should be a dumb appliance turned out to be phoning home every thirty minutes. A router brand the homelab loves had to issue a security notice. None of it was catastrophic — but all of it was a reminder that "self-hosted" is a verb, not a one-time purchase. You don't own your stack once; you keep owning it, every time a vendor changes the deal.

Here's what caught my eye from November 17–23, 2026.

---

## 1. Inkling 2 Mini — Real Reasoning, Finally Small Enough to Run at Home

**What it is:** [Inkling 2 Mini](https://thinkingmachines.ai/news/inkling-2-mini/) is Thinking Machines Lab's new open-weights model, and it's the most consequential local-AI release in a while — 1,466 points on Hacker News. It's a *looped transformer*: the middle layers run three times per token, so it applies more reasoning with fewer tokens. The result is a model that leads every open-weights release under 100B parameters on agentic-coding benchmarks like DeepSWE v1.1 (48.2%) and Vals Index v2.2 (46.5%) — and, crucially, [runs in as little as 5.4 GB of memory](https://github.com/ShinMegamiBoson/lookatmyquant) via aggressive NVFP4 quantization.

**Why it matters:** The local-LLM crowd has spent two years chasing a moving target: models kept getting *smarter*, but always at a size that demanded a $3,000 GPU. Inkling 2 Mini changes the geometry. The looped-transformer trick means you get reasoning that used to require a 65B+ parameter model out of something that fits on a *laptop*. For a self-hoster, that's the difference between "I read about local AI on Hacker News" and "I actually run an agent that can code, on the Mac mini in my closet." Combined with last week's [beginner's guide to Inkling/Qwen/Unsloth](https://www.gpupartner.com/blog/beginners-guide-local-ai-inkling-qwen-unsloth), the path from zero to a useful local agent just got dramatically shorter.

**The takeaway:** The "local AI is a toy" era is ending. This week it stopped being about *whether* you can run a capable model at home, and started being about *what you'll do with it*.

[**Introducing Inkling 2 Mini →**](https://thinkingmachines.ai/news/inkling-2-mini/)

---

## 2. Backblaze Quietly Rewrote Its Privacy Policy — and Self-Hosters Noticed

**What it is:** [Backblaze's updated Notice at Collection and Privacy Policy](https://www.backblaze.com/company/policy/privacy), effective December 1, 2026, set off a wave of [customer concern](https://www.neowin.net/news/backblaze-customers-worried-of-personal-data-salesharing-after-policy-update/) (254 points) over new language around the sale or sharing of personal information.

**Why it matters:** Backblaze B2 is the offsite backup layer for a *huge* slice of the self-hosting world — the S3-compatible bucket where your restic or Rclone dumps the one copy of your data that survives a house fire. It's earned that trust by being the boring, cheap, no-nonsense option. When the boring option starts adding "we may sell or share your personal information" clauses to its policy, the ground shifts. To be clear: your *encrypted backup blobs* are not suddenly being auctioned off, and Backblaze has said the changes are about legal compliance and analytics — but the reaction was the point. A community that preaches "you are your own cloud" is acutely aware that the *one* vendor you can't self-host is your offsite backup, and it watches that vendor's terms with a hawk's eye. Expect a fresh round of "encrypt before upload, always" evangelism, and a few people quietly re-evaluating their 3-2-1 strategy.

**The takeaway:** The trust you place in a backup vendor is renewed on *their* schedule, not yours. Read the policy change email when it arrives.

[**Backblaze's updated privacy policy →**](https://www.backblaze.com/company/policy/privacy)

---

## 3. Dumping the AES Key From a MyQ Garage Opener — Because Your Garage Door Should Be Yours

**What it is:** [Kusha's writeup](https://kusha.me/blog/stop_myq_homebridge_819lmb_rebooting/) (171 points, featured on Hackaday) documents extracting the AES key from a Chamberlain/LiftMaster MyQ Home Bridge (819LMB) so it stops crashing — and, more to the point, so it works without the vendor's cloud.

**Why it matters:** The MyQ Home Bridge is one of those "smart" devices that self-hosters love to hate: a garage door opener that insists on phoning home to Chamberlain's MQTT servers. Isolate it on an IoT VLAN with no internet, and it enters a loop — the connection attempts hang, the watchdog reboots the device, and your HomeKit garage control goes down every five to ten minutes. Kusha's fix is pure right-to-repair: point the cloud domains at a local service, spoof the MQTT handshake, and the device settles down. It's the same thesis as last week's Eight Sleep rooting — *every "smart" device is a self-hosting opportunity waiting to happen* — but this one hits closer to home, literally. A garage door opener is the most mundane appliance imaginable, and yet it ships with a cloud dependency so deep that unplugging it from the internet breaks the *button on your wall*.

**The takeaway:** If a device in your house won't work without a server a thousand miles away, that's not "smart" — it's a bug. And someone in this community is already writing the fix.

[**Preventing the MyQ Home Bridge from rebooting →**](https://kusha.me/blog/stop_myq_homebridge_819lmb_rebooting/)

---

## 4. GL.iNet Issued a Security Notice — Patch Your Travel Router

**What it is:** [GL.iNet's Security Notice 2026-11-20](https://www.gl-inet.com/en-us/blogs/blog/glinet-security-notice-2026-11-20) (174 points) flags a vulnerability affecting a range of their routers — the same GL.iNet boxes that are the default choice for self-hosters who want a portable WireGuard endpoint, a travel router, or a cheap OpenWrt-based home gateway.

**Why it matters:** GL.iNet is beloved in this community precisely *because* it ships OpenWrt-based firmware, plays nice with self-hosted VPNs, and doesn't try to lock you into a cloud. A security notice from a vendor you've recommended to friends is a different kind of event than a notice from some random IoT brand — it's a trust check. The responsible move (which GL.iNet made) is publishing the notice quickly and pushing firmware updates; the self-hoster's move is treating *every* network device — even the one you like — as something that needs patching on a schedule, not when you remember. If you've got a GL.iNet box running your travel VPN or a guest network, this is your reminder to log in and hit update.

**The takeaway:** Liking a vendor is not a security control. Patch the routers you trust first, because they're the ones actually on your network.

[**GL.iNet Security Notice 2026-11-20 →**](https://www.gl-inet.com/en-us/blogs/blog/glinet-security-notice-2026-11-20)

---

## 5. PcapAnalyzer — a Self-Hosted Packet Capture Analyzer With 27 Problem Detectors

**What it is:** [PcapAnalyzer](https://github.com/sebaandrada-cell/PcapAnalyzer) (160 points) is a new self-hosted tool that ingests `.pcap` files and runs them through 27 built-in problem detectors — flagging retransmissions, zero windows, suspicious TLS, DNS weirdness, and the other silent gremlins that make a network "feel slow."

**Why it matters:** Packet analysis has always been one of those skills that separates the homelab *enthusiasts* from the homelab *pros* — Wireshark is powerful but assumes you already know what to look for. PcapAnalyzer flips that: instead of handing you a million packets and a prayer, it hands you a *diagnosis* — "here are the 27 things I looked for, and here's what your capture tripped." For a self-hoster debugging a flaky VPN, a dropped IoT device, or a server that intermittently loses its mind, that's the difference between an afternoon of squinting at hex and a five-minute answer. It's part of a welcome trend of self-hosted tools that package hard-won operational expertise into something you can just run in a container.

**The takeaway:** The best self-hosted tools aren't just reimplementations of SaaS — they're the ones that bottle up expertise you'd otherwise have to earn the hard way.

[**PcapAnalyzer on GitHub →**](https://github.com/sebaandrada-cell/PcapAnalyzer)

---

## 6. Jeff Geerling Joined the NTP Pool — and the Homelab's Quiet Infrastructure Keeps Growing

**What it is:** [Jeff Geerling](https://www.jeffgeerling.com/blog/2026/i-joined-the-ntp-pool/) — the homelab community's de facto documentarian — joined the public NTP Pool with a Stratum 2 server fed by his Stratum 1 GPS-disciplined time Pi (152 points), and wrote up what it actually takes to contribute a time server responsibly.

**Why it matters:** The NTP Pool is one of the internet's least-glamorous and most-load-bearing pieces of shared infrastructure — millions of devices sync their clocks against volunteer-run servers, and the whole thing runs on people contributing boxes for free. Geerling's post is a lovely two-for-one: it's a genuinely useful guide (you *don't* need a timing-grade GNSS module to help; you just need to keep a box online and answer abuse emails), and it's a reminder of the ethos the whole self-hosting movement runs on. The same instinct that makes you run your own DNS or your own backups is the one that makes someone donate a time server to strangers. This week's news cycle was heavy on vendors changing terms and cloud dependencies failing — Geerling's post was a nice counterweight: people quietly *giving* infrastructure away because it matters.

**The takeaway:** Self-hosting isn't just about taking your data back — it's about the parts of the internet that only work because enough people chose to run a server for the common good.

[**I joined the NTP Pool →**](https://www.jeffgeerling.com/blog/2026/i-joined-the-ntp-pool/)

---

## 7. ExitPath — a Curated Map of Open-Source Ways Out of Slack, Notion, and M365

**What it is:** [ExitPath](https://exitpath-ruddy.vercel.app/) (251 points as a Show HN) is a catalog of open-source alternatives to the SaaS tools most teams are locked into — Slack, Notion, Microsoft 365, and the rest — organized so you can see, at a glance, what a self-hosted escape route actually looks like for each one.

**Why it matters:** "Just self-host it" is easy to say and hard to execute when the tool you're replacing is a whole *suite* with integrations, mobile apps, and a decade of muscle memory baked in. ExitPath does the useful, unglamorous work of mapping the terrain: for every SaaS tool, here's the Matrix/Element equivalent, the Outline or AppFlowy for docs, the Nextcloud for files, and the gotchas along the way. It's not a new tool so much as a *decision aid* — the thing that turns "I'd love to leave Slack" from a vague aspiration into a checklist with actual product names on it. For a community that's always one bad vendor announcement away from a migration, that kind of map is genuinely valuable.

**The takeaway:** The hardest part of de-clouding isn't running the software — it's knowing what's actually worth switching to. ExitPath does that homework for you.

[**ExitPath →**](https://exitpath-ruddy.vercel.app/)

---

## Honorable Mentions

- **Mayberry** (122 pts) — a [self-hosted little library branch](https://joinmayberry.com/) served over public web OPDS, for the ebook-hoarding crowd who want their own lending system.
- **Localcode** (55 pts) — [open-source agentic coding on your Mac](https://github.com/mjwsolo/localcode) with one command, for the "I want an agent but not their cloud" contingent.
- **OpenComputer** (125 pts) — an [open-source alternative to Devin](https://github.com/diggerhq/opencomputer) for autonomous coding agents.
- **Brazil open-sources its tax calculator** (787 pts) — [the federal tax authority published its calculator on GitHub under MIT](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/novembro/receita-federal-publica-primeiro-codigo-fonte-aberto-no-github-e-amplia-transparencia-da-reforma-tributaria), a rare and genuinely significant public-sector open-source move.
- **A Beginner's Guide to Local AI** (450 pts) — [Inkling, Qwen, and Unsloth](https://www.gpupartner.com/blog/beginners-guide-local-ai-inkling-qwen-unsloth), the practical pairing for item #1.

---

## Closing Thought

Last week I wrote that the self-hosting community had "stopped waiting for the cloud to be fair and started rebuilding the cloud." This week was the necessary corrective to that optimism: **even as you build, the ground keeps shifting.**

Inkling 2 Mini is a genuine gift — real reasoning, open weights, fits on a laptop. But it arrived in the same week that Backblaze rewrote its privacy terms, GL.iNet issued a security notice, and a garage door opener reminded us that "smart" usually means "rented from a vendor." The lesson isn't cynicism. It's that ownership is *maintenance*. You don't self-host once and win; you self-host continuously, re-examining your backup vendor, re-patching your routers, re-checking what your devices are phoning home to — every single week, because that's how often the terms change.

That's the quiet truth underneath all the "de-cloud everything" enthusiasm: the exit ramp is the easy part. The hard part is staying on the road, reading the fine print, and accepting that the job of owning your own stack never actually ends. This week made that job a little more tractable — a smarter small model, a better packet analyzer, a clearer map of the exits — and a little more necessary.

What did the vendors change on *you* this week? Drop a comment — I read every one.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
