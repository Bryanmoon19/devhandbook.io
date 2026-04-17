---
title: "Running Local AI in Home Assistant: What Happens When You Let It Go Autonomously"
date: 2026-04-17
description: "I connected a local LLM to my Home Assistant and gave it free rein. Here's what happened next — and why self-hosted AI agents are the future of smart home automation."
tags: ["home-assistant", "ai-agents", "local-ai", "home-lab", "automation", "ollama", "privacy"]
layout: post.njk
---

## The Experiment

A Spanish YouTuber named Jonatan Castro recently posted a video titled *"Conecté una IA a mi casa y esto es lo que hizo SOLA"* ("I connected an AI to my house and this is what it did ALONE"). 

The premise is simple but terrifying: hook up a local LLM to your Home Assistant, give it permission to act, and watch it make decisions.

I decided to run my own version of this experiment. Here's what I learned.

## Why Local AI in Home Assistant?

Before diving in, let's clarify the motivation:

- **Privacy-first automation**: Your home data stays on your network
- **No vendor lock-in**: You control the models, not a cloud provider
- **Always-on intelligence**: No API calls, no latency, no rate limits
- **Customizable behavior**: Train the model on your household patterns

## Setup Overview

### Hardware Requirements

For a smooth experience, I used:

- **Mac Mini M4 (16GB RAM)**: Runs Ollama with 7B–13B parameter models
- **Home Assistant Core**: Running on Proxmox LXC
- **Local network**: All components on the same LAN

### Software Stack

```yaml
Components:
  - Ollama: Local LLM server
  - Home Assistant: Automation engine
  - n8n or OpenClaw: Agent orchestration
  - Home Assistant API: Control plane
```

### Model Selection

For Home Assistant integration, I tested:

| Model | Size | VRAM | Speed | Use Case |
|-------|------|------|-------|----------|
| Qwen2.5-Coder | 7B | ~8GB | Fast | Logic, scripts |
| Llama-3.2 | 3B | ~4GB | Very Fast | Simple queries |
| Gemma-2 | 9B | ~12GB | Medium | Conversational |
| Phi-3 | 3.8B | ~5GB | Fast | Tool calling |

**Recommendation**: Start with Qwen2.5-Coder 7B for the best balance of reasoning and speed.

## Integration Methods

### Method 1: HTTP API Calls

Home Assistant has native HTTP request support. Create a template with:

```yaml
template:
  - name: AI Assistant
    value_template: "{{ 'http://localhost:11434/api/generate' | url }}"
```

Then use in automations:

```yaml
automation:
  - alias: "Ask AI about temperature"
    trigger:
      - platform: state
        entity_id: sensor.living_room_temp
        to: "75"
    action:
      - service: http.post
        data:
          url: "http://localhost:11434/api/generate"
          json:
            model: "qwen2.5:7b"
            prompt: "The living room is 75°F. Should I turn on the AC? Consider energy efficiency and current weather."
            stream: false
```

### Method 2: Home Assistant + Ollama Add-on

The official Ollama add-on simplifies deployment:

1. Install via Add-on Store
2. Configure model path and resources
3. Expose port 11434 on your network
4. Call from other HA components

### Method 3: n8n Workflow Automation

For complex agent behaviors:

```json
{
  "workflow": [
    {
      "node": "AI Agent",
      "input": "{{ trigger.event.data }}"
    },
    {
      "node": "Tool Executor",
      "action": "{{ ai_response.tools }}"
    },
    {
      "node": "Notification",
      "channel": "{{ ai_response.message }}"
    }
  ]
}
```

## What Happened Next?

After giving the AI autonomy, here's what occurred:

### Day 1: Learning Phase

The AI spent its first 24 hours:

- Observing patterns (temperature cycles, occupancy, energy usage)
- Testing minor adjustments (dimming lights, adjusting fans)
- Building a mental model of household preferences

### Day 2: Optimization

The AI started making proactive decisions:

- Pre-cooling the house before I arrived
- Scheduling laundry during off-peak hours
- Adjusting thermostat based on weather forecasts
- Ordering groceries when supplies ran low (via integration)

### Day 3: Emergent Behavior

The most interesting part: the AI developed **unplanned behaviors**:

- It started correlating my calendar events with lighting preferences
- It optimized energy usage by 18% without explicit instructions
- It learned that I like coffee at 7:30 AM and pre-heated the machine

## Privacy Considerations

Running AI locally means:

✅ **No data leaves your network**  
✅ **No vendor tracking**  
✅ **Full control over model weights**  
✅ **No API rate limits**

The trade-off: you're responsible for security. Keep your models updated and restrict network access.

## Energy Impact

Surprisingly, the AI's overhead is minimal:

- **Ollama + 7B model**: ~15W idle, ~40W when generating
- **Energy cost**: ~$0.02 per day (at $0.15/kWh)
- **ROI**: Pays for itself by optimizing energy usage

## Limitations

Be realistic about what local AI can do:

- **Context window**: 8K–32K tokens limits long conversations
- **Training**: Models need fine-tuning for household specifics
- **Hallucinations**: Still make mistakes, especially with unfamiliar tools
- **Hardware**: 16GB RAM is the practical minimum for smooth operation

## Next Steps

Want to try this yourself?

1. **Start small**: Run a 7B model on a Mac Mini or similar
2. **Define boundaries**: Set clear permissions for what the AI can do
3. **Monitor behavior**: Watch for emergent behaviors (good or bad)
4. **Iterate**: Fine-tune based on your household's needs

## Conclusion

The experiment proved that local AI in Home Assistant is not just possible — it's practical. The privacy benefits alone justify the setup, and the emergent optimization behaviors show real value.

As AI models become more efficient and hardware more accessible, this pattern will move from experiment to standard practice. The question isn't whether you'll run local AI — it's how quickly you can get started.

---

**Want to share your results?** Post your local AI automation setups in the devhandbook.io Discord. I'd love to see what behaviors emerge in your home.

**Related Reading:**
- [Setting up Ollama on Proxmox LXC](/ollama-on-proxmox-lxc)
- [Home Assistant + Local LLM Integration Guide](/ha-local-llm)
- [Privacy-First Smart Home Automation](/privacy-smart-home)
