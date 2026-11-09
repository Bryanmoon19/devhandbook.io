---
layout: post.njk
title: "Self-Hosted This Week: A Ten-Year-Old SSH Backdoor, Ubuntu's Silence, and a $10 Homelab — November 3 – 9, 2026"
date: 2026-11-09
description: "A decade-old OpenSSH bug lets attackers log into musl Linux boxes with any long password, Ubuntu sits on a critical kernel patch, AI models start rewriting their own weights, and someone runs a whole homelab on a $10 stick. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "security", "openssh", "ubuntu", "linux", "ai", "local-llm", "hardware"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-11-09"
---

Some weeks the self-hosting story is about *building* — new tools, new toys, new models. This week it was mostly about *the foundation under everything you've already built.* A bug that's been sleeping in the OpenSSH that ships with Alpine, OpenWrt, and half the Docker images on the planet for a decade quietly woke up. A critical kernel hole stayed unpatched on the most popular self-hosting distro there is. And while that was happening, the local-AI crowd got a genuinely strange new development: models that can read and write their *own* weights.

The through-line this week: **owning your stack is a trust exercise, and this week the trust got tested.** Here's what caught my eye from November 3 – 9, 2026.

---

## 1. sshole — a Decade-Old OpenSSH Bug That Lets Attackers In With Any Long Password

**What it is:** [sshole](https://sshhole.com) is the writeup of a bug that's been hiding in OpenSSH on *musl* libc systems — Alpine Linux, OpenWrt, Buildroot, Yocto, and a huge slice of the Docker images you've actually pulled — since 2016. The short version: accounts that should *never* accept a password at all (root, your key-only deploy user, LDAP users, the default user on Alpine's own AWS and Azure images) will happily accept *any* password longer than 256 characters. Any password. It hit 2,980 points on Hacker News.

**Why it matters:** This is the nightmare that keeps self-hosters up, in the most boring possible form. Nobody introduced the bug this week — it sat in the wild for a decade, waiting in the exact places the self-hosting crowd is most likely to reach for: the "minimal, secure-by-default" distro, the router firmware, the base image in your `docker-compose`. The lesson isn't "don't use Alpine." It's that *"minimal and popular" is not the same as "audited."* The musl build of OpenSSH is a less-traveled path than glibc, and less-traveled paths get less scrutiny — right up until someone with a fuzzer and an afternoon walks down them. Check your images, your routers, and your key-only accounts. If your threat model said "that box can't be brute-forced," this bug is your counterexample.

**The takeaway:** The most dangerous vulnerabilities aren't the new ones that get named and patched in a weekend — they're the old ones that quietly shipped to the places you trusted by default.

[**The sshole writeup →**](https://sshhole.com)

---

## 2. WTF Ubuntu? — a Critical Kernel Bug, Six Days With a Working Exploit, No Patch

**What it is:** [CVE-2026-98432](https://chalmovsky.com/posts/wtf-ubuntu) is a critical (CVSS 9.8) bug in the Linux kernel's TCP code, present since 2016, reachable remotely, and exploitable for full root. Anthropic says it built a working exploit. Debian patched it on October 16. As of the post going up on November 2 — and the frustration it captured earning 1,628 points — **Ubuntu, every supported release LTS included, still hadn't shipped a patch.**

**Why it matters:** Ubuntu is *the* default choice for self-hosters dipping a toe into a VPS or a bare-metal box. "Just install Ubuntu and run Docker" is practically the starter command of the entire homelab. And here was Ubuntu's flagship promise — "timely patches for critical vulnerabilities" — sitting in direct contradiction with nine days of "Vulnerable" on a remote root exploit. This is the flip side of the self-hosting bargain: you take responsibility for your own box, but you're still trusting *someone* to ship the fix. When the distro stalls, "self-hosted" means *you* are the one who has to notice, mitigate, and decide. The post is angry for a reason — this is the exact scenario that makes people re-read the word "enterprise-grade" with fresh suspicion.

**The takeaway:** Self-hosting means self-patching, or at least self-monitoring for patches. When the vendor's SLA is just marketing, the SLA that matters is yours.

[**WTF Ubuntu? →**](https://chalmovsky.com/posts/wtf-ubuntu)

---

## 3. Weight-Space Programming — Models That Read and Write Their Own Weights

**What it is:** A pair of posts this week lit up the local-AI corner of Hacker News. First, ["Astra can read and write weights to improve Qwen"](https://rikiyat.github.io/blog/weight-space-programming/) (2,960 points) claimed a model could inspect and modify another model's weights directly. Then [a counterpoint](https://honnibal.dev/blog/astra-read-write-misleading) (1,042 points) argued the claim was overstated — and Simon Willison followed up showing [Qwen 3.8 27B running on a laptop could genuinely interpret weights](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/).

**Why it matters:** This is the local-AI crowd's version of a gold rush, and the gold is the *weights themselves.* If a model can read its own parameters and reason about them, a whole class of tooling opens up — self-editing, self-inspecting, self-debugging models that live on your own hardware and answer questions about *why* they said what they said. For self-hosters, this is the frontier of "the model you run is the model you can audit." It also matters that the pushback got as much attention as the claim: the week's real signal wasn't any one demo, it was that *weight introspection is now a thing normal laptops can do,* even if the flashiest claims were overhyped. When Simon Willison can get a 27B model to read its own weights on a MacBook, the "inspectable model" idea stops being science fiction and starts being a project.

**The takeaway:** Interpretability is moving from "research paper" to "something you can run on your own box." The self-hosting instinct — trust but verify — is about to get a whole new set of tools aimed at the models themselves.

[**Astra weight-space writeup →**](https://rikiyat.github.io/blog/weight-space-programming/) · [**Simon Willison's laptop test →**](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/)

---

## 4. What I Run on a $10 OpenStick Homelab

**What it is:** [A writeup of a full homelab running on an OpenStick](https://blog.bosscher.ch/posts/openstick/) — a $10 (shipping included) gadget with 512 MB of RAM, four ARM Cortex-A53 cores at 1 GHz, 4 GB of eMMC, Wi-Fi, a 4G modem, and GPS. The author admits your watch is probably more powerful, then proceeds to run a surprising amount of self-hosting on it anyway. 785 points.

**Why it matters:** This is the antidote to the week's security gloom, and the purest expression of the homelab spirit: *you don't need much to start.* The barrier to self-hosting has never been the cost of the hardware — it's the decision to actually begin. A $10 stick, silently cooled, running real services, is a reminder that the movement was never about racks of enterprise gear; it was about taking a box that's *yours* and making it *useful.* It's also a gentle counterweight to the "I need a GPU and a server room before I can self-host anything" feeling that the local-LLM hype machine loves to generate. You can start with ten bucks and a Wi-Fi chip.

**The takeaway:** The homelab that matters isn't the one with the most cores — it's the one that actually exists. Start small, start silent, start at $10.

[**The OpenStick homelab →**](https://blog.bosscher.ch/posts/openstick/)

---

## 5. Your Tools Are Talking About You — Claude Code's Email Leak and Postman's Silent Plugins

**What it is:** Two trust stories landed back-to-back. [Claude Code was caught sending the user's email address to websites](https://github.com/anthropics/claude-code/issues/107757) in its User-Agent header (1,605 points), and [Postman was caught silently auto-installing AI plugins and attempting to share API data](https://github.com/postmanlabs/postman-app-support/issues/14370) (1,525 points).

**Why it matters:** For the self-hosting crowd, this is the recurring theme made personal: **the tools you run locally are increasingly making their own decisions about what leaves your machine.** Claude Code leaking an email address in a header, or Postman deciding it gets to share your API data, is exactly the kind of quiet exfiltration that self-hosting is supposed to *prevent* — except now it's coming from the AI assistant and the API client you run *on purpose.* The deeper point is that "local" and "private" are no longer synonyms. A tool can live in your editor or your tray and still phone home, install things you didn't ask for, and change the terms while you're not looking. The self-hosting answer is the same as always: read the changelog, watch the network, and don't assume "it runs on my machine" means "it only talks to my machine."

**The takeaway:** The attack surface moved inside your tools. Owning your stack now means auditing what your *assistants* are doing with your data, not just what your servers are.

[**Claude Code issue →**](https://github.com/anthropics/claude-code/issues/107757) · [**Postman issue →**](https://github.com/postmanlabs/postman-app-support/issues/14370)

---

## 6. Libghostty 1.0 — the Terminal Becomes a Library

**What it is:** [Libghostty 1.0](https://mitchellh.com/writing/libghostty-1-0) extracts Ghostty's terminal emulator engine into a reusable C library, so any application can embed a fast, modern terminal instead of rolling its own. 1,078 points.

**Why it matters:** The terminal is the front door of the self-hosted world — it's how you SSH into the box, run the container, tail the log, edit the config. Ghostty became the homelab/dev crowd's favorite terminal by being fast and GPU-accelerated, and now that engine is a library other projects can build on. That's a signal worth noting: the terminal is being treated as *infrastructure* rather than a standalone app, and the self-hosting tools you'll use next year (web UIs with embedded terminals, TUIs, remote-management dashboards) will inherit that polish for free. It's the kind of quiet, compounding win that makes the whole ecosystem a little better without anyone making a big deal of it.

**The takeaway:** Good primitives get reused. A terminal you can embed is a terminal that shows up everywhere you manage your own stuff.

[**Libghostty 1.0 →**](https://mitchellh.com/writing/libghostty-1-0)

---

## Honorable Mentions

- **Stringman** (843 pts) — an [$800 open-source room-scale gripper robot](https://neufangled.com/). The homelab's "because I can" energy applied to a physical arm.
- **Jailbreaking a Renault's navigation** (952 pts) — [changing the clock meant jailbreaking the car](https://blog.nns.ee/2026/11/02/renault-hack/). The right-to-repair instinct applied to a dashboard.
- **HackerBooks** (1,868 pts) — [HackerTube, but for books mentioned on HN](https://hackerbooks.org). Karpathy's feed-reclaiming idea, extended to reading.

---

## Closing Thought

Last week was about ownership going mainstream — open weights, a supermarket fleeing VMware, a dad freeing his kids' toy. This week the same instinct got pointed at the *trust layer* underneath all of it, and the results were sobering.

A decade-old SSH bug woke up in the distros and Docker images you reach for by default. The most popular self-hosting distro stalled on a remote-root patch while a working exploit sat in the open. And your own AI assistant turned out to be quietly leaking your email address. The pattern across all of it: **"secure by default" and "runs locally" are promises, not guarantees, and promises need to be checked.**

But the week wasn't all grim. A model on a laptop read its own weights, and a whole homelab ran on a $10 stick. Those two stories are the same story, really: the frontier keeps getting closer to *you* — closer to your hardware, your budget, your ability to inspect and own. The cost of that proximity is vigilance. The ten-dollar box and the trillion-parameter model both end up in the same place: on your desk, your responsibility, yours.

What did you patch, audit, or finally distrust this week? Drop a comment — I read every one.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
