---
layout: post.njk
title: "Give Home Assistant a Brain: Running Local AI Agents With Ollama"
date: 2026-04-12
description: "Connect local LLMs to Home Assistant for private, intelligent smart home control. Full setup for Ollama conversation agents, voice commands, and AI-powered automations."
tags: ["home-assistant", "ollama", "local-llm", "ai", "smart-home", "automation", "privacy", "self-hosted"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/home-assistant-local-ai-agents"
---

Home Assistant can already automate your lights, thermostat, and media players. But what if it could *reason* about your home? What if you could say "I'm leaving for the weekend" and your assistant decided which devices to turn off, which cameras to arm, and what temperature to set — without sending a single byte to OpenAI?

That's exactly what local AI agents in Home Assistant enable. Using Ollama and the built-in **Conversation** integrations, you can run a local large language model that controls your smart home, answers questions about your devices, and even writes automations for you. This guide covers the full setup from zero to talking house.

## What "Local AI Agent" Means in Home Assistant

Home Assistant's conversation engine lets you define an **LLM conversation agent** — essentially replacing Alexa, Siri, or Google Assistant with a model running on your own hardware. The model receives:
- Your voice or text prompt
- A list of exposed entities (lights, switches, climate, etc.)
- The current state of those entities
- Pre-written prompts that tell it how to behave

The model then decides what to do and returns Home Assistant service calls. All of this happens on your network.

**Requirements:**
- Home Assistant 2025.4 or newer
- An Ollama server (Docker, bare metal, or another machine on your LAN)
- A local LLM that supports **function calling / tools** (required for device control)

## Step 1: Set Up Ollama

If you don't have Ollama running yet, the fastest path is Docker:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

For CPU-only setups, remove the `deploy` section. For Apple Silicon, run Ollama natively (`brew install ollama`) rather than in Docker for best performance.

Pull a tool-capable model. As of early 2026, these work reliably with Home Assistant:

```bash
# Small, fast, surprisingly capable
ollama pull qwen2.5:3b

# Best balance of speed and smarts for home control
ollama pull qwen2.5:7b

# If you have the VRAM/RAM for it
ollama pull qwen2.5:14b

# Experimental but impressive
ollama pull llama3.2:3b
```

Test it:

```bash
curl http://localhost:11434/api/tags
```

## Step 2: Add the Ollama Integration to Home Assistant

Home Assistant has a built-in **Ollama** integration. Go to:

**Settings > Devices > services > Add Integration > Ollama**

Enter your Ollama host:
- If Ollama runs on the same machine as HA: `http://host.docker.internal:11434` (for HA Container/Supervised) or `http://localhost:11434` (for HA OS with the Ollama add-on)
- If Ollama runs elsewhere: `http://192.168.1.100:11434`

The integration will discover your pulled models. Select the one you want to use.

**Important:** Only models that support tools can actually control devices. The integration will warn you if the model doesn't support function calling. Stick to Qwen 2.5 or Llama 3.2+ for the best experience.

## Step 3: Set Ollama As Your Conversation Agent

Go to **Settings > Voice assistants > (Your Assistant)** and change the **Conversation agent** from the default (Home Assistant) to your new Ollama model.

Now when you type or speak to Home Assistant, your local LLM handles the request.

### Expose Entities Intentionally

Local LLMs get confused if you expose too much. The official recommendation is **fewer than 25 entities** for smaller models. For Qwen 2.5 7B or 14B, you can push to 50–100, but start small.

Go to **Settings > Voice assistants > Expose** and only expose entities the assistant actually needs to control:
- Lights in commonly used rooms
- Thermostat / climate
- Media players
- Locks and door sensors (if you trust it)

Avoid exposing: every individual smart plug, obscure sensors, or administrative switches.

## Step 4: Customize the System Prompt

The system prompt tells the LLM who it is and what it's allowed to do. You can edit this per conversation agent.

A good starting prompt:

```
You are a helpful smart home assistant running entirely locally. You control devices in Bryan's home. Be concise. When asked to control devices, call the appropriate Home Assistant services. If a request is unclear, ask for clarification. Never make up device names — only use entities you have been provided.
```

Add rules like:
- "Never unlock doors without explicit confirmation"
- "Turn off all lights when the user says 'goodnight'"
- "Set the thermostat to 68°F when the user says 'I'm cold'"

These aren't hardcoded automations — the LLM interprets them. It's both powerful and slightly unpredictable, which is why you should keep your prompt explicit.

## Step 5: Test Voice Control

If you have a voice satellite (Home Assistant Voice PE, an ATOM Echo, or any Wyoming satellite), your local LLM now handles voice commands end-to-end.

Try these:
- "Turn off the living room lights"
- "Set the temperature to 72"
- "Is the front door locked?"
- "Goodnight" (with a custom prompt that turns off lights, arms alarms, etc.)

### What Works Today

- Direct device control via natural language
- Reasoning about device states ("Is anything still on downstairs?")
- Simple multi-step requests ("Turn off the kitchen and dim the bedroom to 20%")

### What Still Needs Work

- Complex multi-room context can confuse small models
- LLMs occasionally hallucinate entity names
- Response latency on CPU-only setups is 2–5 seconds — usable, but not instant

## Step 6: Go Beyond Voice — AI Tasks and MCP

Home Assistant 2025 introduced **AI Tasks** — pre-defined jobs your local LLM can run on a schedule or trigger. For example:
- Summarize the day's energy usage every evening
- Review security camera events and flag anomalies
- Suggest automations based on your usage patterns

Configure AI Tasks under **Settings > System > General > AI Task preferences**.

**MCP (Model Context Protocol)** is the newer standard that lets Home Assistant expose tools to any compatible model, not just built-in integrations. This means your local Ollama model can eventually interact with external sources — calendars, email, weather APIs — without writing custom YAML.

## Performance Tips

| Hardware | Recommended Model | Expected Latency |
|----------|-------------------|------------------|
| Raspberry Pi 5 | `qwen2.5:3b` | 3–6s |
| Intel N100 / old laptop | `qwen2.5:7b` | 2–4s |
| Mac mini M4 (16GB+) | `qwen2.5:14b` | 1–2s |
| RTX 3060 12GB | `qwen2.5:14b` | <1s |

If latency matters, run Ollama on your fastest machine and point Home Assistant at it over the network. A Mac mini M4 running Ollama locally is one of the best smart home AI setups you can build in 2026.

## Privacy and Control

The entire point of this setup is that **nothing leaves your house**. No cloud AI provider sees:
- Your device names
- Your home's layout
- Your occupancy patterns
- Your voice recordings

Compare that to Alexa or Google Assistant, where every request is logged, analyzed, and occasionally reviewed by humans. Local AI isn't just a nerdy flex — it's a meaningful privacy upgrade.

## Troubleshooting

**"The model says it can't control devices"**
→ You picked a model that doesn't support tools. Pull `qwen2.5:7b` or newer Llama.

**"Responses are too slow"**
→ Your hardware is underpowered for the model size. Drop to 3B or add a GPU.

**"It sometimes controls the wrong light"**
→ Reduce exposed entities and give devices clearer, unique names.

**"Ollama integration can't connect"**
→ Check firewall rules on port 11434. If Ollama is in Docker, use the container's IP or host network mode.

## Bottom Line

Local AI agents turn Home Assistant from a rigid rule engine into something that actually understands context. It's not perfect — small models make mistakes, and voice latency on weak hardware is real — but the tradeoff is worth it. You get a privacy-first smart home assistant that follows your rules, runs on your hardware, and never phones home.

If you've already got Ollama running for coding or chat, extending it to Home Assistant takes under ten minutes. Your house has never been smarter.

---

*Inspired by the growing community around [local AI in the smart home](https://www.youtube.com/watch?v=siD6cxvEUOE) and Home Assistant's official [AI-powered smart home vision](https://www.home-assistant.io/blog/2025/09/11/ai-in-home-assistant/).*
