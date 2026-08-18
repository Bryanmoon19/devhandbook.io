---
layout: post.njk
title: "Your AI Wrote It. Who's Reviewing It? The Human-Oversight Stack for AI-Generated Code"
date: 2026-08-18
description: "Copilot Autofix allowed a compromise of Snowflake's Jira, and a growing wave of developers are quietly going back to hand-written code. The problem isn't AI code quality — it's that nobody built the review layer. Here's a practical checklist and tool stack for actually reviewing AI-generated code before it ships."
tags: ["ai", "code-review", "security", "copilot", "cursor", "claude-code", "codex", "developer-tools", "oversight", "trust", "supply-chain"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ai-code-review-checklist"
---

Two stories hit the front page of Hacker News this week, and together they tell you exactly where the AI coding wave is heading.

The first: **"Copilot Autofix Allowed Compromise of Snowflake's Jira"** — 339 points. The short version is that GitHub's Copilot Autofix, the feature that automatically generates and applies security fixes, was used to *introduce* a vulnerability that led to a real compromise. The tool that was supposed to make code safer made it less safe, and nobody caught it until it was too late.

The second: **"went back to hand-written code?"** — 104 points. A thread full of developers who tried AI coding assistants, got burned by subtle bugs and unmaintainable output, and quietly went back to typing everything themselves.

I've spent the last few months writing about the *cost* of AI coding — the [hidden costs deep-dive](/blog/2026-08-09-hidden-costs-ai-coding-agents/), the [cost-tracking tools comparison](/blog/2026-08-12-ai-coding-agent-cost-tracking-tools/), the [6-week explosion of budget trackers](/blog/2026-08-13-ai-coding-agent-cost-tracking-tools-compared/). But cost was always the wrong frame. The real problem isn't what AI code *costs*. It's whether you can *trust* it.

And right now, most teams can't — not because the models are bad, but because **nobody built the review layer.** We automated the writing. We forgot to automate — or even systematize — the checking.

This post is the missing piece. A practical, opinionated checklist and tool stack for reviewing AI-generated code before it ships. Not "be careful." Not "use your judgment." An actual process you can run today.

## The Trust Gap, in One Paragraph

Here's the uncomfortable truth about AI-generated code: **it looks right, and that's the problem.**

Human code has tells. A junior dev's code has a certain shape — the awkward variable names, the slightly-off indentation, the comment that doesn't quite match the logic. Your brain flags it as "needs a closer look" without you thinking about it.

AI code doesn't have those tells. It's *too* clean. The variable names are perfect. The comments are helpful. The structure is idiomatic. It reads like the answer key, which means your normal review instincts go quiet. You skim it, nod, and merge — and that's exactly when the subtle bug slips through.

The Snowflake incident is the canonical example. Copilot Autofix produced a fix that *looked* correct — it passed the tests, it satisfied the linter, it addressed the reported issue. But it also introduced a new vulnerability, and because the fix came from a trusted tool with a green checkmark, nobody looked hard enough to see it.

The trust gap is this: **AI code gets the same level of scrutiny as code that's already been reviewed, when it actually needs *more* scrutiny than a first draft.** It's not that AI writes worse code than humans. It's that we've built a pipeline that treats AI output as finished work, and it isn't.

## Why "Just Review It Like Normal Code" Fails

The most common advice I see is: "AI code is just code. Review it like you'd review any other PR."

That's wrong, for three specific reasons.

### 1. Volume

A human developer writes maybe 200-500 lines of meaningful code in a good day. An AI coding agent can produce 2,000-5,000 lines in an afternoon. The review bandwidth doesn't scale. If you review AI output at the same *rate* as human output, you're reviewing a fraction of it — and the fraction you skip is where the bugs live.

### 2. Confidence Calibration

AI models are confidently wrong. A human who's unsure will hedge, ask questions, leave a `// TODO: verify this`. An AI will assert the wrong thing with the same confidence as the right thing. There's no signal in the output that says "this part is shaky." You have to *manufacture* that signal yourself.

### 3. The "It Passed the Tests" Trap

AI coding agents are trained to make tests pass. That's their objective function, and they're very good at it. But "passes the tests" and "is correct" are different things — the tests only cover what you thought to test, and the AI is optimizing for exactly that. The Snowflake bug passed the tests. The tests were the problem.

So the review process for AI code has to be *different* — not just more of the same. It has to compensate for volume, for false confidence, and for the test-passing trap.

## The Checklist: What to Actually Check

Here's the checklist I use. It's ordered by how likely each category is to hide a real bug in AI-generated code. Run it top to bottom, and don't skip the first three.

### 1. Security-Sensitive Changes (Non-Negotiable)

This is the Snowflake lesson. Any AI-generated change that touches security-sensitive code gets *manual* review, no exceptions, no matter how small.

**What counts as security-sensitive:**

- Authentication and authorization logic
- Input validation and sanitization
- SQL queries (especially anything dynamic)
- File paths and file operations
- Network requests and URL handling
- Anything touching secrets, tokens, or credentials
- Dependency changes (new packages, version bumps)
- Configuration that affects permissions or exposure

**The rule:** If the diff touches any of these, a human reads every line. Not skims — reads. The AI's "fix" for a security issue is the single most dangerous thing it produces, because it's optimized to *look* like a fix, not to *be* one.

### 2. The "Why" Behind Every Change

AI code is often correct in isolation and wrong in context. The model doesn't know your codebase's invariants, your team's conventions, or the reason that weird-looking function exists.

**For every non-trivial change, ask:**

- Why was this change made? (Can you articulate it in one sentence?)
- What assumption is this code making about the surrounding system?
- Does this change break any invariant the rest of the code relies on?
- Is there a simpler change that would accomplish the same thing?

If you can't answer "why" for a change, that's a red flag — either the change is unnecessary, or you don't understand it well enough to ship it.

### 3. The Test-Passing Trap

AI agents optimize for green tests. So you have to ask what the tests *don't* cover.

**Check:**

- Does the test actually assert the right thing, or just that the code ran?
- Are there edge cases the test doesn't cover that the change might affect?
- Did the AI *modify the test* to make it pass? (This is a huge red flag — check the test diff separately.)
- Is there a test for the *failure mode*, not just the happy path?

The Snowflake bug passed the tests because the tests didn't cover the vulnerability the fix introduced. The fix *was* the vulnerability. No test suite catches that unless you're specifically looking for it.

### 4. Dependency and Supply-Chain Changes

AI agents love to add dependencies. A new package is a one-line fix for a problem that would take twenty lines to solve by hand, and the model doesn't feel the supply-chain risk.

**Check every dependency change:**

- Is the package actively maintained? (Last commit, open issues, download count)
- What's its own dependency tree? (A "tiny" package can pull in 50 transitive deps)
- Does it have the permissions it claims to need?
- Is there a way to do this without the new dependency?

This connects directly to my [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface) post — the supply chain is where a lot of the real risk lives, and AI agents are *more* likely to introduce it, not less.

### 5. The "Looks Right" Trap

This is the subtle one. AI code is aesthetically perfect, and that perfection is a *liability* — it disarms your review instincts.

**Deliberately look for:**

- Off-by-one errors in loops and bounds
- Integer overflow and truncation
- Race conditions in concurrent code
- Error handling that swallows exceptions silently
- Null/undefined handling that's missing
- Timezone, locale, and encoding edge cases

These are the bugs that survive because the code *looks* too clean to contain them. Force yourself to look for them specifically.

### 6. Maintainability and "AI Smell"

AI code has a signature. It's not always bad, but you should recognize it and decide consciously whether to accept it.

**AI smell includes:**

- Overly generic variable names (`data`, `result`, `temp`, `item`)
- Functions that do too much (no clear single responsibility)
- Comments that restate the code instead of explaining the why
- Over-engineering — abstractions for problems that don't exist yet
- Inconsistent patterns across the codebase (the AI doesn't know your conventions)

None of these are bugs by themselves. But they compound — AI code that's merged without cleanup becomes a codebase that's harder for *humans* to maintain, which is exactly the "went back to hand-written code" complaint.

## The Tool Stack: Automating What You Can

The checklist is the manual layer. But you can automate a surprising amount of it, and you should — because the volume problem is real, and tools don't get tired.

Here's the stack I recommend, in order of adoption difficulty.

### Tier 1: The Free, Immediate Wins

These take minutes to set up and catch a real fraction of AI-code bugs.

**1. A second model as reviewer.** The single highest-leverage trick. Run your AI-generated diff through a *different* model and ask it to find bugs. Different models have different blind spots, and a second pass catches a surprising amount. This is the "two doctors" principle — you don't need the second opinion to be better, just *different*.

```bash
# Example: pipe a diff to a second model for review
git diff main | claude -p "Review this diff for bugs, security issues, and edge cases. Be specific. Flag anything that looks correct but isn't."
```

**2. Static analysis with security rules.** `semgrep`, `bandit` (Python), `gosec` (Go), `eslint` with security plugins (JS). These catch the mechanical security issues — SQL injection, path traversal, hardcoded secrets — that AI code is just as likely to introduce as human code, but that nobody's eyeballs will catch at 5,000 lines a day.

**3. Dependency scanners.** `npm audit`, `pip-audit`, `cargo audit`, `osv-scanner`. Run them on every AI-generated PR. The AI added a dependency; the scanner tells you if it's a known-bad one.

### Tier 2: The CI-Integrated Layer

Once you have the basics, wire them into CI so they run automatically on every PR — including the AI-generated ones.

**4. A dedicated AI-review bot in CI.** Tools like **CodeRabbit**, **Greptile**, or a self-hosted reviewer that runs a model against every PR. The key is to treat its output as *triage*, not *verdict* — it flags suspicious code for a human to look at, it doesn't approve anything.

**5. Test coverage gates with mutation testing.** This is the anti-test-passing-trap tool. Mutation testing (like `stryker` or `mutmut`) deliberately introduces bugs into your code and checks whether your tests catch them. If your tests don't catch the mutations, they won't catch the AI's subtle bugs either. A low mutation score on an AI-generated PR is a red flag.

**6. Diff-size limits.** A blunt but effective tool. Cap AI-generated PRs at a size a human can actually review (say, 400-800 lines). If the AI produced 3,000 lines, split it into multiple PRs. This forces the volume problem to be addressed structurally instead of by skimming.

### Tier 3: The Process Layer

Tools can't fix everything. Some of this is just process discipline.

**7. The "AI-generated" label.** Mark AI-generated PRs explicitly. This isn't about shame — it's about *calibrating review*. A reviewer who knows the code came from an AI reviews it differently (more skeptically, more edge-case-focused) than one who assumes it's a colleague's work. The label is a signal that changes the review posture.

**8. Human sign-off on security-sensitive changes.** No automation, no AI reviewer, no "it passed CI" — a human reads every line of any change touching auth, input validation, SQL, file paths, or secrets. This is the Snowflake rule, and it's non-negotiable.

**9. A "why" comment on every non-trivial change.** Require the AI (or the developer using it) to attach a one-line explanation of *why* each change was made. If the "why" can't be articulated, the change doesn't ship. This catches the "AI did something unnecessary but plausible-looking" failure mode.

## The Snowflake Lesson, Applied

Let me make the Snowflake incident concrete, because it's the perfect case study for why this stack matters.

The failure wasn't that Copilot Autofix produced bad code. It's that the *pipeline* treated the fix as trustworthy:

1. **The fix came from a trusted tool** (GitHub's own security feature), so it got a lower review bar than a human's fix would have.
2. **The fix passed the tests**, so the test-passing trap kicked in — nobody asked what the tests *didn't* cover.
3. **The fix touched security-sensitive code** (it was a security fix, by definition), but it didn't get the manual, line-by-line review that security-sensitive changes require.
4. **The fix looked right** — it was clean, idiomatic, and addressed the reported issue — so the "looks right" trap disarmed the reviewers.

Every single layer of the stack I described above would have caught it. A second model reviewing the diff. A security rule in the static analysis. A human reading the security-sensitive change line by line. A "why" comment explaining what the fix actually did and what it assumed.

The point isn't that Copilot Autofix is bad. It's that **no single tool — human or AI — is sufficient on its own.** The fix is the *stack*: multiple independent checks, each catching what the others miss.

## The "Went Back to Hand-Written Code" Crowd

The second HN thread is worth addressing directly, because it's the other failure mode.

Some developers tried AI coding, got burned by subtle bugs and unmaintainable output, and concluded the answer is to *stop using AI*. That's an overcorrection. The problem wasn't the AI — it was that they used the AI *without the review layer*. They treated AI output as finished code, merged it, and paid the price in debugging time and maintenance burden.

The developers who are *happy* with AI coding aren't the ones who type less. They're the ones who **type less but review more.** They use the AI for the boilerplate, the scaffolding, the tedious 80% — and they apply the checklist and the tool stack to the result. They treat AI output as a *first draft*, not a *final answer*.

That's the mindset shift. AI coding isn't "write less code." It's "write code faster, and spend the saved time reviewing it properly." If you're not doing the second half, you're not getting the benefit — you're just moving the bugs around.

## The Bottom Line

The AI coding wave has a trust problem, and it's not going to be solved by better models. It's going to be solved by better *process*.

The models will keep getting better at writing code. But they'll also keep getting better at writing code that *looks* right and isn't — because that's the same skill. The gap between "looks correct" and "is correct" is where the bugs live, and no amount of model improvement closes it. Only review does.

So here's the stack, compressed to a card you can stick on your monitor:

1. **Security-sensitive changes get manual, line-by-line review. Always.**
2. **Run every AI diff through a second model.**
3. **Static analysis + dependency scanning on every AI PR.**
4. **Mutation testing to catch the test-passing trap.**
5. **Cap diff size so a human can actually review it.**
6. **Label AI-generated PRs to calibrate review posture.**
7. **Require a "why" for every non-trivial change.**

The developers who thrive in the AI-coding era won't be the ones who type the least. They'll be the ones who build the best review layer. Because when your AI writes the code, *you* are the one who has to answer for it.

---

*How are you reviewing AI-generated code? Have you been burned by a "looks right but isn't" bug? I'd love to hear your process — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [AI coding agent cost tracking](/blog/2026-08-12-ai-coding-agent-cost-tracking-tools/), the [hidden costs of AI coding agents](/blog/2026-08-09-hidden-costs-ai-coding-agents/), and the [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface/).*
