---
layout: post.njk
title: "Self-Hosted This Week: Open Weights, a Supermarket Exodus, and One Dad's Story Box — October 26 – November 2, 2026"
date: 2026-11-02
description: "Mistral drops a trillion-parameter open-weight model, Tesco walks away from VMware for Proxmox, a backdoor hides in a 'official' Claude Code extension, on-device AI gets a real local assistant, and a dad builds his kids an open-source story box. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "ai", "mistral", "proxmox", "vmware", "security", "local-llm", "hardware"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-11-02"
---

Last week was about owning the *silicon* in your house — rooting your TV, unlocking your GPU, de-Googling your phone. This week, that ownership instinct went *mainstream*. A trillion-parameter frontier model dropped its weights into the open. One of the biggest retailers on Earth quietly decided to walk away from VMware and toward Proxmox. And down at the very other end of the scale, a dad built his kids a story box because he refused to pay the vendor-lock-in tax on one.

The through-line: **"self-hosted" is no longer the hobbyist's secret — it's the direction the whole industry is drifting, whether it likes it or not.** Here's what caught my eye from October 26 – November 2, 2026.

---

## 1. Mistral Releases the Weights of Large 4 — a Trillion Parameters, Open

**What it is:** [Mistral Large 4 — nicknamed "Le Chonk" — is now open-weight](https://mistral.ai/news/mistral-large-4-oss/). It's a 1-trillion-parameter, natively multimodal model, and after three weeks of additional reinforcement learning it now leads the open-weight field on coding benchmarks (a 19.7% on Cognition's FrontierCode 2.0, top of the open pack) and defensive security. The announcement hit 1,716 points on Hacker News, the biggest story in the open-model world this week.

**Why it matters:** This is the story that makes "self-hosted AI" feel less like a compromise and more like the default. A trillion parameters is real frontier territory, and Mistral is explicitly shipping it with "customizable, self-hosted deployment options" in the pitch — the sovereign-AI framing, pointed straight at people who want to *own* their models rather than rent them. The catch is the one every self-hoster should read before they get excited: a trillion parameters is not going to run on a single RTX 3090. This is a *direction* story — proof that the frontier is opening up — more than a "download and run tonight" story. But the trajectory matters enormously for anyone building a homelab around local models: the ceiling keeps rising, and the weights keep getting released.

**The takeaway:** Open-weight models now touch the frontier. The homelab's job is no longer "can we run AI at all?" — it's "how much of this can we actually run, and how do we orchestrate it?"

[**Mistral Large 4 announcement →**](https://mistral.ai/news/mistral-large-4-oss/)

---

## 2. Tesco Walks Away from VMware, Heads for Proxmox

**What it is:** Tesco — the UK's largest supermarket chain, with thousands of stores — is [hiring for a role to migrate its edge infrastructure from VMware to Proxmox](https://itsfoss.com/news/tesco-vmware-exit/). The backstory is the one you already know: Broadcom's post-acquisition licensing. Tesco alleges one Broadcom offer this year came in at roughly *175% above* what its 2021 contract entitled it to. So they're leaving.

**Why it matters:** This is the homelab's chosen virtualization stack getting an enterprise seal of approval. Proxmox has been the self-hosting community's answer to VMware for years — open-source, no per-core licensing games, runs LXC *and* KVM, and it just [officially landed on ARM64](https://itsfoss.com/news/proxmox-ve-arm64/). Watching a company with Tesco's scale bet its store-edge infrastructure on it is the strongest possible validation of the exact software you run in your closet. It also hardens a lesson that's been building for a while: **perpetual licenses and "we'll always own this" vendor assumptions are liabilities.** The people who diversified early — onto Proxmox, onto open standards — are the ones who sleep well when a vendor gets acquired.

**The takeaway:** The gap between "enterprise virtualization" and "homelab virtualization" just closed a little more. If you're still on VMware, the writing on the wall is in a supermarket aisle now.

[**The Tesco/Proxmox story →**](https://itsfoss.com/news/tesco-vmware-exit/)

---

## 3. A Backdoor Hid in the "Official" Claude Code Extension on the Cursor Marketplace

**What it is:** Security firm Phorion published [a detailed advisory](https://phorion.io/blog/offical-claude-code-vsx-compromise/) on a compromised Claude Code VS Code extension found on the Cursor Marketplace — shipping an SSH backdoor. It hit 995 points on Hacker News.

**Why it matters:** If last week was about owning your hardware, this week delivered the reminder that *the software supply chain is the soft underbelly of everything you own.* The self-hosting crowd runs AI coding agents more than almost anyone — and those agents live inside your editor, with access to your files, your SSH keys, and your shell. A compromised "official-looking" extension is the nightmare scenario: you install it assuming it's the real thing, and it quietly phones home or opens a door. The deeper lesson is the one self-hosters already preach about their own stacks: **verify provenance, pin your sources, and treat "it looked official" as the weakest possible form of trust.** The homelab answer isn't to avoid the tools — it's to run them in ways you can audit.

**The takeaway:** The more powerful your local tooling gets, the more valuable the attack surface it sits on. Check your extensions; trust signatures, not logos.

[**Phorion's advisory →**](https://phorion.io/blog/offical-claude-code-vsx-compromise/)

---

## 4. Hob — an On-Device, Offline Alternative to Claude and ChatGPT

**What it is:** [Hob](https://github.com/FrigadeHQ/hob) is a free, open-source desktop assistant that runs open-weight models — Gemma, gpt-oss, and friends — *locally* on Mac, Windows, and Linux. Private, works offline, no subscription. It front-paged at 177 points as a "Show HN."

**Why it matters:** This is the counterweight to the trillion-parameter story, and honestly the one more people can actually use this week. Mistral Large 4 is the frontier you can admire; Hob is the frontier you can *run on the laptop in front of you.* It's part of a wave of "on-device coworker" tools trying to do what cloud assistants do, without the cloud — the same instinct that built the local-LLM homelab in the first place, packaged up so you don't have to hand-roll the whole thing. Tools like Hob are the bridge: they make "self-hosted AI" something a normal person installs in an afternoon, not a weekend project with a GPU and a prayer.

**The takeaway:** Local-first AI is graduating from "roll your own" to "just install it." The homelab's role is increasingly deciding *where* your models run and *who* you trust with your prompts — not whether you can run them at all.

[**Hob on GitHub →**](https://github.com/FrigadeHQ/hob)

---

## 5. Marelleo — a Dad's Open-Source Story Box for His Kids

**What it is:** [Marelleo](https://zebra.rodeo/en/blog/marelleo/) is a build log by a father of three who refused the Toniebox/Lunii business model — cheap hardware, but the *content* is where the money is made — and instead built his own ESP32-based story box: put a figurine on top, it plays a story. He started knowing nothing about electronics, learned by breaking things, and ended with something his kids use daily.

**Why it matters:** This is the self-hosting ethos distilled to its purest, least-scalable form, and it's why the 194 points it earned felt so earned. The whole project is a quiet argument: you don't have to accept the vendor-lock-in tax on the objects in your own home. A child's story box doesn't need a cloud account, a subscription, or a company that can change the terms whenever it likes — it needs an RFID reader, a speaker, and a parent willing to learn. The writeup is also refreshingly honest about the failure in the middle (a potentiometer wired wrong, the smell of "ski wax," a battery soldered on with no switch) — a reminder that the *real* self-hosted story is usually a messy one, and that's the point.

**The takeaway:** Not every self-hosted project needs to scale. Some just need to free a toy, or a feed, or a room, from someone else's terms. Those count too.

[**The Marelleo build log →**](https://zebra.rodeo/en/blog/marelleo/)

---

## 6. HackerTube — Karpathy Rebuilds His Feed So the Algorithm Can't Have It

**What it is:** Andrej Karpathy, tired of YouTube's "enshittified wall of slop," spent a weekend with his coding agent and built [HackerTube](https://karpathy.bearblog.dev/hacker-tube/) — a YouTube clone that only surfaces videos recommended on Hacker News, uses the 50% thumbnail, and keeps its state in your browser with no accounts. It hit 2,499 points.

**Why it matters:** Strip away the celebrity and this is the most relatable self-hosting story of the week, because *everyone* has felt it: you open a feed and realize it's been optimized for engagement, not for you. The self-hosted answer to "the algorithm serves me slop" has always been "fine, I'll curate my own." HackerTube is that instinct run at full speed — a reminder that "self-hosted" doesn't just mean servers in a closet; it means *reclaiming the surfaces you look at every day.* It's also a neat proof of the loop this whole movement is in: local AI agents are now powerful enough that one person can prototype an entire personalized media platform in a weekend, then own it outright.

**The takeaway:** The algorithm is a vendor too. When its terms stop working for you, the self-hosted move is to build your own.

[**HackerTube →**](https://karpathy.bearblog.dev/hacker-tube/)

---

## Honorable Mentions

- **Ghostty 1.4** (1,356 pts) — the [terminal emulator's latest release](https://ghostty.org/docs/install/release-notes/1-4-0). A favorite in the homelab/dev crowd for good reason.
- **BootGPT** (98 pts) — [a language model that lives in a boot sector](https://github.com/kerlenton/bootgpt). Peak "because I can" homelab energy.
- **Homebrew Cray-1A** (3 pts, but delightful) — a [functionally-accurate Cray-1A built at home](https://www.chrisfenton.com/homebrew-cray-1a/). The homelab's spiritual ancestor.
- **Radio-in-a-box** (13 pts) — [self-hosted internet radio with Icecast and Liquidsoap](https://github.com/skorotkiewicz/radio-in-a-box). Run your own station.
- **Oxide on self-hosted AI agents** (5 pts) — a [sober writeup on running AI agents on your own hardware](https://oxide.computer/blog/self-hosted-ai-agents), from the people who build the servers for it.

---

## Closing Thought

Three weeks of these roundups now, and the arc is getting clearer. Week one: the *people* keeping your software alive. Week two: the *hardware* you thought you owned. This week: the *industry* catching up to what self-hosters already knew.

A trillion-parameter model opened its weights. A supermarket giant fled to Proxmox. A dad freed his kids' toy. And underneath all of it, the same stubborn conviction: **you should own the things that matter to you, and increasingly, you can.** The frontier model, the virtualization layer, the AI assistant, the story box — every layer of the stack now has a credible "yours" option.

The harder lesson was the one buried in the Claude Code backdoor: more power, more open weights, more local AI means more attack surface, and "it looked official" was never much of a guarantee. Owning your stack now means *securing* your stack — verifying what you install, pinning where it came from, and auditing what it does. The freedom and the responsibility arrive together. That's the trade the whole movement has always been built on.

What did you run locally for the first time this week? Drop a comment — I read every one.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
