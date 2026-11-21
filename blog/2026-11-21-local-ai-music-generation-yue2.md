---
layout: post.njk
title: "Run Local AI Music Generation (YuE2) on Your Homelab or Mac"
date: 2026-11-21
description: "Generate full songs with vocals and lyrics on your own hardware — no cloud, no per-track fees, no licensing wall. Here's how to run YuE2 locally on Apple Silicon (MLX) or a homelab GPU, and how it fits a self-hosted music stack built around Navidrome."
tags: ["ai-music", "yue2", "local-ai", "music-generation", "apple-silicon", "mlx", "homelab", "gpu", "navidrome", "self-hosted", "audio", "diffusion"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/local-ai-music-generation-yue2"
affiliate: false
cta: true
---

# Run Local AI Music Generation (YuE2) on Your Homelab or Mac

If you've been following this site, you already know the thesis: own the compute, own the data, own the stack. I've written about [quitting Spotify](/blog/2026-06-08-quit-spotify-intentional-listening), [self-hosting music with Navidrome and Soulseek](/blog/2026-05-16-self-hosted-music-navidrome-soulseek), and [running local LLMs on a Mac Mini](/blog/2026-06-12-local-llms-mac-mini-practical-guide). Those two threads — the *music* thread and the *local AI* thread — finally crossed.

The trigger is **YuE2**, the newest release from the open-source YuE project (originally out of HKUST and the MAP Foundation). YuE was already notable for one thing most "AI music" tools can't do: it generates **full songs — vocals, lyrics, and accompaniment together** — not just instrumental loops or a 30-second clip. YuE2 sharpens that into something genuinely usable, and it runs on hardware you probably already own.

The search landscape for this is weirdly empty right now. "Local AI music generator" returns a handful of cloud tools and a pile of stale Suno/Udio comparisons. Real answers for running YuE2 on your own box are nearly nonexistent. So here's the actual guide, written for people who already know how to `docker run` and would rather not pay a per-generation subscription for a tool they can host.

## Why YuE2 Is Different From Suno, Udio, and the Rest

Most of what people call "AI music generation" is a walled garden. Suno and Udio give you a text box and a "Generate" button, then charge you credits for every attempt. You don't control the model, the seed, the inference parameters, or where your audio goes. And you can't run it offline or self-host it.

YuE2 inverts that. It's an open-weights model that generates **lyrics + vocal + accompaniment in one coherent song**, and because it's open, the community has already produced quantized variants, MLX conversions for Apple Silicon, and Docker workflows. The trade-off is real: you supply the GPU and the patience. But the *capability* — a model that produces an actual singable track with a coherent structure — is the reason this crossed from "research novelty" to "homelab project."

Here's the honest framing before we get into hardware:

- **Cloud (Suno/Udio):** fastest, no setup, but per-track fees, no offline use, and your prompts/audio live on someone else's servers.
- **YuE2 local:** free after hardware, private, scriptable, and infinitely remixable — but you need a beefy GPU and a tolerance for long generation times.

If you've been running 7B–30B LLMs locally, you already understand this trade. YuE2 is just the same deal applied to audio.

## Hardware Reality Check

YuE is a *large* model — the original release landed around the 7B-parameter scale, and it's a diffusion-based transformer that has to produce a lot of tokens (audio is dense). That means VRAM and unified memory are the whole game.

| Hardware | Memory | What You Can Run | Rough Expectation |
|----------|--------|------------------|-------------------|
| M-series Mac (32GB+) | unified | MLX quantized builds | slow but functional; a minute of audio can take several minutes |
| Mac Studio / M-series Max/Ultra (64GB+) | unified | full-ish precision, longer songs | comfortable, still slower than a GPU |
| Single 24GB GPU (RTX 4090 / 3090) | 24GB VRAM | quantized inference | good — the sweet spot for a homelab |
| 2×24GB or 48GB+ (A6000, dual GPU) | 48GB+ VRAM | full model, longest generations | best experience |

The pattern should look familiar if you've read the [Mac Mini LLM guide](/blog/2026-06-12-local-llms-mac-mini-practical-guide): memory is the constraint, quantization is the lever, and "can it fit in 24GB" is the question that decides whether a model is a toy or a tool.

**The 8GB Mac Mini you're using for Ollama?** That's not going to cut it for YuE2. This is a 32GB-minimum kind of workload on Apple Silicon, and a real GPU is better. Plan accordingly.

## Two Paths: Apple Silicon (MLX) vs Homelab GPU (CUDA)

The community has effectively split YuE2 deployment into two camps, mirroring the local-LLM ecosystem.

### Path 1: Apple Silicon via MLX

If you're on a Mac with enough unified memory, the MLX path is the natural extension of what you already do with `mlx-lm`. The idea is the same: use Apple's MLX framework to run a quantized model efficiently on Metal.

The broad workflow:

```bash
# Create an isolated environment (Python 3.11+ recommended)
python -m venv ~/yue2-env && source ~/yue2-env/bin/activate

# Install MLX and audio deps
pip install mlx numpy soundfile

# Clone the YuE repo and fetch the MLX-converted weights
git clone https://github.com/multimodal-art-projection/YuE.git ~/YuE
cd ~/YuE
```

Then you load the model, feed it a lyric + style prompt, and generate. The MLX conversion handles the heavy lifting of mapping the model onto unified memory, so the same Mac that runs a 30B LLM can (slowly) generate music.

**Expectation-setting:** even on a fast M-series Max, generating a full-length track is a "go make coffee" operation, not an instant one. The MLX path wins on *accessibility* (you already own the Mac) and loses on *speed* (a CUDA GPU will beat it).

### Path 2: Homelab GPU via CUDA + Docker

For a Proxmox or bare-metal homelab box with an NVIDIA GPU, the CUDA path is where YuE2 actually shines. Wrap it in Docker and you've got a repeatable, scriptable music-gen service that fits right next to your other containers.

The shape of a typical setup:

```yaml
# docker-compose.yml (illustrative — pin your own image and weights path)
services:
  yue2:
    image: your-pinned/yue2:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./weights:/models
      - ./output:/output
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

The point isn't the exact image — YuE2 is new enough that tags are moving fast. The point is the *pattern*: pin your weights to a mounted volume, expose an output directory that Navidrome (or whatever you stream with) can read, and let the container do the work.

**Where this gets interesting** is the same place every homelab project gets interesting: you now have a *pipeline*, not just a toy.

## Fitting YuE2 Into a Self-Hosted Music Stack

This is the part that connects back to everything I've written before. A generated song isn't useful sitting in a `~/output` folder. It's useful when it lands in the same library you already stream from.

Here's the pipeline that ties YuE2 into a Navidrome-based stack:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   YuE2      │     │  Tagging /   │     │  Navidrome  │     │   Phone /   │
│  (GPU/MLX)  │────▶│  Normalize   │────▶│  (Library)  │────▶│   CarPlay   │
│  generates  │     │  (beets/ffmpeg)     │  scans      │     │   Web UI    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

Three steps:

1. **Generate.** YuE2 outputs your track as a `.wav` (or `.flac`/`.mp3` after conversion).
2. **Tag.** Run the output through your tagger of choice — `beets`, MusicBrainz Picard, or a simple `ffmpeg` metadata pass — so it has a title, artist, and album. YuE2 won't write clean tags for you.
3. **Drop and scan.** Move the file into your Navidrome library directory and trigger a scan. Done — it's now streamable everywhere you already listen.

This is the genuinely novel bit: you're not just *consuming* AI music, you're *producing* it into the same self-hosted library where your Soulseek downloads and ripped CDs live. A generated track and a downloaded FLAC become indistinguishable in the pipeline. That's the "own every track" thesis extended from *acquiring* music to *creating* it.

## The Honest Limitations (Read Before You Get Excited)

YuE2 is impressive and bleeding-edge, and "bleeding-edge" means rough edges:

- **Speed.** Full-song generation is slow. Budget minutes-per-minute-of-audio on a 24GB GPU, and longer on Apple Silicon. This is not a live jam tool.
- **Quality variance.** Lyrics can come out garbled or mispronounced, especially on non-English text. Vocals can drift off-key or mumble. You'll discard more generations than you keep — treat it like a sampler, not a finished record.
- **Prompt control.** You steer with lyrics + a style/genre description, but you don't get the fine-grained per-section control a DAW gives you. If you need a specific melody, you're out of luck.
- **Hardware gate.** This is a big-model workload. No 8GB machine, no cloud CPU instance, no Raspberry Pi.
- **Moving target.** The weights, quantization levels, and community tooling are changing weekly. What's true this month will shift next month.

None of this makes YuE2 not worth running. It just means you should set expectations to "fascinating, useful for sketching and experimentation" rather than "replaces my DAW and my library."

## Should You Actually Run It?

Run YuE2 locally if:

- You already have a 24GB+ GPU or a 32GB+ Apple Silicon machine sitting around.
- You're comfortable with the same workflow you use for local LLMs (git clone, venv, quantized weights, Docker).
- You want full control over your AI-generated audio — privacy, scripting, no per-track fees.
- You've already built the Navidrome/Soulseek stack and want to *create* music, not just collect it.

Skip it if:

- You just want a finished song in 30 seconds — Suno/Udio still win on convenience.
- You're on an 8GB Mac Mini or a CPU-only box.
- You want studio-grade, DAW-precise output. That's not what a diffusion music model does today.

The best mental model: **YuE2 is to Suno what a local LLM is to ChatGPT.** More setup, more hardware, more rough edges — but total ownership, zero marginal cost, and the ability to script and automate. If you've already made that trade once for language models, you already know whether you'll make it again for music.

## Conclusion

The interesting thing about YuE2 isn't the model itself — it's that the *local-first* answer to AI music now exists, and it slots into the same homelab stack that self-hosters have spent years building. Generate on your GPU, tag it, drop it in Navidrome, stream it anywhere. No credits, no cloud, no licensing wall between you and the audio.

This is early. The tooling is rough, the generations are hit-or-miss, and the hardware floor is real. But it's the first time "run an AI music generator on your own hardware" has been a legitimate sentence rather than a wish. And for a community that already owns its LLMs and owns its music library, that's a big deal.

Go make something weird.

---

*Running YuE2 on your own hardware and found a workflow or quantization that works well? The tooling here is changing faster than I can document it — drop your findings in the comments or on the fediverse. The community that figures out the rough edges first wins.*
