---
layout: post.njk
title: "RAM Prices Just Went Up 500%. Here's How to Build (or Upgrade) Your Homelab Anyway"
date: 2026-08-19
description: "The memory market just spiked — DDR4 and DDR5 prices are up as much as 500% in weeks, and the Hacker News thread hit 543 points. Nobody's written the actionable guide yet: buy now vs wait, how to spec around the shortage, and what it means for your homelab budget. Here it is."
tags: ["homelab", "ram", "memory", "hardware", "ddr5", "ddr4", "proxmox", "nas", "self-hosted", "budget", "upgrade", "build"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ram-prices-homelab-guide"
---

# RAM Prices Just Went Up 500%. Here's How to Build (or Upgrade) Your Homelab Anyway

The memory market just did the thing it does every few years, and this time it's ugly. DDR4 and DDR5 prices have spiked — some modules up **500%** in a matter of weeks — and the Hacker News thread on the shortage hit **543 points** and stayed on the front page all day.

The comments are full of the usual: "I should have bought last month," "this is the DRAM cartel again," "guess I'm not upgrading this year." What I *don't* see is anyone answering the question that actually matters for homelab people:

**What do I do *now*?**

Do I buy before it gets worse? Do I wait for the correction? Do I spec my next build around the shortage? Can I get away with less RAM than I planned?

That's the gap this post fills. I've spent the last year writing about homelab builds — the [Proxmox NAS guide](/blog/proxmox-nas-truenas-anas-turnkey/), the [local LLM guide](/blog/local-llms-mac-mini-practical-guide/), the [midyear review](/blog/midyear-homelab-review-2026/) — and I've been tracking hardware costs the whole time. Here's the actionable playbook for building or upgrading a homelab while RAM is expensive.

## First, What Actually Happened

Let me be precise, because "RAM prices up 500%" is a headline, not a strategy.

The spike isn't uniform. It's concentrated in specific categories:

- **DDR5 high-density modules** (32GB and 64GB DIMMs) — the worst hit, up 300–500% in some cases
- **DDR4 ECC UDIMMs** (the homelab workhorse for used enterprise gear) — up 150–300%
- **DDR4 non-ECC** (consumer desktop) — up 50–150%, the mildest of the bunch
- **SODIMMs** (laptops, mini PCs, NUCs) — up 100–250%

The drivers are the usual suspects: a DRAM supply squeeze from AI datacenter demand (every GPU server needs absurd amounts of HBM and DDR5), a fire at a major fab, and the predictable panic-buying that follows. The exact cause matters less than the shape of the curve: **prices spiked fast, and they won't come down fast.** Historically, DRAM corrections take 6–18 months, not weeks.

The key insight for homelab builders: **the shortage hits new, high-density, current-gen parts hardest.** Used and lower-density parts lag behind. That's your opening.

## Buy Now vs. Wait: The Honest Answer

The single most common question in the HN thread was "should I buy now or wait?" Here's the answer, broken down by what you're actually trying to do.

### Buy now if:

- **You're building a new machine and you *need* it running this quarter.** A build you can't use is worth $0. Paying 2x for RAM on a machine that's productive for 12 months beats waiting 12 months for a 30% price drop.
- **You're buying used enterprise DDR4 ECC.** This is the homelab sweet spot, and it's *less* affected than new DDR5. Used 32GB DDR4 ECC RDIMMs are still findable at reasonable prices, and they're only going to get scarcer as the shortage ripples outward.
- **You have a specific, time-sensitive need** — a project, a migration, a service you're paying cloud for right now that you want to bring in-house.

### Wait if:

- **You're upgrading "because it'd be nice."** If your current box works, the single best move in a shortage is to *not buy*. Every dollar you don't spend at the peak is a dollar that buys more RAM in 12 months.
- **You're speccing bleeding-edge DDR5.** This is the most inflated category. Unless you have a hard requirement, you're paying the maximum premium for the minimum benefit.
- **You can defer the whole build.** If the project is a "someday" homelab, someday just moved to next year.

### The rule of thumb

> **Buy used, buy lower-density, buy only what you need to be productive now. Defer everything else.**

That's the whole strategy in one line. The rest of this post is how to actually execute it.

## How to Spec Around the Shortage

This is the part nobody's written yet. When RAM is expensive, you don't just pay more — you *change what you spec*. Here's how.

### 1. Right-size your RAM, don't over-provision

The single biggest homelab mistake is over-provisioning RAM "just in case." In a normal market it's a minor waste. In a shortage it's a real cost.

Here's a realistic RAM budget for common homelab workloads:

| Workload | Realistic RAM | What people *think* they need |
|----------|--------------|-------------------------------|
| Proxmox + 5–10 LXC containers | 16–32GB | 64GB |
| NAS (TrueNAS/Unraid) + a few apps | 16–32GB | 64GB |
| Docker host, 20–30 containers | 32GB | 64–128GB |
| Local LLM (7B–13B quantized) | 16–32GB | 64GB+ |
| Local LLM (30B–70B quantized) | 64–128GB | 256GB |
| Frigate NVR + 4–6 cameras | 8–16GB | 32GB |
| Full *arr stack + Jellyfin | 16GB | 32GB |

The pattern is consistent: **people spec 2–4x what they actually use.** ZFS is the one legitimate exception — it'll happily eat every byte you give it for ARC cache — but even ZFS runs fine on 16GB for a home NAS. You don't *need* 128GB to serve Plex.

Before you buy, check what you're actually using. On Proxmox, `free -h` and the node summary page will tell you in 30 seconds. On a NAS, check the ARC hit ratio — if it's above 90%, more RAM helps; if it's below, you're already fine.

### 2. Buy used enterprise gear instead of new consumer parts

This is the single most effective way to dodge the shortage. Used enterprise DDR4 ECC is:

- **Cheaper per GB** than new consumer DDR5, even *after* the spike
- **More reliable** (ECC catches single-bit errors that would silently corrupt your data)
- **Abundant** — datacenters decommission servers constantly, and that supply doesn't dry up overnight

A used Dell R730 or HP DL380 with 128GB of DDR4 ECC RDIMMs can still be had for less than the cost of 64GB of *new* DDR5 right now. If you're building a NAS, a Proxmox host, or a general homelab server, used enterprise is almost always the right call — shortage or not.

The trade-off is power draw and noise. A 2U rack server idles at 80–150W and sounds like a jet engine. If that's a dealbreaker, look at used workstation-class gear (Dell Precision, HP Z-series) or mini PCs, which sip power but cap out at 64GB.

### 3. Prefer DDR4 over DDR5 for homelab workloads

Here's a truth that gets lost in the spec-sheet wars: **for homelab workloads, DDR4 is usually the better buy even at equal prices.**

DDR5's bandwidth advantage matters for gaming, video editing, and some AI inference. It matters *much less* for the things homelabs actually do — running containers, serving files, transcoding media, hosting VMs. Those workloads are latency- and capacity-bound, not bandwidth-bound. A 64GB DDR4 kit will serve a homelab just as well as a 64GB DDR5 kit, and right now it costs dramatically less.

The one exception is local LLM inference, where memory bandwidth directly limits token generation speed. If you're running a 70B model and want fast tokens, DDR5 (or better, a Mac with unified memory) is worth the premium. For everything else, DDR4 is the value play.

### 4. Buy the density sweet spot

RAM pricing is non-linear, and the shortage has made it *more* non-linear. Right now:

- **16GB modules** are the value sweet spot for DDR4 — best price-per-GB
- **32GB modules** are the value sweet spot for DDR5 — but still inflated
- **64GB+ modules** are where the 500% numbers live — avoid unless you have no choice

If you need 64GB, buy four 16GB sticks (DDR4) or two 32GB sticks (DDR5) rather than two 64GB sticks. You'll pay less per GB and leave upgrade headroom.

### 5. Leave upgrade headroom, but don't pay for it now

This is the counterintuitive one. In a shortage, the instinct is to max out RAM now so you never have to buy again. But that's backwards: **you're paying peak prices for capacity you won't use for a year.**

Instead, buy a motherboard with four DIMM slots and populate two of them. When prices correct (and they will), you buy the other two sticks at a discount. You get the machine running now, at a lower total cost, and you effectively dollar-cost-average your RAM.

The only time this fails is if the shortage *never* corrects — but DRAM has corrected after every single spike in the last 30 years. Betting against that is betting against history.

## What This Means for Your Homelab Budget

Let me put actual numbers on it, because "RAM is expensive" is useless without a dollar figure.

Here's a realistic mid-range homelab build, specced two ways — the "normal market" way and the "shortage-aware" way:

| Component | Normal-market spec | Shortage-aware spec |
|-----------|-------------------|---------------------|
| CPU | Ryzen 7 / Xeon E5 | Same (CPUs are unaffected) |
| Motherboard | 4× DIMM, DDR5 | 4× DIMM, DDR4 |
| RAM | 64GB DDR5 (2×32) | 32GB DDR4 ECC (2×16) |
| Storage | 2× 8TB HDD | Same |
| Boot | 500GB NVMe | Same |

The shortage-aware build costs **roughly 40–50% less on the RAM line item** and delivers 90% of the real-world performance for homelab workloads. And because you left two DIMM slots open, you can double the RAM later at (hopefully) lower prices.

If you want to run the full numbers for *your* build — hardware, power draw, and the break-even vs. cloud — I built a tool for exactly this. The [Homelab Cost Calculator](https://devhandbook.io/homelab-cost-calculator/) lets you plug in your hardware, your electricity rate, and your cloud alternative, and it'll tell you whether self-hosting actually saves you money. It's free, runs entirely in your browser, and it's been the most useful thing I've built for my own build decisions.

## The Bottom Line

The RAM shortage is real, it's bad, and it's not going away next week. But it's also not a reason to panic — it's a reason to be *deliberate*.

Here's the whole playbook, compressed:

1. **Buy now only if you need to be productive now.** Otherwise, wait.
2. **Buy used enterprise DDR4 ECC** — it's the homelab sweet spot and it's less affected by the spike.
3. **Right-size your RAM.** You probably need half of what you think you do.
4. **Prefer DDR4 over DDR5** for homelab workloads — the bandwidth doesn't matter for containers and file serving.
5. **Buy the density sweet spot** (16GB DDR4 / 32GB DDR5) and avoid 64GB+ modules.
6. **Leave DIMM slots open** and dollar-cost-average your upgrade when prices correct.

The people who get hurt by a shortage are the ones who buy at the peak out of fear. The people who come out ahead are the ones who buy used, buy less, and buy smart. Be the second kind.

And if you're on the fence about whether to build at all, run the numbers first — the [Homelab Cost Calculator](https://devhandbook.io/homelab-cost-calculator/) will tell you in two minutes whether self-hosting is worth it for your situation, RAM spike included.
