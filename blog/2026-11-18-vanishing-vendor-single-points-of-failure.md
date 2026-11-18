---
layout: post.njk
title: "The Vanishing Vendor: Auditing Your Open-Source Single Points of Failure"
date: 2026-11-18
description: "Microsoft's ONNX Runtime — a 22,000-star repo your stack probably depends on transitively — vanished from GitHub overnight with no warning. Here's the practical playbook for finding the bus-factor-1 dependencies in your own project before one of them disappears under you."
tags: ["supply-chain", "open-source", "dependencies", "bus-factor", "security", "onnx", "onnxruntime", "pypi", "vendor-lock-in", "self-hosted", "audit"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-18-vanishing-vendor-single-points-of-failure/"
affiliate: false
cta: true
---

# The Vanishing Vendor: Auditing Your Open-Source Single Points of Failure

On November 17, 2026, a repository with **22,000 GitHub stars** simply stopped existing.

Microsoft's `onnxruntime` — the most widely used engine for serving deep-learning models in production — went dark overnight. No deprecation notice, no archive banner, no migration guide. One developer on Hacker News found out the hard way: *"We found out about this this morning, when evals started failing in our pipelines."* Another had a PR queued up: *"Guess I won't submit the PR I was working on tonight then."*

This isn't a hypothetical risk for the careful few. It's the dependency graph you already ship. Here's the thing most supply-chain writing skips: it's not just *malicious* code you need to worry about. A vendor can hurt you just as badly by **walking away**.

---

## What Actually Happened (and What Didn't)

Let me be precise, because the panic and the reality diverged in ways that matter.

**What disappeared:** the `microsoft/onnxruntime` GitHub repository. As of this writing, hitting the GitHub API for it returns a clean **404** — not a redirect, not an archive, a dead link. The HN thread (258 points, 59 comments) filled with people discovering their CI breakage in real time.

**What did *not* disappear — yet:**

- The **PyPI package** `onnxruntime` is still there, latest **1.32.0**.
- The **npm package** `onnxruntime-node` still resolves (1.31.1).
- The **website** `onnxruntime.ai` still returns 200.
- The **spec repo** `onnx/onnx` (21,700+ stars) is alive and healthy — and this is a common point of confusion, because ONNX-the-standard and ONNX-Runtime-the-implementation share a name.

So the binaries still download and the docs still load. What's gone is the *source of truth* — the place where the actual code, issues, releases, and commit history live. The distinction is exactly why this is scary rather than catastrophic: **the packages keep working until the next release never comes.**

That's the whole lesson in miniature. When a vendor vanishes, it doesn't usually take your working code down in a blaze. It takes the *future* down — the security patch you'll need in March, the bug fix you'll need in April, the person who used to answer your issue. A repo going 404 is the loud version of the quiet thing that happens to thousands of smaller packages every year: the maintainer just stops.

**And it happened twice in the same 24-hour window.** Separately, Microsoft's `agent-framework` package on PyPI was compromised — two malicious releases shipped a **credential stealer** (reported by both Aikido and Socket). One vendor vanishing, one vendor's package poisoned. Same week. The lesson is the same: **you don't own your dependencies.**

---

## The Real Risk Is Bus Factor, Not Just Malware

The security industry has trained us to think about supply chain as *attack* — someone injects malicious code, you get pwned, scanners catch it. That's real, and the `agent-framework` incident is exactly that shape.

But there's a second, quieter failure mode that gets almost no airtime: **maintenance abandonment.** A single maintainer burns out, changes jobs, or just drifts away — and a package you depend on silently enters the "zombie" phase where it technically works but nobody is home.

The term is **bus factor** (or "truck factor"): *how many people would have to get hit by a bus before your dependency is unmaintained?* A package with a bus factor of 1 is one life event away from becoming the next ONNX Runtime.

Most supply-chain content covers malicious injection. Almost nobody covers *this* — the "what happens when the repo just disappears" angle. Which is why it's the gap worth owning.

---

## The Audit: Find Your Own Bus-Factor-1 Dependencies

You can run this in an afternoon, no paid tooling required.

### Step 1 — Enumerate what you actually ship

Start with your lockfiles, not your head:

```bash
# Node
npm ls --all --json > deps.json          # or: yarn list --depth=5
# Python
pip freeze > requirements.lock
# Rust
cargo tree --edges normal
# Go
go list -m all
```

The key is the *transitive* graph — the dependencies of your dependencies. Most people know their top-level deps. Almost nobody knows the 4th-level `left-pad`-style package quietly holding their build together.

### Step 2 — Score each one for bus factor

For every meaningful dependency, ask three questions:

1. **How many active committers in the last 90 days?** One person, or a healthy handful?
2. **Is it a company-owned repo or a solo project?** Company repos *should* be safer, but ONNX Runtime just proved that's not a guarantee — Microsoft is a company with an org chart and it still went dark.
3. **When was the last release, and does the maintainer respond to issues?**

A useful heuristic: a repo where the last commit is over a year old *and* the top committer is a single person is a ticking clock. It works today; it's a liability tomorrow.

### Step 3 — Vendor or pin your critical path

For the dependencies you *cannot* afford to lose, you have three escalating options:

1. **Pin + mirror.** Lock to exact versions and mirror the tarballs to your own storage so a registry outage or package yank can't break your builds. This is the minimum.
2. **Fork.** Keep your own copy of the repo. When `intel/onnxruntime` became the de-facto "soft fork" people pointed to on HN, that was the community scrambling to do in a panic what you can do calmly now.
3. **Replace with something you host.** If a dependency is truly critical and truly fragile, the only durable fix is to own it — same thesis as self-hosting everything else.

---

## What to Do About ONNX Runtime Specifically

If you depend on it (directly or through something like `transformers`, an ML serving layer, or a browser-side model runtime), the honest near-term moves are:

- **Don't panic-delete it.** The packages still work and still resolve. You have time.
- **Pin your version now** so a future hostile or accidental release can't slip in.
- **Watch the `onnx/onnx` spec repo and `intel/onnxruntime`** as the live forks/continuations. Intel's fork (OpenVINO-flavored) was pushed to on 2026-11-17 — it's the closest actively-maintained successor people are rallying around.
- **Have a migration path in your head** — ONNX models are the portability layer, which is exactly why the format was invented. The *runtime* is replaceable even if the *repo* isn't.

---

## The Checklist (Copy This)

Run it once, then re-run it every few months — your dependency graph changes faster than you think.

- [ ] `npm ls` / `pip freeze` / `cargo tree` — got the full transitive graph
- [ ] Identified every dependency with a **bus factor of 1**
- [ ] Flagged every repo with **no commit in 12+ months**
- [ ] Pinned critical-path packages to exact versions
- [ ] Mirrored those tarballs to storage you control
- [ ] Forked the one or two repos you truly can't afford to lose
- [ ] Documented, per critical dep, who the "owner" is and what the fallback is

---

The throughline of this whole site is the same as this post: **you don't own what you didn't build, and you can't trust what you don't control.** Supply-chain security isn't just about stopping attackers — it's about knowing, *before* the 404 lands, which of your dependencies is one person away from becoming a ghost.

*Want to go further? Start with the [self-hosted stack builder](https://devhandbook.io/self-hosted-stack-builder/) and see how much of your critical path you can move onto infrastructure you actually own.*
