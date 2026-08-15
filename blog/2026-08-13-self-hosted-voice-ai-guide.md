---
layout: post.njk
title: "Self-Hosted Voice AI: The Complete Guide to Running Your Own TTS and STT Stack"
date: 2026-08-13
description: "Stop paying for cloud TTS APIs. Kitten TTS (1,003 HN points, 15K GitHub stars), Piper, Kokoro, and voicebox give you a complete self-hosted voice AI stack that runs on a Raspberry Pi. Here's how to set it all up."
tags: ["self-hosted", "tts", "stt", "voice-ai", "kitten-tts", "piper", "kokoro", "whisper", "homelab", "open-webui", "home-assistant", "docker"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-voice-ai-guide"
---

# Self-Hosted Voice AI: The Complete Guide to Running Your Own TTS and STT Stack

Voice AI has been stuck in a weird place for self-hosters. On one hand, we've had great speech-to-text with Whisper for years. On the other, text-to-speech has been a wasteland of robotic voices, cloud API lock-in, and models that need a GPU the size of a small car.

That changed in 2025-2026. A wave of open-source TTS models landed that are small enough to run on a Raspberry Pi, sound natural enough to fool your family, and are completely free. No API keys. No per-character billing. No "your free tier expired" emails at 2 AM.

This guide covers the four tools that make up a complete self-hosted voice AI stack: **Kitten TTS** (the tiny newcomer that hit #1 on Hacker News), **Piper** (the battle-tested workhorse), **Kokoro-82M** (the quality contender), and **voicebox** (the server that ties it all together with STT).

## Why Self-Host Voice AI?

Before we dive into the tools, let's talk about why you'd want to run your own voice stack instead of using ElevenLabs, OpenAI TTS, or Google Cloud Text-to-Speech.

**Cost.** Cloud TTS is expensive at scale. ElevenLabs charges $5/month for 30,000 characters — that's roughly 20 minutes of audio. OpenAI's TTS-1 is $15 per million characters. If you're building a voice assistant, generating audiobooks, or running a podcast pipeline, those costs add up fast. Self-hosted is free after the hardware.

**Privacy.** Your text goes to their servers. For voice assistants, that means every conversation in your home potentially routes through a third party. For audiobook generation, it means uploading entire books to cloud APIs. Self-hosted keeps everything local.

**Latency.** Round-trip to a cloud API adds 200-500ms minimum. For real-time voice assistants, that's the difference between natural conversation and awkward pauses. Local inference on modern hardware can be sub-100ms.

**Customization.** Want to fine-tune a voice on your own voice samples? Clone a specific speaking style? Adjust prosody for different contexts? Local models give you control cloud APIs don't.

**Offline.** Your voice assistant works when the internet doesn't. This matters more than you'd think — ISP outages, travel, or just wanting things to work in the basement.

## The Stack at a Glance

| Tool | Type | Size | Quality | Speed | Best For |
|------|------|------|---------|-------|----------|
| **Kitten TTS** | TTS | 25MB | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | Edge devices, real-time |
| **Piper** | TTS | ~50MB/voice | ⭐⭐⭐ | ⚡⚡⚡⚡ | Home Assistant, reliability |
| **Kokoro-82M** | TTS | 82M params | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Audiobooks, highest quality |
| **voicebox** | TTS+STT | Docker | Varies | Varies | All-in-one server |
| **faster-whisper** | STT | ~1.5GB | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Speech recognition |

## Kitten TTS: The 25MB Powerhouse

Kitten TTS exploded onto the scene and hit **1,003 points on Hacker News** with 361 comments — and for good reason. It's a state-of-the-art TTS model that's **under 25MB**, runs on CPU only, and produces genuinely expressive speech.

### What Makes It Special

- **15 million parameters** — smaller than most images on a web page
- **8 voices** — four male, four female, all natural-sounding
- **CPU-only** — no GPU required, runs on Raspberry Pi
- **ONNX runtime** — portable across platforms
- **Int8 + FP16 quantization** — tiny footprint without sacrificing quality
- **Runs anywhere** — Raspberry Pi, low-end smartphones, wearables, browsers

The team behind it (KittenML) built it because existing expressive open-source TTS models required big GPUs, and cloud alternatives were too expensive for high-frequency use. Their goal: frontier-quality TTS that runs on edge devices.

### Quick Start

```bash
# Clone the repo
git clone https://github.com/KittenML/KittenTTS.git
cd KittenTTS

# Install dependencies
pip install -r requirements.txt

# Download the model (25MB)
python download_model.py

# Generate speech
python synthesize.py --text "Hello, I'm running entirely on your CPU." --voice female_1 --output hello.wav
```

That's it. No Docker, no GPU drivers, no CUDA toolkit. On a Raspberry Pi 4, it generates speech faster than real-time. On a modern laptop, it's nearly instantaneous.

### Voices and Quality

The eight included voices cover a good range. They're not ElevenLabs-level hyper-realistic, but they're far beyond the robotic "computer voice" you'd expect from a 25MB model. The expressiveness — pitch variation, natural pauses, appropriate emphasis — is what sets it apart from older lightweight TTS engines.

The current release is trained on less than 10% of their total data, so quality will only improve. The team has hinted at multilingual support and voice cloning in future releases.

### Docker Deployment

```bash
# Run Kitten TTS as an API server
docker run -d \
  --name kitten-tts \
  -p 8000:8000 \
  ghcr.io/kittenml/kitten-tts:latest

# Generate speech via API
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Your self-hosted voice AI is ready.", "voice": "female_1"}' \
  --output output.wav
```

## Piper: The Battle-Tested Workhorse

If Kitten TTS is the exciting newcomer, **Piper** is the reliable veteran. With over **11,000 GitHub stars**, it's the most widely deployed open-source TTS engine in the self-hosted world. It's the default TTS backend for Home Assistant's voice pipeline, and for good reason.

### What Makes It Special

- **Fast** — optimized C++ inference with ONNX runtime
- **Dozens of voices** — multiple languages, male/female variants
- **Low resource usage** — runs comfortably on a Raspberry Pi 3
- **Home Assistant native** — first-class integration via Wyoming protocol
- **Mature** — battle-tested across thousands of deployments
- **Streaming output** — audio starts playing before generation completes

### Quick Start

```bash
# Install via pip
pip install piper-tts

# Download a voice model
# Voices available at: https://huggingface.co/rhasspy/piper-voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Generate speech
echo "Welcome to your self-hosted voice assistant." | \
  piper --model en_US-lessac-medium.onnx --output_file welcome.wav
```

### Home Assistant Integration

This is where Piper really shines. Home Assistant's voice pipeline uses Piper as the default TTS engine:

```yaml
# Add to Home Assistant via the Wyoming integration
# Settings → Devices & Services → Add Integration → Wyoming Protocol
# Host: localhost (or your Piper server IP)
# Port: 10200
```

Or run it as a Docker container:

```bash
docker run -d \
  --name piper \
  -p 10200:10200 \
  -v /path/to/voices:/voices \
  rhasspy/wyoming-piper \
  --voice en_US-lessac-medium
```

Once connected, any Home Assistant voice command that generates a spoken response will use Piper. "What's the weather?" → spoken forecast. "Turn off the lights" → spoken confirmation. All local, all free.

### Voice Quality

Piper's voices are good but not great. They're clear and intelligible — perfect for assistant-style interactions — but they won't fool anyone into thinking a human is speaking. For audiobooks or content creation, you'll want Kokoro. For quick assistant responses, Piper is ideal.

## Kokoro-82M: The Quality Contender

**Kokoro-82M** sits at the opposite end of the spectrum from Kitten TTS. Where Kitten prioritizes tiny size and universal compatibility, Kokoro prioritizes voice quality. With 82 million parameters, it produces some of the most natural-sounding speech available in open-source TTS.

### What Makes It Special

- **82M parameters** — 5x larger than Kitten, but still manageable
- **Near-studio quality** — the best open-source TTS voice quality available
- **Voice mixing** — blend multiple voices for unique results
- **Auto-stitching** — handles long texts by intelligently segmenting and joining
- **Multiple backends** — PyTorch, ONNX, and Rust implementations available
- **Active ecosystem** — FastAPI wrappers, audiobook generators, MCP servers

### Quick Start (via Kokoro-FastAPI)

The easiest way to run Kokoro is through the excellent Kokoro-FastAPI Docker image (5,300+ GitHub stars):

```bash
docker run -d \
  --name kokoro \
  -p 8880:8880 \
  ghcr.io/remsky/kokoro-fastapi:latest

# Generate speech
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kokoro",
    "input": "The quality difference is immediately noticeable. This sounds like a real person.",
    "voice": "af_heart"
  }' \
  --output kokoro_output.wav
```

The API is OpenAI-compatible, so any tool that works with OpenAI's TTS endpoint can be pointed at your local Kokoro instance with a URL change.

### Audiobook Generation

Kokoro really shines for long-form content. Tools like **abogen** (5,600+ stars) and **epub2tts-kokoro** can turn entire books into audiobooks:

```bash
# Generate an audiobook from an EPUB
pip install epub2tts-kokoro
epub2tts my-book.epub --voice af_heart --output my-book-audiobook/
```

The auto-stitching handles chapter boundaries, paragraph breaks, and long passages intelligently. A full novel takes a few hours on a modern CPU — not real-time, but overnight is perfectly reasonable.

### Performance Notes

Kokoro needs more resources than Kitten or Piper. On a Raspberry Pi 5, it runs at roughly 0.5x real-time (30 seconds to generate 60 seconds of audio). On an M-series Mac or modern x86 CPU, it runs at 2-3x real-time. A GPU isn't required but helps significantly for batch processing.

## voicebox: The All-in-One Voice Server

Here's where things get interesting. **voicebox** (agjs/voicebox) is a relatively new project that combines everything into a single, self-hosted, OpenAI-compatible speech server. It's the missing piece that turns individual TTS/STT engines into a unified voice API.

### What It Does

- **Speech-to-text** via faster-whisper
- **Text-to-speech** via Piper and/or Kokoro
- **OpenAI-compatible API** — drop-in replacement for OpenAI's `/v1/audio/*` endpoints
- **Docker deployment** — single container, single port
- **Open WebUI integration** — voice chat in your local AI chat interface
- **CLI and custom agent support** — any tool that speaks OpenAI's audio API

### Quick Start

```bash
docker run -d \
  --name voicebox \
  -p 8000:8000 \
  -v voicebox-models:/models \
  -e TTS_ENGINE=piper \
  -e STT_ENGINE=faster-whisper \
  ghcr.io/agjs/voicebox:latest
```

Once running, point any OpenAI-compatible client at `http://localhost:8000/v1`:

```bash
# Transcribe audio
curl http://localhost:8000/v1/audio/transcriptions \
  -H "Content-Type: multipart/form-data" \
  -F file="@recording.wav" \
  -F model="whisper-1"

# Generate speech
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Your voice server is running.",
    "voice": "alloy"
  }'
```

### Open WebUI Integration

This is the killer use case. Open WebUI supports voice input/output, and voicebox provides the backend:

1. Start voicebox: `docker run -d -p 8000:8000 ghcr.io/agjs/voicebox:latest`
2. In Open WebUI, go to Settings → Audio
3. Set TTS Engine to OpenAI, endpoint to `http://voicebox:8000/v1`
4. Set STT Engine to OpenAI, same endpoint

Now you have a fully local ChatGPT-like experience with voice input and spoken responses. Your browser captures audio, voicebox transcribes it, your local LLM generates a response, and voicebox speaks it back. All local, all private.

## Building a Complete Voice Pipeline

Here's how these pieces fit together into a complete self-hosted voice AI stack:

```
┌─────────────────────────────────────────────────────┐
│                  Your Application                    │
│         (Open WebUI / Home Assistant / CLI)          │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
     ┌─────▼──────┐           ┌──────▼──────┐
     │   voicebox  │           │  Direct API │
     │  (unified)  │           │   Access    │
     └──┬───────┬──┘           └──┬───────┬──┘
        │       │                 │       │
   ┌────▼──┐ ┌──▼────┐      ┌────▼──┐ ┌──▼────┐
   │  STT  │ │  TTS  │      │ Piper │ │Kokoro │
   │Whisper│ │Piper/ │      │       │ │       │
   │       │ │Kokoro │      │       │ │       │
   └───────┘ └───────┘      └───────┘ └───────┘
```

### Option A: The Simple Stack (voicebox)

Best for most people. One Docker container, one API, both STT and TTS handled.

```bash
docker run -d --name voicebox -p 8000:8000 \
  -e TTS_ENGINE=piper \
  -e STT_ENGINE=faster-whisper \
  ghcr.io/agjs/voicebox:latest
```

### Option B: The Quality Stack (Kokoro + faster-whisper)

Best for audiobook generation and high-quality voice output.

```bash
# STT
docker run -d --name whisper -p 9000:9000 \
  ghcr.io/agjs/voicebox:latest  # STT-only mode

# TTS
docker run -d --name kokoro -p 8880:8880 \
  ghcr.io/remsky/kokoro-fastapi:latest
```

### Option C: The Edge Stack (Kitten TTS + Piper)

Best for Raspberry Pi or low-resource devices.

```bash
# Kitten for expressive short responses
docker run -d --name kitten -p 8001:8000 \
  ghcr.io/kittenml/kitten-tts:latest

# Piper for reliable assistant voice
docker run -d --name piper -p 10200:10200 \
  rhasspy/wyoming-piper --voice en_US-lessac-medium
```

## Hardware Requirements

| Device | Kitten TTS | Piper | Kokoro | faster-whisper |
|--------|-----------|-------|--------|----------------|
| **Raspberry Pi 4** (4GB) | ✅ Faster than real-time | ✅ Real-time | ⚠️ 0.3x real-time | ⚠️ Slow |
| **Raspberry Pi 5** (8GB) | ✅ Instant | ✅ Real-time | ⚠️ 0.5x real-time | ⚠️ Usable |
| **M1 Mac Mini** (8GB) | ✅ Instant | ✅ Instant | ✅ 2x real-time | ✅ Fast |
| **M4 Mac Mini** (24GB) | ✅ Instant | ✅ Instant | ✅ 3x real-time | ✅ Fast |
| **Intel N100** (16GB) | ✅ Instant | ✅ Instant | ✅ 1.5x real-time | ✅ Fast |
| **Old laptop** (8GB) | ✅ Instant | ✅ Real-time | ⚠️ 0.8x real-time | ⚠️ Usable |

The takeaway: Kitten TTS and Piper run on basically anything. Kokoro wants a somewhat modern CPU. faster-whisper benefits from more RAM and cores but works on a Pi 5.

## Real-World Use Cases

### 1. Local Voice Assistant (Home Assistant)

The most practical use case. Home Assistant's voice pipeline with Piper gives you a fully local Alexa/Google Home replacement:

```yaml
# configuration.yaml
assist_pipeline:
  stt_engine: whisper
  tts_engine: piper
```

"Hey Home Assistant, what's the temperature in the living room?" → spoken answer, no cloud involved.

### 2. AI Chat with Voice (Open WebUI + voicebox)

Run a local LLM (Ollama) with voice input/output:

```bash
# Start the stack
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker run -d --name voicebox -p 8000:8000 ghcr.io/agjs/voicebox:latest
docker run -d --name openwebui -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e AUDIO_TTS_ENGINE=openai \
  -e AUDIO_TTS_ENDPOINT=http://voicebox:8000/v1 \
  ghcr.io/open-webui/open-webui:main
```

Now you're talking to your local AI like it's ChatGPT Advanced Voice Mode — except it's running on your hardware and costs nothing per message.

### 3. Audiobook Generation

Turn your ebook library into audiobooks:

```bash
# Using Kokoro for quality
pip install epub2tts-kokoro
epub2tts ~/books/*.epub --voice af_heart --output ~/audiobooks/

# Batch process a whole directory
for book in ~/books/*.epub; do
  epub2tts "$book" --voice af_heart --output ~/audiobooks/$(basename "$book" .epub)/
done
```

A typical novel (80,000 words) takes about 8-10 hours on an M-series Mac. Start it before bed, wake up to a finished audiobook.

### 4. Podcast Production

Generate narration for podcasts without hiring voice talent:

```bash
# Generate episode narration
python synthesize.py \
  --text "$(cat episode-script.txt)" \
  --voice male_1 \
  --output episode-42-narration.wav

# Mix with intro/outro music using ffmpeg
ffmpeg -i intro.mp3 -i episode-42-narration.wav -i outro.mp3 \
  -filter_complex "[0][1][2]concat=n=3:v=0:a=1" episode-42-final.mp3
```

### 5. Accessibility

Add voice output to any application:

```python
import requests

def speak(text):
    response = requests.post(
        "http://localhost:8000/v1/audio/speech",
        json={"model": "tts-1", "input": text, "voice": "alloy"}
    )
    with open("/tmp/speech.mp3", "wb") as f:
        f.write(response.content)
    # Play with system audio player
    import subprocess
    subprocess.run(["afplay", "/tmp/speech.mp3"])  # macOS
    # subprocess.run(["mpg123", "/tmp/speech.mp3"])  # Linux
```

## Comparison: Self-Hosted vs Cloud TTS

| Factor | Self-Hosted | Cloud (ElevenLabs/OpenAI) |
|--------|-------------|---------------------------|
| **Cost** | Free (hardware only) | $5-500+/month |
| **Privacy** | Everything stays local | Text sent to third party |
| **Latency** | 50-200ms | 200-800ms |
| **Quality** | Good to excellent | Excellent |
| **Voice variety** | 8-50+ voices | 100+ voices |
| **Voice cloning** | Limited (emerging) | Yes (ElevenLabs) |
| **Offline** | ✅ Yes | ❌ No |
| **Rate limits** | None | Per-tier limits |
| **Customization** | Full control | Limited API params |
| **Setup time** | 15-60 minutes | 5 minutes |

For most self-hosted use cases — voice assistants, audiobooks, accessibility — the quality gap has narrowed enough that self-hosted is the clear winner on cost and privacy. Cloud still wins for professional voiceover work and when you need dozens of distinct character voices.

## Troubleshooting

### "Model runs but audio sounds robotic"

- **Piper:** Try a different voice model. The "medium" and "high" quality variants sound significantly better than "low."
- **Kokoro:** Ensure you're using the full 82M model, not a quantized version. The Q8 version is a good balance.
- **Kitten TTS:** The current release is an early checkpoint. Quality will improve with future releases.

### "Generation is too slow"

- **Kokoro on Pi:** It's going to be slow. Use Piper or Kitten TTS instead.
- **faster-whisper:** Use the `tiny` or `base` model instead of `large-v3`. The quality difference is smaller than you'd expect.
- **General:** Check CPU usage with `htop`. Other containers might be competing for resources.

### "voicebox can't find my TTS engine"

- Ensure the TTS engine container is on the same Docker network
- Check the `TTS_ENGINE` environment variable matches your setup
- Verify the engine's API is accessible from the voicebox container: `docker exec voicebox curl http://kokoro:8880/health`

### "Open WebUI voice doesn't work"

- Check that the audio endpoint is reachable from your browser (not just from within Docker)
- For localhost setups, use `http://localhost:8000/v1` not the Docker container name
- Some browsers require HTTPS for microphone access — use a reverse proxy with SSL

## What's Next for Self-Hosted Voice AI

The pace of improvement in open-source TTS is staggering. A few things to watch:

- **Kitten TTS v2** — The team has hinted at multilingual support, voice cloning, and models trained on their full dataset. If the 10%-data checkpoint is this good, the full model could be transformative.
- **Streaming TTS** — Real-time streaming (audio starts playing before the full text is generated) is becoming standard. Kokoro-FastAPI already supports it; expect others to follow.
- **Voice cloning** — Open-source voice cloning is catching up to ElevenLabs. Projects like F5-TTS and CosyVoice are already producing impressive results with short reference samples.
- **On-device STT** — Whisper alternatives like Moonshine and SenseVoice are pushing STT latency down to near-zero for real-time applications.
- **Multimodal voice assistants** — The combination of local LLMs + local TTS + local STT means fully offline voice assistants that understand context, remember conversations, and control your smart home — all without a cloud dependency.

## Conclusion

Self-hosted voice AI has crossed the threshold from "technically possible" to "genuinely good." You can now run a complete TTS+STT stack on a Raspberry Pi that sounds natural, responds quickly, and costs nothing beyond the hardware.

Start with **voicebox** if you want the simplest path — one Docker container gives you both speech-to-text and text-to-speech with an OpenAI-compatible API. Add **Kokoro** if you want the best voice quality for audiobooks or content creation. Use **Kitten TTS** if you're running on edge hardware and need something tiny. **Piper** is your go-to for Home Assistant integration.

The tools are free, the setup is straightforward, and the privacy benefits are real. Your voice data stays yours. Your assistant works offline. And you never get a "usage limit exceeded" email at 2 AM.

That's the self-hosted way.

---

*Have you set up a self-hosted voice AI stack? I'd love to hear about your setup — especially creative use cases I haven't covered. Find me on [GitHub](https://github.com/Bryanmoon19) or drop a comment below.*
