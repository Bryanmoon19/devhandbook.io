---
layout: post.njk
title: "AI Agent Sandboxes: Why Your Homelab Needs One (and How to Set It Up)"
date: 2026-07-29
description: "AI coding agents can read your files, run shell commands, and access your network. Here's how to sandbox them safely on your homelab — with step-by-step setup guides for Dormice, Firecracker, and Docker isolation."
tags: ["ai-agent", "sandbox", "security", "self-hosted", "homelab", "docker", "proxmox", "firecracker", "dormice", "claude-code", "openclaw"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ai-agent-sandboxes-homelab-2026"
---

# AI Agent Sandboxes: Why Your Homelab Needs One (and How to Set It Up)

Let's be honest about something: when you give an AI coding agent access to your terminal, you're handing the keys to a stranger who occasionally hallucinates.

Claude Code, OpenClaw, Codex CLI, Cursor, Aider — they all work the same way. You type a prompt. The agent reads your files, writes code, and executes shell commands. Sometimes it runs `rm -rf` in the wrong directory. Sometimes it installs packages you didn't ask for. And if you've given it unrestricted access, it can touch anything on your system.

This isn't paranoia. It's the reality of running AI agents in 2026. The good news: sandboxing has gotten really good, really fast. There are now multiple open-source tools that let you run AI agents in isolated environments — and they're all self-hostable on your homelab.

I spent the last week testing the major options. Here's what works, what doesn't, and how to set it up.

## Why Sandbox an AI Agent?

Before we get into the tools, let's talk about what you're actually protecting against:

**Real risks, not theoretical ones:**

1. **Accidental file destruction.** An agent misinterprets a prompt and deletes the wrong directory. Claude Code has a `--dangerously-skip-permissions` flag for a reason — people have learned the hard way.

2. **Dependency pollution.** An agent installs 47 npm packages to solve a problem that needed 2. Your system is now running code from 47 strangers.

3. **Network exposure.** An agent starts a dev server on port 3000, which happens to be exposed through your reverse proxy. Now the internet can see your half-built app.

4. **Credential leakage.** An agent reads your `.env` file to debug an issue, then accidentally includes your API keys in a generated config file that gets committed to a public repo.

5. **Resource exhaustion.** An agent spawns a runaway process that eats all your RAM and crashes your other services.

These aren't edge cases. They happen. The question isn't *if* you should sandbox — it's *which* sandbox fits your workflow.

## The Sandbox Landscape (July 2026)

Here's what's available right now:

| Tool | Stars | Approach | Best For | Setup Difficulty |
|------|-------|----------|----------|-----------------|
| **Dormice** | 280⭐ | Lightweight container sandbox, E2B-compatible | Quick setup, Claude Code / OpenClaw integration | Easy |
| **Firecracker** | 26k⭐ | MicroVM (used by AWS Lambda) | Maximum isolation, production-grade | Hard |
| **Docker isolation** | n/a | Standard Docker with resource limits | Familiar tooling, existing Docker hosts | Easy |
| **containarium** | 5⭐ | Browser-based sandbox with VNC | Visual debugging, web-based agents | Medium |
| **rocketplaneIO** | 176⭐ | Self-hosted AI SRE for Kubernetes | K8s-native environments | Hard |

For most homelabbers, **Dormice** is the sweet spot. It's purpose-built for AI agent sandboxing, takes 5 minutes to set up, and works with any agent that supports the E2B protocol (which is most of them). If you need military-grade isolation, Firecracker is the answer — but you'll pay for it in setup complexity.

Let's walk through each option.

---

## Option 1: Dormice — The "SQLite of Agent Sandboxes"

[Dormice](https://github.com/nicedoc/dormice) is a self-hosted sandbox runtime designed specifically for AI coding agents. It's E2B-compatible, which means any tool that works with E2B (Claude Code, OpenClaw, Aider, Cursor) can use Dormice as a drop-in replacement — except your code stays on your hardware instead of going to E2B's cloud.

**What makes it good:**
- Single binary, no external dependencies
- Sub-second sandbox creation
- Filesystem isolation (each sandbox gets its own root)
- Network isolation (no outbound access by default)
- Resource limits (CPU, memory, disk)
- E2B API compatibility

### Setting Up Dormice

**Prerequisites:** A Linux server or Proxmox LXC with Docker installed. (Dormice runs in Docker, which means you can put it anywhere in your homelab.)

```bash
# 1. Pull and run Dormice
docker run -d \
  --name dormice \
  --restart unless-stopped \
  -p 49999:49999 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dormice-data:/data \
  ghcr.io/nicedoc/dormice:latest

# 2. Verify it's running
curl http://localhost:49999/health
# Should return: {"status":"ok"}
```

That's it. Dormice is now running on port 49999.

### Connecting Claude Code to Dormice

Claude Code supports E2B sandboxes natively. To point it at your local Dormice instance:

```bash
# Set the E2B API URL to your Dormice instance
export E2B_API_URL="http://192.168.1.XXX:49999"
export E2B_API_KEY="dormice"  # Dormice doesn't require auth by default

# Now run Claude Code — it will use Dormice for sandboxing
claude --sandbox e2b
```

For OpenClaw, add this to your gateway config:

```json
{
  "sandbox": {
    "provider": "e2b",
    "e2b": {
      "apiUrl": "http://192.168.1.XXX:49999",
      "apiKey": "dormice"
    }
  }
}
```

### What Happens Under the Hood

When your agent creates a sandbox, Dormice:

1. Spawns a fresh Docker container with an isolated filesystem
2. Mounts only the directories you explicitly allow
3. Sets CPU and memory limits (configurable per sandbox)
4. Blocks outbound network access (configurable)
5. Returns a sandbox ID your agent uses for all subsequent operations

When the agent is done, the sandbox is destroyed. No cleanup, no leftover processes, no mystery files.

### Dormice Configuration

Create a `dormice-config.yaml` for more control:

```yaml
sandbox:
  default_timeout: 300  # 5 minutes max per sandbox
  max_sandboxes: 5      # Prevent runaway creation
  resources:
    cpu_limit: "2.0"
    memory_limit: "2Gi"
    disk_limit: "10Gi"
  network:
    allow_outbound: false  # Block internet access by default
    allowed_domains:       # Whitelist specific domains
      - "registry.npmjs.org"
      - "pypi.org"
      - "github.com"
  mounts:
    read_only:             # Agent can read but not write
      - "/home/bryan/projects"
    read_write:            # Agent can read and write
      - "/tmp/agent-workspace"
```

Mount this config:

```bash
docker run -d \
  --name dormice \
  -v $(pwd)/dormice-config.yaml:/etc/dormice/config.yaml \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 49999:49999 \
  ghcr.io/nicedoc/dormice:latest
```

---

## Option 2: Firecracker MicroVMs — Maximum Isolation

If Dormice is a locked room, Firecracker is a concrete bunker. It's the same technology AWS uses to run Lambda functions — each sandbox is a full virtual machine with its own kernel, booting in under 125ms.

**When to use Firecracker over Dormice:**
- You're running agents that need to install system packages (`apt`, `yum`)
- You need kernel-level isolation (containers share the host kernel)
- You're building a multi-tenant platform where different users run agents
- You want the absolute maximum security boundary

**The trade-off:** Setup is significantly more complex. You need to build a root filesystem image, configure networking, and manage VM lifecycles.

### Setting Up Firecracker on Proxmox

The easiest path is running Firecracker inside a Proxmox VM (Firecracker needs KVM, which Proxmox LXC containers don't provide by default).

**Step 1: Create a Proxmox VM for Firecracker**

```bash
# On your Proxmox host
qm create 200 \
  --name firecracker-sandbox \
  --memory 4096 \
  --cores 4 \
  --net0 virtio,bridge=vmbr0 \
  --ostype l26
```

Install Ubuntu Server 24.04 on this VM, then:

**Step 2: Install Firecracker**

```bash
# Download the Firecracker binary
ARCH="$(uname -m)"
release_url="https://github.com/firecracker-microvm/firecracker/releases"
latest=$(basename $(curl -fsSLI -o /dev/null -w %{url_effective} ${release_url}/latest))
curl -fsSL ${release_url}/download/${latest}/firecracker-${latest}-${ARCH}.tgz | tar -xz

# Move to path
sudo mv release-${latest}-firecracker-${ARCH}/firecracker-${latest}-${ARCH} /usr/local/bin/firecracker
sudo chmod +x /usr/local/bin/firecracker

# Verify
firecracker --version
```

**Step 3: Build a Root Filesystem**

Firecracker needs a kernel and root filesystem image. Here's a minimal Ubuntu setup:

```bash
# Create a rootfs image
dd if=/dev/zero of=rootfs.ext4 bs=1M count=4096
mkfs.ext4 rootfs.ext4

# Mount and debootstrap Ubuntu
mkdir rootfs-mount
sudo mount rootfs.ext4 rootfs-mount
sudo debootstrap noble rootfs-mount http://archive.ubuntu.com/ubuntu/

# Set up basic config
echo "sandbox" | sudo tee rootfs-mount/etc/hostname
echo "nameserver 1.1.1.1" | sudo tee rootfs-mount/etc/resolv.conf

# Unmount
sudo umount rootfs-mount
```

**Step 4: Start a Firecracker MicroVM**

Firecracker uses a REST API for control. Start the process:

```bash
firecracker --api-sock /tmp/firecracker.sock
```

Then configure and boot the VM via the API:

```bash
# Set kernel
curl --unix-socket /tmp/firecracker.sock -i \
  -X PUT 'http://localhost/boot-source' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "kernel_image_path": "./vmlinux-6.1",
    "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"
  }'

# Set rootfs
curl --unix-socket /tmp/firecracker.sock -i \
  -X PUT 'http://localhost/drives/rootfs' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "drive_id": "rootfs",
    "path_on_host": "./rootfs.ext4",
    "is_root_device": true,
    "is_read_only": false
  }'

# Start the VM
curl --unix-socket /tmp/firecracker.sock -i \
  -X PUT 'http://localhost/actions' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"action_type": "InstanceStart"}'
```

This is the "raw" approach. For production use, you'll want a management layer. [OtoDock](https://github.com/otodock/otodock) wraps Firecracker with a clean API and is worth checking out if you go this route.

### Proxmox MicroVM Alternative (Easier)

Proxmox 9.1 added native OCI/Docker support and improved MicroVM handling. If you're already on Proxmox, you can create MicroVMs directly:

```bash
# Create a MicroVM template
qm create 9000 --name ubuntu-microvm-template --memory 2048 --cores 2
qm set 9000 --machine q35 --bios ovmf
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:0,import-from=/var/lib/vz/template/iso/ubuntu-24.04-server-cloudimg-amd64.img
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --boot order=scsi0
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1
qm template 9000

# Clone a sandbox from the template (takes ~3 seconds)
qm clone 9000 201 --name agent-sandbox-01 --full false
qm start 201
```

This gives you VM-level isolation with Proxmox-native tooling. The clone-from-template approach means new sandboxes spin up in seconds.

---

## Option 3: Docker Isolation — Quick and Familiar

If you're not ready for Dormice or Firecracker, plain Docker with strict resource limits is better than nothing. It won't give you kernel-level isolation, but it will contain filesystem damage and resource exhaustion.

### Minimal Docker Sandbox for AI Agents

```bash
# Create a sandboxed workspace
docker run -d \
  --name agent-sandbox \
  --memory="4g" \
  --memory-swap="4g" \
  --cpus="2.0" \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=2g \
  --tmpfs /home/sandbox:rw,noexec,nosuid,size=10g \
  --network none \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  ubuntu:24.04 \
  tail -f /dev/null

# Enter the sandbox
docker exec -it agent-sandbox bash
```

**What this does:**
- `--memory="4g"` — caps RAM at 4GB
- `--cpus="2.0"` — limits to 2 CPU cores
- `--read-only` — root filesystem is immutable
- `--tmpfs` — writable temp directories that disappear on container stop
- `--network none` — no network access at all
- `--cap-drop ALL` — drops all Linux capabilities
- `--security-opt no-new-privileges` — prevents privilege escalation

**The limitation:** This is still a container sharing your host kernel. A determined (or hallucinating) agent could potentially escape. For most homelab use cases, this is "good enough" — but understand the trade-off.

### Docker Compose for Persistent Sandboxes

If you want sandboxes that persist between sessions:

```yaml
# docker-compose.sandbox.yml
version: '3.8'
services:
  sandbox:
    image: ubuntu:24.04
    command: tail -f /dev/null
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=2g
      - /home/sandbox:rw,noexec,nosuid,size=10g
    network_mode: none
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    volumes:
      - ./workspace:/workspace:ro  # Read-only project files
      - sandbox-output:/output:rw  # Writable output only
```

---

## Which Sandbox Should You Use?

Here's my honest recommendation based on what you're actually doing:

| Your Use Case | Recommended Sandbox | Why |
|---------------|-------------------|-----|
| **Claude Code / OpenClaw on your main machine** | Dormice | 5-minute setup, E2B-compatible, good enough isolation |
| **Running agents for other people** | Firecracker | Kernel-level isolation, multi-tenant safe |
| **Quick experiments, throwaway code** | Docker isolation | Fastest to spin up, familiar tooling |
| **Proxmox homelab, already running VMs** | Proxmox MicroVMs | Native integration, VM-level isolation |
| **CI/CD pipeline running AI-generated code** | Firecracker | Production-grade, auditable |
| **Just testing the waters** | Dormice | Lowest friction, easiest to undo |

**My setup:** I run Dormice on a Proxmox LXC (2 cores, 4GB RAM) for day-to-day Claude Code and OpenClaw work. For anything that needs to install system packages or run untrusted code, I clone a Proxmox MicroVM template. It's a good balance of convenience and security.

---

## Real-World Example: Sandboxing a Claude Code Session

Here's what a typical workflow looks like with Dormice:

```bash
# 1. Start Dormice (if not already running)
docker start dormice

# 2. Point Claude Code at your local sandbox
export E2B_API_URL="http://192.168.1.202:49999"
export E2B_API_KEY="dormice"

# 3. Run Claude Code with sandboxing
claude --sandbox e2b

# Inside Claude Code:
# > Build a Python script that scrapes Hacker News and saves the top 10 stories to a CSV
#
# Claude Code will:
# - Create a sandbox via Dormice
# - Install dependencies inside the sandbox
# - Write and test the script
# - Return the final output to your workspace
# - Destroy the sandbox when done
```

The agent never touches your real filesystem. It can't access your `.ssh` keys, your `.env` files, or your browser history. If it tries to `rm -rf /`, it only nukes its own sandbox — which gets destroyed anyway.

---

## Security Checklist: Before You Let an Agent Loose

Even with sandboxing, follow these rules:

- [ ] **Never run agents as root.** Create a dedicated user with minimal permissions.
- [ ] **Use read-only mounts for sensitive directories.** Your `~/Documents` folder should be read-only to the agent.
- [ ] **Block outbound network by default.** Whitelist only the domains your agent actually needs (package registries, APIs).
- [ ] **Set resource limits.** CPU, memory, and disk caps prevent a runaway agent from taking down your server.
- [ ] **Audit agent actions.** Dormice and Firecracker both support logging. Review what your agents are doing periodically.
- [ ] **Rotate sandboxes.** Don't reuse sandboxes across sessions. Fresh sandbox = clean state = no leftover surprises.
- [ ] **Keep sandbox tools updated.** Dormice, Firecracker, and Docker all release security patches. Stay current.

---

## What's Coming Next

The AI agent sandbox space is moving fast. Here's what I'm watching:

- **Dormice v1.0** — The project is approaching a stable release with snapshot/restore, multi-tenant support, and a web dashboard.
- **Proxmox MicroVM tooling** — As Proxmox 9.x matures, expect one-click MicroVM sandbox creation from the web UI.
- **E2B protocol adoption** — More tools are adopting the E2B sandbox protocol, which means Dormice will work with an expanding ecosystem.
- **GPU passthrough** — Running AI agents that need GPU access inside sandboxes is the next frontier. Firecracker supports GPU passthrough experimentally.

---

## The Bottom Line

If you're running AI coding agents on your homelab without sandboxing, you're one hallucinated `rm -rf` away from a bad night. The tools exist. They're free. They're open-source. And the best one (Dormice) takes 5 minutes to set up.

Start with Dormice. It's the right answer for 90% of homelabbers. If you outgrow it, Firecracker is waiting.

Your future self — the one who didn't lose their `~/Projects` directory at 2 AM — will thank you.

---

**Resources:**
- [Dormice on GitHub](https://github.com/nicedoc/dormice) — Self-hosted E2B-compatible sandbox
- [Firecracker](https://github.com/firecracker-microvm/firecracker) — AWS's open-source MicroVM
- [OtoDock](https://github.com/otodock/otodock) — Firecracker management layer
- [Proxmox MicroVM Guide](https://pve.proxmox.com/wiki/MicroVM) — Official Proxmox documentation

*Have you set up agent sandboxing in your homelab? I'd love to hear what's working for you. Find me on [Reddit](https://reddit.com/r/selfhosted) or [Hacker News](https://news.ycombinator.com).*
