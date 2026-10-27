---
layout: post.njk
title: "Build a Private Voice Assistant Satellite with ESP32-S3 (2026 Edition)"
date: 2026-10-27
description: "The software stack is solved — now put it in a box. This is the hardware follow-up to my self-hosted voice AI guide: a dedicated ESP32-S3 voice satellite with offline Whisper speech-to-text and a local LLM on the other end, plus a real parts list, a real cost breakdown, and the honest trade-offs between Willow, ESPHome Voice, and rolling your own. No cloud, just code."
tags: ["esp32", "esp32-s3", "voice-assistant", "whisper", "stt", "llm", "self-hosted", "hardware", "homelab", "willow", "espHome", "diy", "maker", "embedded", "no-cloud"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-27-esp32-s3-voice-assistant-satellite/"
affiliate: false
cta: true
---

The software problem is solved. That was the point of my [self-hosted voice AI guide](/blog/self-hosted-voice-ai-guide) — Kitten TTS, Piper, Kokoro, and faster-whisper give you a complete, local, free voice stack that runs on a Raspberry Pi. If you've read that post and followed along, you've got a server somewhere in the house that can transcribe speech and talk back.

But a voice assistant that lives inside a Docker container on your NAS isn't a voice assistant. It's a service. To be useful, it needs a body — a physical thing sitting on your desk or kitchen counter that hears you, captures clean audio, and pipes it back to the brain. That body is the part everyone skips, and it's where the project gets genuinely fun.

This is the hardware follow-up. I'm going to walk you through building a dedicated **ESP32-S3 voice satellite** — a small, always-on microphone-and-speaker puck that streams audio back to your self-hosted STT/LLM/TTS stack and speaks the reply. We'll cover the board choice, the audio chain, the firmware landscape (Willow, ESPHome Voice, and rolling your own), and a real parts list with a real price tag. The angle, as always: **no cloud, just code.**

## Why an ESP32-S3 Satellite, Not Another Pi?

You already have a server running the heavy stuff. So why not just plug a USB microphone into that Pi and call it a day? Two reasons: physics and placement.

The server is in a closet, a rack, or the basement — the worst possible place to hear a voice command from across the room. A voice assistant needs to live *where you talk*. And a full Raspberry Pi in every room is overkill: you'd be paying for a CPU that spends 99% of its life waiting for a wake word.

The ESP32-S3 is the sweet spot. It's a dual-core Xtensa LX7 microcontroller with a proper audio-capable I2S interface, native USB, and — critically — **hardware AI vector extensions** that make on-device audio processing (echo cancellation, wake-word detection, even lightweight keyword spotting) actually feasible. It draws under a watt, boots in milliseconds, and costs about five bucks. It's the difference between "a computer that can hear" and "a device that's *built* to hear."

The architecture is clean:

```
[ESP32-S3 satellite] --(LAN/Wi-Fi)--> [self-hosted STT + LLM + TTS server]
      |  mic in / speaker out               |  Whisper + Ollama + Piper/Kokoro
      |  wake word + audio streaming        |
```

The satellite does the dumb-but-important part — wake word detection, audio capture, buffering, playback, and the network hop. The server does the smart part you've already built. No cloud touches the audio, ever.

## The Hardware Landscape: Three Ways In

Before I give you a parts list, you need to know what firmware options actually exist, because they dictate the hardware you buy. There are three realistic paths, and they're not interchangeable.

### Path 1: Willow — the polished, batteries-included option

[Willow](https://heywillow.io) is the most turnkey ESP32-S3 voice-assistant firmware out there. It's a complete, self-hosted stack: the ESP32-S3 runs Willow's firmware (built on ESP-ADF and ESP-SR), which handles wake word ("Hi ESP"), audio streaming, and playback, while a Willow Inference Server — runnable via Docker — does the STT (Whisper) and TTS (OpenAI-compatible, pluggable) on your own hardware. It also ships a Home Assistant integration.

Willow's big advantage is that it *just works*. The firmware is prebuilt for a list of known-good boards (the ESP32-S3-BOX and BOX-3, and the M5Stack Echo/Atom variants), the wake word model is trained, and the audio pipeline is tuned. You flash, point it at your inference server, and talk. The downside is that it's opinionated: you're buying into their board list and their configuration model, and you're running their inference server rather than wiring directly into your existing voicebox/Kokoro stack.

**Pick Willow if:** you want a working voice assistant this weekend and don't care about customizing the guts.

### Path 2: ESPHome Voice — the Home Assistant native route

If you're already running [Home Assistant](https://www.home-assistant.io), the **ESPHome Voice Assistant** project is the natural fit. ESPHome now has first-class voice-assistant support via the `micro_wake_word`, `voice_assistant`, and `assist_pipeline` components. You write a YAML config, ESPHome compiles the firmware, and the satellite becomes a native Assist satellite — streaming audio back to your HA instance, which runs the STT (Whisper/Piper via Wyoming) and TTS.

This is the most "homelab" answer on the list: it slots into infrastructure you likely already have, it's config-as-code, and it's endlessly tinkerable. The wake word runs on-device (microWakeWord), the audio processing is solid, and you get every Home Assistant voice feature for free. The cost is that you're now tied to the ESPHome/HA ecosystem — if you don't run HA, this is a lot of scaffolding.

**Pick ESPHome Voice if:** you run Home Assistant and want your satellite to control your lights, not just chat.

### Path 3: Roll your own with ESP-ADF / ESP-SR

This is the "no cloud, just code" purist path, and it's the one the Hacker News crowd has been circling. Last year an HN Show post — *"Live speech-to-text on an ESP32-P4 microcontroller, no cloud"* — did the rounds, and the takeaway was that **you can now run STT directly on Espressif silicon.** The P4 is the flagship for that, but the S3 gets you most of the way with ESP-SR's on-device keyword spotting plus streaming audio to a local Whisper.

Rolling your own means using Espressif's [ESP-ADF](https://github.com/espressif/esp-adf) (Audio Development Framework) and [ESP-SR](https://github.com/espressif/esp-sr) (speech recognition) libraries directly. You get wake word via WakeNet, command recognition via MultiNet, and full control over the audio pipeline — I2S config, AEC (acoustic echo cancellation), VAD (voice activity detection), the works. You write C, you own every byte of the audio path, and you integrate with *your* stack, not someone else's server.

This is the most work by a wide margin, but it's also the most educational and the most flexible. If the whole point of the project is to understand and own the thing, this is the path.

**Pick roll-your-own if:** you want to learn the audio stack, or you have specific hardware/requirements that Willow and ESPHome don't cover.

## The Parts List (BOM) and Real Cost

Here's the concrete bill of materials for a single-room satellite. I'm listing the ESP32-S3-BOX-3 as the core because it's the best-documented board across all three firmware paths — it has a built-in speaker, a decent microphone array, a screen, and a case, which removes about four separate purchases. Prices are ballpark 2026 street prices.

| # | Part | Why | Cost |
|---|------|-----|------|
| 1 | **ESP32-S3-BOX-3** (or M5Stack Echo) | The satellite itself: dual-core S3, dual mic array, speaker, screen, case | $35–$45 |
| 1 | **USB-C power supply + cable** | Always-on power; the S3 sips under a watt | $8 |
| 1 | **microSD card (16GB)** | Optional — audio buffer / wake-word model storage on the BOX-3 | $6 |
| 1 | **Speaker upgrade (optional)** | The BOX-3's onboard speaker is thin; a 3W I2S speaker improves TTS clarity | $10 |
| — | **Server (already owned)** | The Pi/mini-PC you run Whisper + Ollama + Piper on. If you don't have one, a Raspberry Pi 5 (8GB) is ~$80 | $0–$80 |

**Total per satellite: ~$50–$70** (excluding a server you probably already have). Add a second or third satellite for another ~$50 each, and you've got whole-house voice for the price of a single Amazon Echo Show — except the Echo subsidizes itself by selling your voice data and the satellite doesn't.

The honest cost caveat: the server is the real expense if you don't own one. Whisper (even `faster-whisper` with the `small` or `medium` model) wants a few gigs of RAM and a decent CPU; a local LLM wants more. A Raspberry Pi 5 8GB handles `whisper small` + a 3B-class quantized LLM + Piper comfortably, and it's the budget anchor. A used mini-PC or an M-series Mac mini does it faster.

## Choosing Your Board (Quick Decision Table)

| Board | Built-in mic array | Built-in speaker | Screen | Best firmware path | Notes |
|-------|-------------------|------------------|--------|-------------------|-------|
| **ESP32-S3-BOX-3** | ✅ dual mic | ✅ | ✅ 2.4" | Willow, ESPHome, DIY | The default pick; most documented |
| **M5Stack Echo** | ✅ dual mic | ✅ | ✅ small | Willow, ESPHome | Compact, cheaper, no camera |
| **ESP32-S3-DevKitC + I2S breakout** | ❌ (add INMP441) | ❌ (add MAX98357A) | ❌ | DIY | Cheapest, most flexible, most soldering |
| **ESP32-S3-BOX (gen 1)** | ✅ dual mic | ✅ | ✅ | Willow (legacy) | Cheaper used, but older |
| **ESP32-P4 (future-proof)** | ❌ | ❌ | ❌ | DIY | On-device STT, but still early |

For 90% of readers, **buy the ESP32-S3-BOX-3.** It's the reference hardware for both Willow and ESPHome Voice, it's on Amazon and AliExpress from every vendor under the sun, and the onboard mic array + speaker means you're up and running without touching a soldering iron. If you want to build a *custom* enclosure or do multi-room on a budget, the DevKitC + INMP441 mic + MAX98357A amp route is the tinkerer's path and it drops the per-unit cost under $25.

## The Build: ESPHome Voice (Fastest Path to Working)

Let me give you the fastest working path, because a guide that only describes *what* to buy isn't a guide. I'll use ESPHome Voice since it's the most homelab-native and it works with a stack you can stand up in an evening.

### Step 0 — Have a brain

You need your STT + TTS + LLM running somewhere. From my [software guide](/blog/self-hosted-voice-ai-guide), the one-command brain is voicebox (STT + TTS in one container) plus Ollama for the LLM:

```bash
# STT + TTS in one OpenAI-compatible container
docker run -d --name voicebox -p 8000:8000 \
  -e TTS_ENGINE=piper \
  -e STT_ENGINE=faster-whisper \
  ghcr.io/agjs/voicebox:latest

# Local LLM
docker run -d --name ollama -p 11434:11434 ollama/ollama
ollama pull llama3.2:3b   # or whatever 3B-class model your box can run
```

### Step 1 — Flash the ESP32-S3-BOX-3

Install ESPHome and adopt the board over USB. On a Mac or Linux box:

```bash
pip install esphome
esphome wizard voice-satellite.yaml
```

In the wizard, pick the `esp32-s3-box-3` board (or `m5stack-atom-echo` for the M5Stack). Then paste this minimal voice config into `voice-satellite.yaml`:

```yaml
esphome:
  name: voice-satellite
  friendly_name: Voice Satellite

esp32:
  board: esp32-s3-box-3
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

i2s_audio:
  - id: i2s_in
    i2s_lrclk_pin: GPIO45
    i2s_bclk_pin: GPIO17

microphone:
  - platform: i2s_audio
    id: mic
    adc_type: external
    i2s_din_pin: GPIO16
    pdm: false

speaker:
  - platform: i2s_audio
    id: speaker
    dac_type: external
    i2s_dout_pin: GPIO17
    mode: mono

voice_assistant:
  microphone: mic
  speaker: speaker
  noise_suppression_level: 2
  auto_gain: 31dBFS
  volume_multiplier: 2.0
  on_wake_word_detected:
    - logger.log: "Wake word detected!"
  on_end:
    - logger.log: "Pipeline finished."

micro_wake_word:
  model: hey_jarvis
```

(The exact GPIO pins vary by board revision — the ESPHome docs for `esp32-s3-box-3` have the authoritative mapping; I'm showing the structure, not asking you to copy pin numbers blindly.)

### Step 2 — Point it at Home Assistant

In Home Assistant, the satellite auto-discovers over the ESPHome API. Adopt it, then set up an Assist pipeline with Whisper (via the Wyoming `wyoming-faster-whisper` add-on) for STT and Piper (via `wyoming-piper`) for TTS, and optionally Ollama as the conversation agent. Assign that pipeline to the satellite, and you're done: "Hey Jarvis" wakes it, your speech streams to HA, Whisper transcribes it, the LLM answers, and Piper speaks it back through the satellite's speaker.

### Step 3 — (Optional) Wire in the LLM for actual conversation

Default Assist handles home-control commands out of the box. To make it *chat*, add Ollama as a conversation agent in HA, or skip HA and point the satellite's pipeline at your own voicebox/Ollama stack directly if you went the roll-your-own route.

The whole build — flash to working — is a couple of hours on a Saturday, most of it waiting for the first ESPHome compile.

## The Roll-Your-Own Path (For the "Just Code" Purists)

If ESPHome and Willow feel like too much abstraction, the ESP-ADF + ESP-SR route is where you actually learn the audio stack. The core loop is:

```c
// Pseudocode: the satellite's main loop
void app_main() {
    setup_wifi();
    setup_i2s();              // mic in + speaker out
    wakenet_init("hey_jarvis");
    vad_init();

    while (1) {
        if (wakenet_detect()) {
            start_recording();
            while (!vad_silence(1200ms)) {   // VAD: stop after 1.2s of silence
                buffer_audio();
            }
            send_audio_to_server(buffer);     // HTTP POST to your Whisper endpoint
            play_response(receive_tts());     // stream Piper audio back to the speaker
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

That's the whole architecture in five lines: wake word → capture → stream → transcribe → speak. The HN ESP32-P4 demo proved the *fully on-device* version of this is now real (STT running right on the chip, no server round-trip), and while the S3 isn't quite there for full Whisper, it's the natural stepping stone — you learn the pipeline with a server in the loop, then graduate to the P4 when you want it all on the chip.

I won't pretend this path is quick. ESP-ADF is a deep framework, the IDF build system takes some getting used to, and debugging audio over serial logs is a rite of passage. But it's the only path where you end up genuinely understanding *why* the pipeline is shaped the way it is — and the one where you can build something the turnkey firmware can't.

## Honest Trade-Offs (Read Before You Buy)

Three things I wish someone had told me before I started down this road:

**1. Wake words are still the hard part, and they're the "cloud" in most devices.** A commercial Echo or HomePod sends a rolling audio stream to the cloud precisely because on-device wake-word accuracy is hard. The S3's on-device wake word (microWakeWord / WakeNet) is *good* but not *great* — expect the occasional false trigger and the occasional miss, especially in noisy rooms. It's the trade you make for keeping audio local, and it's worth it, but set your expectations.

**2. Far-field audio is a physics problem, not a software problem.** A $5 mic array on a desk will not match a $100 dedicated far-field array with beamforming and multi-mic DSP. The BOX-3's dual mic is fine for a desk or counter within a few feet. Across a large, noisy room, it'll struggle. If you want whole-room coverage, budget for a better mic array (or multiple satellites, which is honestly the smarter answer).

**3. Latency is a chain, and the server is the longest link.** Wake word (~100ms) + streaming + Whisper transcription (~200-500ms for `small`) + LLM generation (~1-3s for a 3B model) + TTS + playback. A snappy assistant is maybe 1-2 seconds end to end; a slow one is 5+. The single biggest lever is the LLM — a 3B-class quantized model responds fast, a 13B does not. Tune the model size to your patience.

## The Cost vs. The Alternative

Let me make the value argument concrete, because "no cloud" is a principle, but you still have to pay for hardware:

| | One ESP32-S3 satellite | One Amazon Echo (2026) | One Google Nest |
|---|------------------------|------------------------|-----------------|
| **Upfront cost** | ~$50–$70 | ~$50–$100 | ~$100 |
| **Ongoing cost** | $0 | $0 (you're the product) | $0 (you're the product) |
| **Audio leaves your home** | Never | Always | Always |
| **Works offline** | ✅ Yes | ❌ No | ❌ No |
| **You can change the brain** | ✅ Swap the LLM anytime | ❌ Locked | ❌ Locked |
| **Open source** | ✅ Fully | ❌ | ❌ |
| **Wake-word accuracy** | Good | Excellent | Excellent |

The Echo is cheaper in *dollars* and better at wake words. The satellite is cheaper in *everything that matters to a self-hoster*: privacy, ownership, offline operation, and the freedom to swap Whisper for Moonshine, Piper for Kokoro, or a 3B LLM for a 70B whenever you feel like it. You're not renting a voice; you're building one.

## Conclusion: Put a Body On It

The self-hosting community has spent two years obsessing over the *brain* — the STT models, the TTS quality, the local LLMs — and rightly so, because the brain is what makes it real. But a brain without a body is just a container in a closet. The ESP32-S3 satellite is the body, and it's finally cheap enough and easy enough that "build your own voice assistant" isn't a month-long research project anymore. It's a Saturday.

Buy the BOX-3. Flash ESPHome Voice if you run Home Assistant, or Willow if you want the polished path, or dive into ESP-ADF if you want to own the pipeline. Point it at the voicebox + Ollama stack from my last post. Put it on your desk, say the wake word, and ask it something.

Then notice what *doesn't* happen: no blue light phoning home, no "we listened to this recording to improve our services" in a terms-of-service you never read, no server in a data center you don't control deciding what you said. Just a $50 board on your desk, your code, and a voice that belongs to you.

That's the whole point.

---

*Built a voice satellite yourself, or hit a snag I didn't cover? I'd love to hear it — especially if you went the ESP-ADF route and have a story about debugging I2S at 2 AM. Find me on [GitHub](https://github.com/Bryanmoon19) or drop a comment below.*
