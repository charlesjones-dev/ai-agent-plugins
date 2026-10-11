# AI-Slop Plugin

**AI slop audits and rewrites for Claude Code, Codex and Cursor.** Find what a codebase shows its users that reads as machine-made and what in it is wrong, or rewrite one piece of text so it reads as a person wrote it.

---

## What This Plugin Does

`/slop-audit` reads every surface a user sees: pages and shared layout, components and data files that carry copy, forms, emails, visible error text, legal pages, metadata, app strings and store listings, READMEs and `--help` output. It reports four kinds of problem:

- **Copy** that reads as AI-written: em dashes, "X, not Y" slogans, triplets, filler, inflated vocabulary, résumé voice
- **Layouts** that read as templates: the centered hero, icon grid and logo marquee stack, decorative badges, stock icon tiles, default AI palettes
- **Metadata** built from boilerplate: one tagline repeated across meta tags, JSON-LD, `llms.txt` and the manifest, or descriptions that promise content the site doesn't have
- **Errors**: a privacy policy that misses the fonts, analytics or pixels the code loads; prices, reply times or product lists that differ between pages; claims another page contradicts; links and components that lead nowhere

The audit changes nothing until you answer its questions.

`/slop-rewrite` works on one piece of text instead: a file, or text you paste after the command. It uses the same signal list.

## Available Skills

### `/slop-audit`

**How it works:**

1. Reads the project's own rules first (`CLAUDE.md`, `AGENTS.md`, an ai-knowledge knowledge base, voice or style docs, `DESIGN.md`), so it doesn't flag documented house style or re-ask questions an earlier audit settled
2. Lists every user-facing surface before reading, and splits large repos across parallel read-only subagents
3. Counts habits that repeat across the site, and how many files each appears in
4. Checks legal pages against the code and, given a live URL, against the scripts the live page loads
5. Scores each area from 0 to 100, quotes each finding with `file:line`, and gives a concrete fix for every one
6. Ends with a fix plan, the defaults it will use, and numbered questions you can answer in one reply

After you answer, it applies the fixes, removes the old wording from every metadata surface, regenerates OG images and updates legal effective dates where needed, runs the project's checks, and records your answers as project rules so later sessions don't bring the old copy back.

The signal checklist is [`signals.md`](skills/slop-audit/signals.md), shared with `/slop-rewrite`. Rules in the project override it.

The agent also runs the skill when you ask whether a site, app or README reads as AI-written.

**Usage:**

```
/slop-audit
/slop-audit skip the blog
/slop-audit only /about https://example.com
```

### `/slop-rewrite`

Rewrites one piece of text so it reads as a person wrote it. Point it at a file or glob, or paste the text right after the command. It works from the same [`signals.md`](skills/slop-rewrite/signals.md) as the audit, and reads the project's own writing rules first.

- **Content type** sets how much personality the rewrite allows: none for technical docs and PR or changelog text, a little for a README, and full voice for a blog post.
- **Level** sets how far it goes: `light` fixes clear tells only, `standard` fixes every signal and keeps the structure, and `heavy` rewrites freely.
- It asks for whatever the arguments leave out. Pasted text comes back as one block to copy. Files change only after you approve the edits.
- It never adds facts. A line that needs one, such as an unmeasured figure, comes back as a question.

It runs only when you call it.

**Usage:**

```
/slop-rewrite
/slop-rewrite README.md
/slop-rewrite type=blog level=standard docs/posts/launch.md
/slop-rewrite type=pr level=light
<paste the text on the lines after the command>
```

### Related plugins

- `/modernize-audit` ([ai-modernize](../ai-modernize/)) covers slop in the code itself: anti-patterns and technical debt left by older AI-generated code.

---

## Quick Start

### Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-slop@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-slop@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-slop`. See the [Cursor install steps](../../README.md#cursor).

---

## Plugin Details

- **Name:** AI-Slop Plugin
- **Type:** AI Instruction Plugin (Skills)
- **Skills:** `/slop-audit`, `/slop-rewrite`
- **Version:** 1.1.0
- **License:** MIT
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
