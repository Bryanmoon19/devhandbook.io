---
layout: post.njk
title: "Ditch Docker? Podman vs Docker for the Homelab — An Honest Verdict"
date: 2026-08-22
description: "Every few months the same Hacker News thread resurfaces: someone ditched Docker for Podman and never looked back. But the homelab is a different beast than a production Kubernetes cluster. Here's the honest, hands-on comparison — Docker Hub rate limits, rootless containers, systemd integration, and whether the switch is actually worth it when you're running containers inside LXC on Proxmox."
tags: ["docker", "podman", "containers", "homelab", "proxmox", "lxc", "self-hosted", "rootless", "docker-hub", "devops"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-22-ditch-docker-podman-vs-docker-homelab"
affiliate: true
cta: true
---

There's a genre of Hacker News post that never really dies. It goes something like this: *"I ditched Docker for Podman and never looked back"* — 1,123 points, hundreds of comments, and a top thread full of people nodding along about how Docker is bloated, how the daemon is a security hole, and how rootless Podman is the future.

Then there's the other one, the one that actually stings: the Docker Hub hack that hit 1,146 points, where a compromised image sat on the registry for who knows how long before anyone noticed. And underneath both of them, a quieter, more persistent grumble about Docker Hub's pull rate limits and Docker's licensing changes that pushed a lot of self-hosters to start asking the question in the title.

I run Docker inside LXC containers on Proxmox. I feel the Hub pain firsthand — the `toomanyrequests` errors, the anonymous pull limits, the nagging feeling that I'm one compromised base image away from a bad week. So I did what any reasonable homelabber does: I actually tried Podman. Not in a throwaway VM, but on the same hardware, running the same services, for long enough to form a real opinion.

This is that opinion. It's not a "Podman is better" manifesto, and it's not a "Docker is fine, stop worrying" dismissal. It's the honest comparison I wish someone had written before I spent a weekend on it — because the homelab is a *different beast* than the production Kubernetes clusters where most of the Podman evangelism comes from.

## Why This Keeps Coming Up

Let me set the table, because the "ditch Docker" conversation is really three separate conversations that keep getting mashed together.

**First, the security story.** Docker's architecture runs a single privileged daemon (`dockerd`) as root. Every container you launch talks to that daemon, and the daemon has root on the host. If a container escapes — or if you misconfigure a volume mount — you've handed root to whatever's inside. Podman's headline feature is that it's *daemonless* and *rootless*: no long-running root process, and containers can run as your unprivileged user with user namespaces doing the isolation. For a homelabber who's been burned by a bad image, that's a genuinely compelling pitch.

**Second, the licensing and rate-limit story.** Docker Desktop's license change in 2021 (free for individuals and small businesses, paid for larger companies) spooked a lot of people, even though it mostly didn't affect homelabbers. The Docker Hub pull rate limits — 100 pulls per 6 hours for anonymous users, 200 for authenticated free users — are a *much* more real pain point. If you're pulling a dozen images across a few LXC containers, you can hit that ceiling faster than you'd think, especially when you're rebuilding or experimenting.

**Third, the "Docker is bloated" story.** The daemon, the CLI, the build cache, the networking stack — Docker bundles a lot. Podman's pitch is that it's a drop-in CLI replacement (`alias docker=podman`) that's lighter, more Unix-y, and plays nicer with systemd.

All three are real. But here's the thing the HN threads don't tell you: **the homelab is the one place where Docker's "bloat" is actually a feature, and Podman's "purity" is sometimes a tax.**

## What Podman Actually Is

Before I get into the comparison, let me be precise about what Podman is and isn't, because a lot of the confusion comes from people treating it as "Docker but free."

[Podman](https://podman.io) is a daemonless container engine from Red Hat. It uses the same OCI container format and the same images as Docker — a `docker.io/library/nginx:latest` image runs identically under both. The difference is *how* it runs them:

- **No daemon.** `podman run` launches a container directly, as a child process of your shell, not by talking to a background `dockerd`. When the container stops, there's no daemon left running.
- **Rootless by default.** Podman can run containers as your regular user, using user namespaces to map your UID to root *inside* the container. The container thinks it's root, but on the host it's just you.
- **systemd-native.** Podman can generate systemd unit files (`podman generate systemd`) so your containers are managed by systemd like any other service — no `restart: always` in a compose file, no Docker daemon to babysit.
- **Pod support.** Podman has first-class "pods" — groups of containers that share a network namespace, Kubernetes-style. This is genuinely useful and something Docker only approximates with `network_mode: service:`.

The catch, and it's a big one for homelabbers: **Podman's Compose support is a second-class citizen.** There's `podman-compose` (a Python reimplementation) and Podman's own `podman compose` (which shells out to `docker-compose` or `podman-compose`), but neither is a perfect drop-in for the `docker compose` you already know. And since the entire self-hosted world — every `docker-compose.yml` on GitHub, every "just run this compose file" tutorial — is written for Docker, that's a real friction point.

## The Honest Comparison

Let me put the two side by side on the axes that actually matter for a homelab, not for a production cluster.

### Security: Podman wins, but the gap is smaller than you think

This is Podman's strongest argument, and it's real. A rootless Podman container is meaningfully harder to escape than a rootful Docker container, because there's no root daemon to compromise and the container's "root" is just your user on the host.

But here's the nuance the evangelists skip: **you can run Docker rootless too.** Docker has supported rootless mode since 2021, and it works fine for most homelab workloads. It's not as polished as Podman's rootless story, and it has some limitations (no `--privileged`, some networking features need extra setup), but the "Docker is inherently insecure" framing is outdated.

The bigger security win for Podman is architectural: no always-on root daemon means a smaller attack surface, period. If you're running containers that face the internet — a reverse proxy, a web app, anything with a port open — that's a legitimate reason to prefer Podman.

### Docker Hub rate limits: this is where it gets personal

This is the pain I feel most directly, and it's worth being precise about, because it's the thing that actually drives people to switch.

Docker Hub's limits are: **100 pulls per 6 hours for anonymous users, 200 per 6 hours for authenticated free users.** That sounds like a lot until you realize that a single `docker compose pull` on a stack with 10 services is 10 pulls, and a rebuild that re-pulls base images can chew through dozens more. Run a few LXC containers, experiment a bit, and suddenly you're staring at:

```
ERROR: toomanyrequests: Too Many Requests.
You have reached your pull rate limit.
```

The fix most people land on is a **registry mirror or a pull-through cache** — either self-hosted (like [Docker Registry](https://docs.docker.com/registry/) or [Harbor](https://goharbor.io)) or a public mirror. That solves the rate-limit problem *without* switching container engines. But it's an extra moving part, and it's exactly the kind of thing that makes you wonder if there's a simpler path.

Here's the thing about Podman and rate limits: **Podman doesn't magically fix them.** Podman pulls from the same Docker Hub, and it's subject to the same anonymous limits. What Podman *does* give you is a cleaner path to a local mirror — because it's daemonless, you can point it at a local registry with a simple config file, and there's no daemon cache to fight with. But the rate limit itself is a Docker Hub policy, not a Docker Engine problem.

### systemd integration: Podman's quiet killer feature

This is the one that surprised me, and it's the reason I think Podman is genuinely underrated for homelabs specifically.

When you run Docker, your containers are managed by the Docker daemon, which is managed by systemd. There's a layer of indirection: systemd → dockerd → container. If dockerd crashes, all your containers go down with it, and you're relying on Docker's restart policy to bring them back.

With Podman, you can generate a systemd unit for each container (or pod), and systemd manages it *directly*. Your container becomes a first-class service:

```bash
# Run a container, then generate a systemd unit for it
podman run -d --name nginx -p 8080:80 docker.io/library/nginx
podman generate systemd --new --name nginx > ~/.config/systemd/user/nginx.service
systemctl --user enable --now nginx.service
```

Now systemd starts it on boot, restarts it if it crashes, and you can `systemctl --user status nginx` to see exactly what's happening. No daemon in the middle. For a homelabber who already lives in systemd (and if you run Proxmox, you do), this is a *much* more natural fit than Docker's restart policies.

The tradeoff: you lose the convenience of `docker compose up -d` managing a whole stack as one unit. You can get it back with `podman-compose` or by generating units for a whole pod, but it's more manual.

### Compose compatibility: Docker wins, and it's not close

This is the dealbreaker for most homelabbers, and I want to be blunt about it.

The self-hosted ecosystem runs on `docker-compose.yml`. Every project's README says "copy this compose file and run `docker compose up -d`." When you switch to Podman, you're now translating every one of those files, debugging the places where `podman-compose` doesn't quite match Docker's behavior, and explaining to every tutorial author why their instructions don't work for you.

`podman-compose` is a heroic effort, but it's a reimplementation, and it lags. `podman compose` is better than it used to be, but it still has gaps — certain `depends_on` conditions, some networking setups, and anything that relies on Docker-specific features will trip you up.

If your homelab is 30 services you run from compose files you didn't write, **Podman's Compose friction will cost you more time than its security benefits will save you.** That's not a knock on Podman — it's a statement about where the ecosystem's gravity is.

### Running inside LXC: the elephant in the room

I run Docker inside LXC containers on Proxmox, and this is where the comparison gets genuinely interesting, because **Podman and Docker behave very differently inside an unprivileged LXC.**

Docker inside LXC is a known quantity. It works, but it's finicky: you need `nesting=1` and `keyctl=1` on the LXC config, you often need to run the container privileged (or at least with specific capabilities), and overlayfs can be a headache. It's the classic "works but you're fighting it" situation.

Podman inside LXC is, counterintuitively, *cleaner* in some ways — because Podman is already rootless and daemonless, it doesn't need the same privileged setup that Docker's daemon does. You can run rootless Podman inside an unprivileged LXC and get a much cleaner isolation story: LXC isolates the container from the host, and Podman's user namespaces isolate the containers from each other.

But — and this is the honest part — **most people running Docker in LXC aren't doing it because they love Docker's architecture. They're doing it because that's what the tutorials say, and it works.** Switching to Podman inside LXC is a real project, and the payoff is mostly architectural elegance, not a concrete problem you were having.

## The Six HN Stories, Actually Read

Let me actually engage with the evergreen threads, because they're the reason this post exists, and they deserve more than a drive-by.

1. **The Docker Hub hack (1,146 points).** A compromised image sat on Docker Hub, and the takeaway everyone drew was "don't trust the registry." The *correct* takeaway is more specific: pin your images by digest, not by tag, and don't pull `latest` in production. That's true whether you use Docker or Podman — Podman doesn't protect you from a malicious image, it just changes how you run it.

2. **"I ditched Docker for Podman" (1,123 points).** The author's actual reasons were rootless security and systemd integration, and those are *legitimate*. But the author was running a production workload, not a homelab, and the Compose friction that's a minor annoyance at work is a major one at home.

3. **The licensing panic.** Docker Desktop's license change barely affects homelabbers — you're almost certainly not running Docker Desktop on a headless Proxmox box. The *rate limits* are the real issue, and they're a Docker Hub policy, not a Docker Engine one.

4. **The "Docker is bloated" thread.** True, but bloat is a tradeoff. Docker's daemon is what makes `docker compose up -d` and `restart: always` work with zero thought. Podman's leanness is what makes it elegant, but it's also what makes it more manual.

5. **The "rootless is the future" thread.** Rootless *is* the future, and Docker has been moving that way too. But "the future" and "what works today with the compose files I already have" are different things.

6. **The "just use systemd-nspawn / LXC directly" thread.** This one's actually the most interesting for homelabbers, because it's the real third option: skip containers-as-Docker entirely and use LXC natively on Proxmox. I've written about this before, and it's a legitimate path — but it's a different workflow, not a drop-in Docker replacement.

The pattern across all six: **the threads are written by and for people running production workloads, and the homelab is a different context with different tradeoffs.** That's the gap this post is trying to fill.

## My Actual Recommendation

Here's where I land, and I'll be direct.

**If you're a typical homelabber running 10-30 services from compose files you found on GitHub: stay on Docker.** The Compose compatibility alone is worth it, and the security gap is smaller than the threads make it sound — especially if you run rootless Docker or keep your containers in unprivileged LXC. Fix the rate-limit problem with a registry mirror, not an engine switch.

**If you're security-conscious and run internet-facing services: try rootless Podman for those specific services.** You don't have to switch everything. Run your reverse proxy, your web apps, anything with a port open, under rootless Podman, and keep your internal services on Docker. It's not all-or-nothing.

**If you already live in systemd and want containers to behave like services: Podman is genuinely better.** The `podman generate systemd` workflow is the one thing that made me seriously consider switching, and if you're the kind of person who writes your own unit files, you'll love it.

**If you run Docker inside LXC and it's working: don't switch for the sake of switching.** The architectural elegance of rootless Podman inside unprivileged LXC is real, but it's a solution to a problem you probably don't have. Spend the weekend on backups or monitoring instead.

**If you're starting fresh and have no Docker investment: Podman is worth a serious look.** No legacy compose files, no muscle memory — you can build the rootless, systemd-native workflow from day one and never miss Docker.

## The Bottom Line

Podman is a genuinely good tool, and the "ditch Docker" crowd isn't wrong about its technical merits. Rootless security is real, systemd integration is a killer feature, and the daemonless architecture is cleaner. If I were building a production Kubernetes cluster, I'd take Podman seriously.

But the homelab is not a production cluster. It's a place where you run 30 services from compose files you didn't write, where "it works" beats "it's elegant," and where the Docker Hub rate limit is a registry problem, not an engine problem. For most of us, the honest answer to "should I ditch Docker for Podman?" is: **not yet, and maybe not ever — but run the internet-facing stuff rootless, and keep an eye on Podman, because it's getting better every release.**

The real lesson from those six HN threads isn't "Docker is bad." It's "understand what you're running, pin your images, and don't trust `latest`." Do that, and you've solved 90% of the problem — regardless of which engine you pick.

---

*Are you running Podman in your homelab, or did you try it and go back to Docker? I'm genuinely curious where people land on this — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [Portainer alternatives](/blog/2026-06-03-portainer-alternatives-proxmox-lxc) and the [Docker backup playbook](/blog/2026-08-14-docker-backup-playbook-restic-dockstash).*
