---
layout: post.njk
title: "Self-Hosted Meeting Notes: Kill Your Otter.ai and Granola Bill With a Local Transcription Stack"
date: 2026-11-23
description: "Otter.ai, Granola, and Fireflies all send your meeting audio to a third party — and charge you for it. Yogurt, Meetily, faster-whisper, and WhisperX give you the same transcriptions and speaker labels running entirely on your own hardware. Here's the turnkey apps vs. the DIY pipeline, with exact commands for both."
tags: ["self-hosted", "transcription", "whisper", "faster-whisper", "whisperx", "meeting-notes", "privacy", "local-ai", "speech-to-text", "diarization", "granola", "otter", "homelab", "yogurt", "meetily", "pyannote", "mac-mini"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-23-self-hosted-meeting-notes-local-transcription/"
affiliate: false
cta: true
---

# Self-Hosted Meeting Notes: Kill Your Otter.ai and Granola Bill With a Local Transcription Stack

Every meeting you run through Otter.ai, Granola, Fireflies, or Read.ai ships your raw audio to a third-party cloud — along with whatever gets said in a closed-door call about pricing, hiring, or a product that hasn't launched. Then you pay a subscription for the privilege of the leak.

It doesn't have to be that way. A complete **private meeting-notes stack** — transcription, speaker labels, and a searchable notes UI — now runs entirely on hardware you already own. Two open-source apps (Yogurt and Meetily) give you a turnkey experience with zero config, and if you'd rather build the pipeline yourself, `faster-whisper` + `WhisperX` + `pyannote` will transcribe and diarize hours of audio on a Mac mini or homelab GPU.

Here's the honest map of both paths — what each tool actually does, what it costs in compute, and exactly how to wire it up.

## The two ways to do it, in 30 seconds

| Path | What you get | Best for | Effort |
|------|-------------|----------|--------|
| **Turnkey app** — Yogurt or Meetily | Install, grant mic access, done. Live transcription, summaries, speaker names, search. | Anyone who just wants their meetings private | 5 minutes |
| **DIY pipeline** — faster-whisper / WhisperX + pyannote | Full control, batch jobs, scriptable, GPU-accelerated, no GUI | Homelabbers who want a building block, not a product | 1–2 hours |

The apps and the pipeline are **not competitors** — they share the same underlying models (Whisper for transcription, a diarization model for "who said what"). The apps just package them behind a polished UI. Understanding the pipeline is what lets you understand the apps, so we'll start there and finish with the apps.

---

## Part 1 — The DIY pipeline: transcribe + diarize on your own box

The building blocks, in order of how much of the stack they cover:

### faster-whisper — the transcription workhorse

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) (26,954★, MIT) is a reimplementation of OpenAI's Whisper on the [CTranslate2](https://github.com/OpenNMT/CTranslate2) inference engine. The headline number matters: **up to 4× faster than the original `openai/whisper` at the same accuracy, using less memory.**

Its other big trick is **8-bit quantization** — you can run the `large-v2` model in ~2.9 GB of VRAM instead of ~4.7 GB, at 59 seconds for a 13-minute clip. That's the difference between "fits on a 6 GB card" and "doesn't."

```sh
pip install faster-whisper

python -c "
from faster_whisper import WhisperModel
model = WhisperModel('large-v2', device='cuda', compute_type='int8_float16')
segments, info = model.transcribe('meeting.wav', beam_size=5)
for s in segments:
    print(f'[{s.start:.1f}s → {s.end:.1f}s] {s.text}')
"
```

**Honest tradeoff:** faster-whisper gives you *timestamps and text*, but it does **not** tell you *who* is speaking. For a one-on-one call that's fine. For a five-person meeting, you need the next two tools.

### WhisperX — word-level timestamps + speaker labels

[WhisperX](https://github.com/m-bain/whisperX) (25,607★, BSD-2-Clause) wraps faster-whisper and adds two things the raw model can't do:

1. **Word-level timestamps** (via forced alignment, so transcripts align to the audio precisely)
2. **Speaker diarization** (via pyannote — it segments the audio into "speaker A / speaker B / speaker C")

This is the piece that turns a wall of text into *meeting notes you can actually follow*. One call produces a transcript labeled `SPEAKER_00`, `SPEAKER_01`, and so on.

```sh
pip install whisperx

whisperx meeting.wav --model large-v2 --device cuda \
  --diarize --hf_token YOUR_HF_TOKEN
```

**The one gotcha worth knowing up front:** diarization uses `pyannote/speaker-diarization-3.1`, which is [gated on Hugging Face](https://huggingface.co/pyannote/speaker-diarization-3.1) (`gated: auto`). You accept the MIT license with one click on the model card, grab a free read token, and pass it as `--hf_token`. It's a 30-second step, but if you skip it the diarization silently won't run — the exact failure mode people hit and then post "diarization does nothing" about.

### pyannote-audio — the diarization engine itself

[pyannote-audio](https://github.com/pyannote/pyannote-audio) (10,834★, MIT) is the underlying "who spoke when" engine. You rarely call it directly once WhisperX wires it in, but it's worth knowing it's there — and that `speaker-diarization-3.1` has seen ~6 million downloads, so you're building on a battle-tested model, not a toy.

### whisper.cpp — when you want zero Python

If you'd rather avoid a Python environment entirely, [whisper.cpp](https://github.com/ggml-org/whisper.cpp) (55,440★, MIT) is a single C++ binary with no dependencies. It runs on CPU, Apple Silicon, and CUDA, and it's the same engine Yogurt uses under the hood. Slower to get started with than `pip install`, but it's the right call for embedded devices or a clean container.

```sh
git clone https://github.com/ggml-org/whisper.cpp
cd whisper.cpp && make
./main -m models/ggml-large-v3.bin -f meeting.wav
```

---

## Part 2 — The turnkey apps: install and be done

### Yogurt — the Granola alternative that stays on your computer

[Yogurt](https://github.com/FrigadeHQ/yogurt) (2,999★, MIT, TypeScript) is the newest and most polished of the bunch — it launched November 10, 2026 and is explicitly positioned as a free, open-source alternative to Granola, Otter, and Fireflies. The pitch: *"No meeting bot. Private AI meeting notes that stay on your computer."*

What it actually does, straight from the project:

- **Live transcripts** — records mic + call audio and transcribes as you talk
- **Meeting summaries** — writes up the conversation and any notes you add
- **Speaker names** — pulls names from Zoom, Teams, and Meet
- **99-language transcription**, including mid-meeting language switching
- **Answers with sources** — asks questions across past meetings and links to the source line
- **Local MCP server** — lets other apps on your machine read notes, transcripts, and saved audio

The stack is honest: **whisper.cpp** (plus Apple's SpeechAnalyzer on supported Macs) for transcription, and a local open-weight model via **llama.cpp** for summarization. Your audio and notes never leave the machine — it goes online only to download models and check for updates.

On a Mac it's one line:

```sh
brew install --cask frigadehq/yogurt/yogurt
```

Native builds also exist for Windows and Linux. This is the one I'd hand a non-technical teammate — it's the closest thing to a drop-in Otter replacement that doesn't phone home.

### Meetily — the enterprise-flavored alternative

[Meetily](https://github.com/Zackriya-Solutions/meetily) (32,977★, MIT) is the older, heavier hitter. It's a privacy-first meeting assistant that captures, transcribes, and summarizes **entirely on your infrastructure**, using on-device Whisper/Parakeet transcription plus speaker diarization. It's aimed at enterprises that need meeting intelligence without sending audio to a third party — and its 33k stars suggest that market is real.

The tradeoff vs. Yogurt: Meetily is more "platform" (pre-release binaries, an enterprise subscription upsell, macOS/Windows focus), where Yogurt is leaner and Mac/Linux-native. Both are MIT, both keep audio local.

---

## Which one should you pick?

A decision tree that respects the never-lie rule:

- **You want private notes tomorrow, no tinkering** → **Yogurt**. One `brew install`, local by default, free. The clearest Granola/Otter replacement for a solo dev or a Mac-first team.
- **You need enterprise features / are already on Windows** → **Meetily**. On-device diarization out of the box, a real vendor behind it.
- **You want a scriptable building block** (batch-transcribe a podcast archive, feed transcripts into your own notes pipeline) → **faster-whisper + WhisperX**. You own the output, you control the GPU, and it composes with everything else.
- **You're on a Pi or an embedded device** → **whisper.cpp**. One binary, no Python, runs on a potato.

The one thing all four have in common: **none of them send your audio to a third party.** That's the point, and it's why this category is growing fast right now — privacy is the feature, not a checkbox.

---

## What it actually costs to run locally

Rough real-world numbers, so you can plan VRAM before you download a 3 GB model:

| Model | Precision | VRAM (13-min clip, faster-whisper benchmark) |
|-------|-----------|---------------------------------------------|
| `large-v2` | fp16 | ~4.5 GB |
| `large-v2` | int8 | ~2.9 GB |
| `large-v3` | int8 | ~3.3 GB (approx.) |
| `small` / `medium` | int8 | well under 2 GB — fits a 6 GB card easily |

If you've got a 6 GB card, `int8` quantization is what makes `large-v2` viable. If you're on a Mac mini with unified memory, the same models run fine on the CPU/Metal path — slower per minute, but fine for a couple of hour-long calls a day. Measure your own before/after; these are benchmarks, not promises.

(For a deeper look at fitting models to your card, the [GPU VRAM calculator](/gpu-vram-calculator/) and the [quantization guide](/blog/2026-08-21-shrink-local-llm-quantization/) cover the sizing math.)

---

## The honest limitations

Nothing here is magic, and pretending otherwise would be doing you a disservice:

- **Diarization isn't perfect.** pyannote's `speaker-diarization-3.1` is good, but it can still split one person into two or merge two speakers when they talk over each other. For clean, turn-taking meetings it's solid; for a raucous brainstorming call, expect a few mislabels.
- **"Local" means local compute, not zero cloud.** Yogurt and Meetily download models on first run (and check for updates). The *audio* stays local; the *model weights* come from the internet once. That's the right tradeoff, but it's not "air-gapped."
- **Accuracy is model-size-bound.** `large-v2`/`large-v3` are dramatically better than `tiny`/`base` on accents, jargon, and overlapping speech. If you run the smallest model to save VRAM, you pay for it in mistakes. For meetings, spend the VRAM.
- **This is transcription + diarization, not an AI assistant.** Yogurt's local summarizer is a real, useful bonus — but it's a local open-weight model, not a frontier cloud model. Set expectations accordingly.

---

## The bottom line

A year ago, "private meeting transcription" meant running raw `whisper` on the CLI and squinting at unlabeled text. Today, Yogurt and Meetily give you the full Otter/Granola experience with your audio never leaving your machine, and faster-whisper + WhisperX give you a GPU-accelerated pipeline you can script into anything.

If you're still paying $16–30/month for a cloud meeting bot, this is the month to stop. Your audio is your business — literally. Keep it on your own hardware.

---

*This post ties into the rest of the self-hosted voice stack: for text-to-speech and speech-to-text beyond meetings, see the [self-hosted voice AI guide](/blog/2026-08-13-self-hosted-voice-ai-guide/).*
