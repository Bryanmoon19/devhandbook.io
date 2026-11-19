---
layout: post.njk
title: "vGPU on a Consumer GeForce Card: SR-IOV Actually Works in 2026"
date: 2026-11-19
description: "NVIDIA has kept vGPU (splitting one GPU across multiple VMs) locked to expensive datacenter cards for years. A weeks-old open-source project called geforce-sriov finally unlocks SR-IOV on consumer Ampere and Ada GeForce cards — letting you carve a single 3090 or 4090 into multiple virtual GPUs for Proxmox. Here's what it actually does, what it costs, and how many VMs your card can really run."
tags: ["vgpu", "sriov", "gpu-virtualization", "proxmox", "nvidia", "geforce", "homelab", "kvm", "self-hosted", "gpu-passthrough", "virtualization"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-19-consumer-gpu-sriov-vgpu"
affiliate: true
cta: true
---

For years, there's been a quiet wall inside the homelab community, and you've probably hit it: **one GPU, one VM.** You can pass your GeForce card through to *one* virtual machine and get near-native performance — or you can leave it on the host for CUDA and transcoding — but you can't do both. The moment you want a Windows VM for gaming *and* a Linux VM for AI inference sharing the same card, the answer has always been "buy a second GPU."

That wall had a name: **NVIDIA's vGPU licensing.** The hardware capability to split a GPU into multiple virtual GPUs (SR-IOV) has been baked into GeForce silicon for two generations. NVIDIA just never exposed it — they reserved it for the $5,000+ datacenter and professional cards, where the per-seat vGPU license is the business model.

That changed a couple of weeks ago. A project called **[geforce-sriov](https://github.com/noon-at-cgn/geforce-sriov)** (187 stars in its first two weeks, created November 3, 2026) flips that switch on consumer **Ampere** and **Ada** cards — so a single 3090 or 4090 can present itself as multiple virtual GPUs to a Proxmox host. This is the post I wish I'd had, because the *practical* question isn't "does it work" (it does) — it's **"how many VMs can I actually carve out of *my* card, and what's the catch?"**

## The Problem It Solves

Let's be precise about what's broken, because the fix only makes sense against it.

With **PCIe passthrough**, your GPU is handed to a single VM, and while that VM runs, the host — and every other VM — has no access. Want to game in a Windows VM while your Plex container transcodes on the same card? Can't. Want two Linux VMs each running a small local LLM? Buy two cards. This is why homelab forums are full of "should I get a second 3060?" threads.

**SR-IOV** (Single Root I/O Virtualization) is the alternative. Instead of one card → one owner, the card exposes several lightweight *virtual functions* (VFs), and each VF is handed to a different VM as its own virtual GPU. The host keeps the physical card; every VM gets a slice. This is exactly what NVIDIA's commercial vGPU does on datacenter cards — it's just never been available to the cards normal people actually own.

geforce-sriov automates the three steps that reveal that hidden capability:

1. **A kernel module** exposes the SR-IOV capability to Linux (4 VFs by default, up to 16 on Ampere).
2. **An identity hook** makes the GeForce card present itself as its professional twin — an RTX A6000 for Ampere, an RTX 6000 Ada for Ada.
3. **A driver patcher** rebuilds NVIDIA's own vGPU host driver so it accepts the card.

The result: your 3090 looks like a 48 GB RTX A6000 to NVIDIA's vGPU software, and you can hand out virtual GPUs from it.

## The Honest Catch (Read This First)

There's a reason this is a "finally, but..." story, not a "free vGPU!" story. Two things will save you real pain if you know them up front:

**1. You still need NVIDIA's vGPU software and license.** geforce-sriov does *not* bypass or replace licensing. It's explicit about this in its own README and FAQ. You download the vGPU host driver (`NVIDIA-Linux-x86_64-580.159.01-vgpu-kvm.run`, vGPU software 19.5) from NVIDIA's Licensing Portal with your own entitlement, and guest licensing is your responsibility. The project is a *shim that makes the software run on consumer cards* — not a crack.

**2. It's beta, and it's software-only (which is both the safety and the sharp edge).** On the reassuring side: no firmware is flashed, no vBIOS is written, nothing is permanent, and `uninstall` restores NVIDIA's stock driver. The VFs and vGPU types vanish on every reboot and are recreated at boot. On the "be careful" side: it's weeks old, some failures need a full cold power-off (not a reboot), and only one driver version — **580.159.01** — is confirmed working.

Neither of these is a reason to avoid it. Both are reasons to *understand it* before you spend an afternoon on it.

## Does It Slow the GPU Down?

No — and this is the most encouraging number in the whole project. Because the tool's changes all happen at boot or when a VM starts, nothing runs in the hot path of the GPU's actual work. The project's own benchmark (a memory-modded RTX 3080 20 GB, one 4 GiB vGPU vs. the physical card on the host):

| Benchmark | Host (physical) | VM (vGPU) | VM / host |
|---|---|---|---|
| FP32 matmul | 20.47 TFLOPS | 20.54 TFLOPS | **100.3%** |
| FP16 matmul (tensor cores) | 58.35 TFLOPS | 58.54 TFLOPS | **100.3%** |
| Device memory copy | 681.7 GB/s | 704.4 GB/s | **103.3%** |

A vGPU VM runs at essentially full native speed of its share of the card. There's no 20% virtualization tax the way there is with some mediated-device approaches. That's the whole appeal.

## The Practical Question: How Many VMs Can *Your* Card Run?

This is where the existing [vGPU split calculator](/gpu-vgpu-split-calculator/) and the raw spec sheets actually meet reality — and where most "vGPU" write-ups (still datacenter-oriented) miss the consumer angle entirely.

The mechanics: NVIDIA's vGPU comes in fixed **profiles**, each a set VRAM size (an "RTXA6000-4Q" is 4 GB, a "RTX6000-Ada-2Q" is 2 GB, and so on up to the professional card's full 48 GB). geforce-sriov presents your consumer card *as* the 48 GB pro card, so the full profile list is offered — **but nothing stops you from picking a profile bigger than your physical VRAM.** That's the trap. The tool explicitly warns you to size profiles yourself; there's no automatic VRAM check.

The rule that keeps you out of trouble: **all running vGPUs must fit in physical VRAM, with room left for the host driver.** Let me work the two most common cards:

**24 GB card (RTX 3090, 4090):** four `4Q` (4 GB) vGPUs need 16 GB, plus a couple of GB for the host driver — fits comfortably, ~6 GB headroom. This is the sweet spot: **4 VMs at ~4–6 GB each**, which is enough for Plex transcoding, a lightweight Windows desktop, or a small quantized model per VM.

**16 GB card (RTX 4080, 4070 Ti):** four `4Q` vGPUs need 16 GB — that *doesn't* fit, because there's nothing left for the host driver. Drop to `2Q` (2 GB each) for four VMs, or run three `4Q` VMs and keep headroom. Either way, **fewer or smaller VMs than the 24 GB tier.**

That's the honest headline the datacenter guides won't give you: **a 24 GB consumer card realistically yields four usable virtual GPUs; a 16 GB card yields three to four smaller ones.** Everything else is licensing paperwork and patience.

## What You Actually Need (and Don't)

The requirements are specific, so here they are plainly:

**Supported cards:** Ampere (RTX 3090/3080/3070/3060 Ti/3060/3050) and Ada (RTX 4090/4080/4070 Ti/4070). The full device table also covers a long tail of laptop GPUs and workstation cards (RTX A4000, A2000, etc.). Turing, Pascal, and Maxwell are *not* supported — NVIDIA never enabled SR-IOV there. AMD is out of scope.

**The host:** Linux x86_64 with KVM and libvirt/QEMU — Proxmox VE is the natural fit — with IOMMU enabled and kernel 6.8+ (with livepatch support).

**The software (yours to obtain):** the NVIDIA vGPU host driver `.run` file from your own entitlement. Nothing NVIDIA-related is bundled or downloaded for you.

**The install:** `make`, then `sudo ./geforce-sriov setup` — twice, with a cold power-off/power-on in between. It prompts for the driver path and any cards you want. On later boots, the VFs restore automatically.

If a prerequisite is missing (like `nouveau` still loaded), `setup` stops and tells you exactly what to fix. That's the mark of a tool that's trying to be runnable, not a weekend hack.

## Should You Do It?

**Yes, if:** you're already running Proxmox, you already own (or can reasonably obtain) a vGPU entitlement, and you're tired of the one-GPU-one-VM wall. The performance is genuinely native, the setup is reversible, and the "carve one card into four" workflow is something no amount of PCIe passthrough can give you.

**No — or at least wait — if:** you were hoping this makes vGPU free. It doesn't; the license is the real cost and the real friction, and it always has been. If you don't have a licensing path, this project solves a problem you can't actually reach yet. A second-hand second GPU is still the cheaper answer for most people who just want two isolated VMs.

The honest summary: **geforce-sriov removes the *hardware* wall. It does not remove the *licensing* wall.** For the homelab crowd that already has, or can justify, the entitlement, that hardware unlock is exactly the piece that was missing — and it's why this project blew up in two weeks.

*The details in this post were verified against the geforce-sriov repository's README, FAQ, and device table as of November 19, 2026. If the project's status or supported-card list has changed since, its [docs](https://github.com/noon-at-cgn/geforce-sriov) are the source of truth.*

