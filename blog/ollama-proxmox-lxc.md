---
layout: post.njk
title: "Run Ollama on Proxmox LXC (Full Setup Guide)"
date: 2026-03-26
description: "Step-by-step guide to running Ollama inside a Proxmox LXC container — GPU passthrough, persistent models, and integrating with Home Assistant and Open WebUI."
tags: ["ollama", "proxmox", "self-hosted", "llm", "homelab", "lxc", "ai"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ollama-proxmox-lxc"
---

Your Proxmox server is probably sitting idle most of the day. It's got RAM you're not using, CPU headroom to spare, and if you have a dGPU in it, a graphics card that's doing absolutely nothing. Running Ollama inside an LXC container is one of the highest-value things you can do with that spare capacity — a private, always-on LLM that responds in under a second, never leaks your prompts to a third party, and costs $0/month beyond existing electricity.

This guide walks through the full setup: LXC creation, Ollama install, GPU passthrough if you have it, Open WebUI for a ChatGPT-style interface, and how to wire it into Home Assistant for voice-activated local AI.

## Why LXC Instead of a VM

**LXC shares the host kernel for near-native GPU performance and near-zero overhead vs a full VM.**

You could run Ollama in a full VM, but LXC containers on Proxmox share the host kernel. That gives you:

- **Lower overhead** — no hypervisor CPU/RAM tax per container
- **Near-native GPU performance** — device passthrough is direct, not emulated
- **Faster startup** — an LXC container starts in under a second vs 15–30s for a VM

The tradeoff: LXC containers require `nesting=1` for Docker (if you want it), and root in an LXC container has more host access than in a VM. For a home network, this is fine. For production multi-tenant setups, use a VM.

## Prerequisites

**You need Proxmox 8.x, an Ubuntu LXC template, and optionally an NVIDIA or AMD GPU.**

- Proxmox 8.x (7.x works with minor differences)
- An LXC-compatible base template (Ubuntu 22.04 or 24.04 recommended)
- Optional: NVIDIA or AMD GPU in your Proxmox host for hardware acceleration

## Step 1: Create the LXC Container

**Create a container with 4+ cores, 16GB RAM, and 40GB disk — models are large and need room.**

In the Proxmox web UI:

1. **Datacenter → Storage** — make sure you have a CT template downloaded. If not, go to your storage → CT Templates → Templates and download `ubuntu-24.04-standard`.

2. **Create CT** with these settings:
   - **Hostname:** `ollama` (or whatever)
   - **Template:** ubuntu-24.04-standard
   - **Disk:** 40GB minimum (models are large — Llama 3.1 70B is ~40GB alone)
   - **CPU:** 4+ cores
   - **RAM:** 8GB minimum, 16GB recommended
   - **Network:** Bridge to your main VLAN

3. In **Options → Features**, enable:
   - `nesting=1` (required if you want Docker inside the container)
   - `keyctl=1` (needed for some container workloads)

Or via CLI on the Proxmox host:

```bash
pct create 110 local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \
  --hostname ollama \
  --cores 4 \
  --memory 16384 \
  --rootfs local-lvm:40 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1,keyctl=1 \
  --unprivileged 1 \
  --start 1
```

## Step 2: Install Ollama

**One curl command installs Ollama as a systemd service — it's running in under 60 seconds.**

Start the container and SSH in (or use the Proxmox shell):

```bash
pct exec 110 -- bash
```

Once inside:

```bash
# Update and install curl
apt update && apt install -y curl

# Install Ollama (official installer)
curl -fsSL https://ollama.com/install.sh | sh

# Verify it's running
ollama --version
systemctl status ollama
```

Ollama installs as a systemd service and starts automatically. The service listens on `127.0.0.1:11434` by default.

## Step 3: Pull Your First Model

**`ollama pull llama3.2` gets you a capable model in minutes; test it immediately with `ollama run`.**

```bash
# Small, fast — great for testing and Home Assistant
ollama pull llama3.2

# Better quality, needs 8GB RAM
ollama pull llama3.1:8b

# Coding focused
ollama pull qwen2.5-coder:7b

# Embed vector search (for RAG later)
ollama pull nomic-embed-text
```

Test it immediately:

```bash
ollama run llama3.2 "What's the capital of France? Answer in one word."
```

You should get a response in 1–3 seconds on a modern CPU. With a GPU, it's nearly instant.

## Step 4: Make Ollama Accessible on Your Network

**Set `OLLAMA_HOST=0.0.0.0` via a systemd override to expose Ollama to your local network.**

By default, Ollama only binds to `127.0.0.1`. To access it from other machines (Open WebUI, Home Assistant, your laptop), you need to change the bind address.

```bash
# Edit the systemd service override
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
EOF

systemctl daemon-reload
systemctl restart ollama
```

Now Ollama is accessible at `http://<container-ip>:11434` from any machine on your network.

Test from another machine:

```bash
curl http://192.168.7.XXX:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"Hello!","stream":false}'
```

## Step 5: Add Open WebUI (Optional but Recommended)

**One Docker command gives you a full ChatGPT-style UI with multi-user and conversation history.**

Open WebUI gives you a full ChatGPT-style interface connected to your local Ollama. It also handles multi-user sessions, model management, and conversation history.

Install with Docker (requires `nesting=1` on the LXC):

```bash
# Install Docker inside the container
curl -fsSL https://get.docker.com | sh

# Run Open WebUI connected to Ollama
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

Open WebUI will be at `http://<container-ip>:3000`. First visit creates an admin account.

If you want Open WebUI and Ollama on separate ports and prefer not to use Docker inside LXC, you can run Open WebUI as a separate LXC and point it at the Ollama container's IP.

## Step 6: NVIDIA GPU Passthrough (If You Have a GPU)

**A mid-range gaming GPU gives 5–10x inference speedup; requires a privileged LXC and device passthrough.**

This is where it gets significantly faster. LLM inference is memory-bandwidth bound — a mid-range gaming GPU from 5 years ago will outrun a modern CPU by 5–10x on most models.

> **Note:** GPU passthrough to LXC containers requires a **privileged** container. Redo the container setup with `--unprivileged 0` if you want GPU access.

On the **Proxmox host**, identify your GPU:

```bash
lspci | grep -i nvidia
# Example: 01:00.0 VGA compatible controller: NVIDIA Corporation GA106 [GeForce RTX 3060]
```

Add device passthrough to your LXC config (`/etc/pve/lxc/110.conf`):

```ini
lxc.cgroup2.devices.allow: c 195:* rwm
lxc.cgroup2.devices.allow: c 235:* rwm
lxc.mount.entry: /dev/nvidia0 dev/nvidia0 none bind,optional,create=file
lxc.mount.entry: /dev/nvidiactl dev/nvidiactl none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm dev/nvidia-uvm none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-uvm-tools none bind,optional,create=file
```

**Inside the container**, install the NVIDIA driver (must match the host version):

```bash
# Check the host driver version first
ssh root@proxmox-host "nvidia-smi | grep 'Driver Version'"

# Install matching version inside container (example: 535.x)
apt install -y nvidia-driver-535 nvidia-utils-535

# Verify GPU is visible
nvidia-smi
```

Restart Ollama and it will automatically use the GPU:

```bash
systemctl restart ollama
ollama run llama3.1:8b "What's 2+2?" 
# Should show GPU utilization in nvidia-smi
```

### AMD GPU Passthrough

AMD is actually easier on Linux — use ROCm:

Inside the container, install ROCm:

```bash
apt install -y rocm-hip-libraries
```

Add device passthrough to your LXC config (`/etc/pve/lxc/110.conf`):

```ini
lxc.mount.entry: /dev/dri dev/dri none bind,optional,create=dir
lxc.mount.entry: /dev/kfd dev/kfd none bind,optional,create=file
```

Then install Ollama (it auto-detects ROCm):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 7: Wire Into Home Assistant

**Point HA's Ollama integration at your container IP for a fully local, private voice AI assistant.**

This is where it gets genuinely useful for a smart home. You can use Ollama as the AI backend for Home Assistant's conversation agent — completely local, no monthly subscription, no API keys.

### Via the Ollama Integration (HA 2024.3+)

In Home Assistant:

1. **Settings → Integrations → Add Integration → Ollama**
2. Enter your Ollama URL: `http://192.168.7.XXX:11434`
3. Select your preferred model (llama3.2 works well for HA)
4. Set as your default conversation agent

Now your voice assistant uses local AI. "Hey Google, talk to Home Assistant" → your Proxmox server handles the NLU, nothing leaves your network.

### For Automation — Using the REST API

```yaml
# In an automation action
action: rest_command.ask_ollama
```

```yaml
# configuration.yaml
rest_command:
  ask_ollama:
    url: "http://192.168.7.XXX:11434/api/generate"
    method: POST
    content_type: "application/json"
    payload: '{"model":"llama3.2","prompt":"{{ prompt }}","stream":false}'
```

You can now build automations that use an LLM to interpret sensor data, draft notifications, or make context-aware decisions — no cloud required.

## Model Selection Guide

**Use llama3.2 for general/HA, qwen2.5-coder for code, and nomic-embed-text for RAG pipelines.**

Different tasks need different models. Here's a quick reference for home/lab use:

| Use Case | Recommended Model | Size | Notes |
|----------|------------------|------|-------|
| General chat / HA assistant | `llama3.2` | 2.0GB | Fast, good reasoning |
| Home Assistant (low RAM) | `llama3.2:1b` | 1.3GB | Tiny, still useful |
| Code generation | `qwen2.5-coder:7b` | 4.7GB | Best free coding model |
| Long context (big docs) | `llama3.1:8b` | 4.7GB | 128k context window |
| Privacy-first chat | `mistral:7b` | 4.1GB | Clean Apache license |
| Vector embeddings | `nomic-embed-text` | 274MB | For RAG pipelines |
| Vision tasks | `llava:7b` | 4.5GB | Describe images locally |

Disk tip: models are stored in `/root/.ollama/models/` by default. If your LXC root is on limited-size storage, symlink or bind-mount to a larger volume:

```bash
# If /mnt/nas is mounted inside the container
mkdir -p /mnt/nas/ollama-models
ln -s /mnt/nas/ollama-models /root/.ollama/models
```

## Keeping Ollama Updated

**Re-run the install script to update in-place — it handles everything without losing your models.**

Ollama updates frequently. The Proxmox community script handles this automatically if you used it to create the container, but for manual setups:

```bash
# Re-run the installer — it updates in-place
curl -fsSL https://ollama.com/install.sh | sh
systemctl restart ollama
```

Or pin to a specific version by downloading the binary directly from [github.com/ollama/ollama/releases](https://github.com/ollama/ollama/releases).

## Recommended Hardware

<div class="affiliate-disclosure">Some links below are affiliate links — I earn a small commission at no extra cost to you. I only recommend hardware I've personally used or researched for homelab use.</div>

If you're building or upgrading for local LLM inference, here's what I'd recommend:

**For CPU-only (great starting point):**
- [Intel N100 Mini PC](https://www.amazon.com/dp/B0CWJ3X2JH?tag=devhandbook26-20) — Fanless, low power, runs llama3.2 comfortably. Perfect dedicated Ollama box for ~$150.
- [32GB DDR5 SO-DIMM Kit](https://www.amazon.com/dp/B0C9V3HD87?tag=devhandbook26-20) — More RAM = larger models. 32GB lets you run 13B parameter models.

**For GPU acceleration (serious inference):**
- [NVIDIA RTX 3060 12GB](https://www.amazon.com/dp/B08WR34RFY?tag=devhandbook26-20) — The sweet spot for home LLM use. 12GB VRAM handles most 7-13B models fully offloaded. Often found used for ~$200.
- [NVIDIA RTX 4060 Ti 16GB](https://www.amazon.com/dp/B0C9KLS6BN?tag=devhandbook26-20) — If you want headroom for 30B+ models and future-proofing.

**Storage (models are large):**
- [Samsung 870 EVO 1TB SSD](https://www.amazon.com/dp/B08QBJ2YMG?tag=devhandbook26-20) — Fast SATA SSD for model storage. Ollama reads models sequentially, so even SATA is fine.
- [Samsung 990 Pro 2TB NVMe](https://www.amazon.com/dp/B0BHJJ9Y77?tag=devhandbook26-20) — For Proxmox host storage if you're running multiple LXC workloads.

**Full Proxmox server (if starting fresh):**
- [Beelink SER7 (AMD 7840HS)](https://www.amazon.com/dp/B0CR1JNMXL?tag=devhandbook26-20) — Powerful mini PC with integrated Radeon 780M. Runs Proxmox beautifully, handles 7B models on the iGPU via ROCm.

## What's Next

**Open WebUI, AnythingLLM for RAG, and Whisper+Piper for a fully local voice assistant are the natural next steps.**

Once Ollama is running, the usual next steps are:

- **[Open WebUI](https://openwebui.com)** — Full ChatGPT-style UI with multi-user support
- **[AnythingLLM](https://github.com/Mintplex-Labs/anything-llm)** — RAG pipeline for chatting with your documents
- **[LocalAI](https://localai.io)** — Drop-in OpenAI-compatible API, useful for apps that hardcode OpenAI endpoints
- **Home Assistant AI Voice** — Combine Whisper (local STT) + Ollama (LLM) + Piper (local TTS) for a fully local voice assistant

The Ollama ecosystem is expanding fast. A Proxmox LXC is the right foundation: isolated, low-overhead, easy to snapshot before experiments, and trivial to clone if you want to test multiple model setups.

---

*Questions or improvements? The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
