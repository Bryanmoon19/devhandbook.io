---
layout: post.njk
title: "Cursor Origin vs Self-Hosted Git: A Decision Framework, Not a Feature List"
date: 2026-08-19
description: "Cursor just shipped Origin, its own GitHub alternative, and the HN thread hit 525 points. Yesterday I wrote about Gitea, Forgejo, and GitLab as exit ramps from GitHub. Now there's a new question: does a hosted, AI-native Git platform change the calculus? Here's a decision framework for choosing between Cursor Origin and self-hosted Git — not a spec sheet, but a way to think about what you're actually trading."
tags: ["self-hosted", "git", "cursor", "origin", "gitea", "forgejo", "gitlab", "github", "ai", "devops", "version-control"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-19-cursor-origin-vs-selfhosted-git"
---

Yesterday I published a piece on [self-hosted Git](/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab) — Gitea, Forgejo, and GitLab as exit ramps from GitHub. The thesis was simple: the GitHub trust crisis is real, the self-hosted options have never been better, and if your motivation is "I don't want a corporation owning my code platform," Forgejo is the answer and it isn't close.

Then, almost on cue, Cursor shipped **Origin** — its own hosted Git platform — and the "Show HN" thread hit 525 points. The timing is almost too perfect. It's the exact counter-argument to everything I wrote: *why self-host when the AI-native future of code hosting just arrived, fully managed, with zero infrastructure to run?*

So this is the sequel. Not a feature list — you can read Cursor's launch page for that. This is a **decision framework**. Because the real question isn't "which tool has more features." It's "what are you actually optimizing for, and which of these two paths gets you there?"

## The Two Paths, Stated Plainly

Let me strip both options down to their essence, because the marketing on both sides is doing a lot of work.

**Cursor Origin** is a hosted Git platform built by the company that makes the Cursor editor. It's AI-native — the pitch is that your code, your issues, your PRs, and your AI agent all live in one place, and the AI understands your entire codebase because it's *in* the platform. You don't run anything. You sign up, you push, and the AI does the rest.

**Self-hosted Git** (Gitea/Forgejo/GitLab) is your code on your own hardware. You run the server, you own the data, you control the governance. The trade-off is that *you* are the one who has to run it, back it up, and keep it alive.

That's the whole decision in one sentence: **Origin trades control for convenience; self-hosted Git trades convenience for control.** Everything else is detail.

The trick is figuring out which side of that trade you actually live on — and being honest about it, because most people *say* they want control and then *act* like they want convenience.

## The Framework: Four Questions

I've found that this decision collapses into four questions. Answer them honestly and the choice mostly makes itself.

### 1. What are you actually fleeing?

This is the question I ended yesterday's post on, and it's the one that matters most here.

If you're leaving GitHub because of **features** — you want better AI integration, a smoother workflow, less friction — then Origin is a legitimate answer. It's arguably the most AI-native Git platform that exists, and if your goal is "make the AI work better with my code," a hosted platform built around that exact goal is hard to beat.

If you're leaving GitHub because of **trust** — you don't want a corporation owning your code, you're worried about AI training on your repos, you want a single point of failure removed — then Origin is not an answer. It's the same problem with a different logo. Cursor is a venture-backed company. Origin is a hosted service. Your code lives on *their* servers, under *their* terms of service, subject to *their* account moderation. If the thing you're fleeing is "a company owns my code platform," Origin is just a newer company.

This is the uncomfortable truth that a lot of the Origin hype is glossing over: **Origin is not an exit ramp from corporate code hosting. It's a different on-ramp to the same highway.** That's not a criticism — it's a categorization. It matters because a lot of people are going to adopt Origin *thinking* they're solving their GitHub trust problem, when they're actually just switching vendors.

### 2. How much do you actually want to run?

Be honest here, because this is where self-hosting advocates (including me) tend to oversell.

Self-hosted Git is not free. It costs you time, attention, and a slice of your hardware. Forgejo is genuinely lightweight — it'll run on a Raspberry Pi — but it's still *your* responsibility. Backups, updates, security patches, uptime, the occasional "why is my Git server down at 2am" moment. That's real, and it's not for everyone.

Origin costs you none of that. You push code and it works. The AI is integrated. There's no server to patch, no database to back up, no TLS cert to renew.

If you're a solo developer who just wants to ship, and the thought of maintaining a Git server makes you tired, Origin is a completely reasonable choice. There's no shame in that. The self-hosting movement has a bad habit of moralizing this decision, and I want to be clear: **choosing a hosted service because you don't want to run infrastructure is a legitimate engineering decision, not a character flaw.**

The question is just whether you're *aware* of what you're trading for that convenience.

### 3. What's your actual threat model?

This is the question that separates the people who should self-host from the people who shouldn't, and it's almost never asked explicitly.

What are you actually afraid of? Write it down. Be specific.

- **"I'm afraid GitHub will train AI on my private code."** → Self-host. A hosted platform, any hosted platform, has access to your code. Origin's whole value proposition is that its AI *reads* your code. If AI access to your code is the thing you're afraid of, Origin is the worst possible choice, not the best.
- **"I'm afraid of losing access to my account."** → Self-host, or at least keep your own mirrors. A hosted platform can suspend you. Your own server can't.
- **"I'm afraid of outages."** → This one's genuinely ambiguous. A hosted platform has a team of engineers keeping it up. Your self-hosted box has *you*. For most people, a hosted service is actually *more* reliable than their own hardware. Don't assume self-hosting wins this one.
- **"I'm afraid of vendor lock-in."** → Self-host, or pick a platform with a clean exit. Git is portable by nature — your repos are just `.git` directories — but issues, PRs, and CI configs are not. The more you lean on Origin's AI-native features, the more locked in you get.
- **"I'm not actually afraid of anything specific, I just have a vague unease."** → This is the most common answer, and it's the one where you should *not* make a big infrastructure commitment based on a feeling. Figure out the specific fear first.

The point of the threat model exercise is that "self-host vs hosted" is not a moral question. It's an engineering question about what failure modes you're actually trying to protect against. Different threat models, different answers.

### 4. What does the AI actually need from your Git host?

This is the genuinely new question that Origin forces, and it's the one that makes this more than a rehash of yesterday's post.

Here's the thing: **AI coding agents don't need your Git host to be AI-native.** They need *access* to your code, and they need it in a form they can work with. A self-hosted Forgejo instance with a good API gives an AI agent everything it needs to read your code, understand your repo, and make changes. The AI doesn't care whether your Git host has a built-in chatbot. It cares whether it can `git clone`, read the files, and push a branch.

Origin's pitch is that the AI is *better* when it's inside the platform — that it has deeper context, better understanding, tighter integration. There's some truth to that. But it's worth being skeptical of the framing that you *need* a hosted AI-native platform to get good AI coding. You don't. You need your code to be accessible, and that's true of any Git host, self-hosted or not.

The real question is: **are you buying Origin for the Git hosting, or for the AI?** Because those are separable. You can self-host your Git and still use Cursor (or Claude Code, or any other agent) against it. You can use Origin and still run your own AI tooling. The AI and the Git host are not the same decision, and Origin's marketing is trying very hard to make you think they are.

## The Decision Matrix

Here's the framework in table form. Read it as "if this is your situation, this is your answer."

| **Your situation** | **Answer** | **Why** |
|---|---|---|
| Fleeing GitHub over trust/AI-training concerns | **Self-host (Forgejo)** | Origin is the same problem with a new logo |
| Want the best AI-native coding experience, don't care about control | **Cursor Origin** | It's genuinely the most AI-integrated hosted Git |
| Solo dev who doesn't want to run infrastructure | **Cursor Origin** | Convenience is a legitimate priority |
| Want to own your data and governance, willing to maintain a server | **Self-host (Forgejo)** | Community-owned, lightweight, portable |
| Need built-in CI/CD and a full platform | **Self-host (GitLab CE)** | Origin doesn't replace a full DevOps platform |
| Not ready to self-host but want off GitHub | **Codeberg** | Forgejo hosted by a non-profit, EU-based |
| Want AI coding but also want to own your code | **Self-host Git + external AI agent** | These are separable decisions; don't conflate them |

## The Case I Actually Want to Make

Here's the argument I want to land, because I think it's the one that's getting lost in the Origin hype cycle.

**The AI and the Git host are two different decisions, and conflating them is how you end up locked into a platform you didn't mean to choose.**

You can have AI-native coding *and* self-hosted Git. You can run Forgejo on a Raspberry Pi and point Cursor, Claude Code, or any other agent at it. The AI doesn't need to live inside your Git host to be good at its job. It needs your code to be accessible, and self-hosted Git makes it accessible *on your terms*.

What Origin is really selling is not "AI-native Git." It's "AI-native Git *that we host for you*." And the "we host for you" part is the part that matters, because that's the part that reintroduces every trust concern you were trying to escape from GitHub.

If you're comfortable with that — if your threat model is "I want the best AI coding experience and I don't care who hosts my code" — then Origin is a great product and you should use it. Genuinely. I'm not here to talk you out of it.

But if you're in the camp that's been eyeing the exit ramp from GitHub because of *trust*, then Origin is not your exit. It's a U-turn. And the thing I want you to understand is that you don't have to choose between "AI-native coding" and "owning your code." Those two things are not in tension. The only thing Origin forces you to choose is *who hosts it* — and that's a choice you should make deliberately, not by default.

## The Bottom Line

Yesterday I said the GitHub trust crisis is real and the exit ramp has never been better paved. That's still true. What Origin adds to the picture is a new *hosted* option that's genuinely compelling on the AI front — and a new reason to be clear-eyed about what you're actually optimizing for.

The framework, one more time:

1. **What are you fleeing?** Features → Origin is fair game. Trust → Origin doesn't help.
2. **How much do you want to run?** Nothing → hosted. A little → Forgejo is genuinely light.
3. **What's your threat model?** Be specific. "Vague unease" is not a reason to buy a server.
4. **What does the AI actually need?** Access to your code, not a hosted platform. Don't conflate the two.

If you answer those four questions honestly, you'll land somewhere. And wherever you land, the important thing is that you landed there *on purpose*, not because a 525-point HN thread made the decision for you.

Your code is the most important thing you'll ever host — or hand over. It's worth deciding which one you're doing, and why.

---

*Where do you land on Origin vs self-hosted Git? I'm genuinely curious whether the AI-native pitch changes anyone's mind who was already leaning self-hosted — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like yesterday's post on [self-hosted Git](/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab), and my pieces on [self-hosted SSO](/blog/2026-08-08-self-hosted-auth-sso-showdown) and [Cloudflare Tunnels](/blog/2026-07-26-cloudflare-tunnels-homelab-guide).*
