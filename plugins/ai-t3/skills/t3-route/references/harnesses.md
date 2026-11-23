# Harness profiles

A harness is the agent program that runs a T3 Code provider, such as Claude Code or the Grok CLI. Match a provider to its profile by the `driverKind` that `orchestrator_capabilities` reports. Each profile says which rules files the harness loads, how large they can be, and where the rules pointer goes.

If a provider's `driverKind` has no profile here, say "No harness profile for <displayName> (<driverKind>)". Don't guess a path, and don't write a pointer for it. Rank the provider's models with the warning that it may not load your rules.

## The rules pointer

Only Claude Code loads `~/.claude/CLAUDE.md`. Other harnesses never see it, so a thread on another provider misses every rule in it. A copy or a symlink doesn't help, because each harness cuts off a rules file at its size cap. The pointer is a short block that tells the model to read the file itself.

The current block, version 1:

```markdown
<!-- t3-route: rules pointer v1 -->
At the start of every session, read ~/.claude/CLAUDE.md in full and follow it.
In a repository, also read its CLAUDE.md and .claude/rules/ before you plan or edit.
Some rules name Claude Code tools. Where you lack that tool, follow the rule's intent with your own tools.
<!-- /t3-route -->
```

- The opening marker carries the version. A file that has `<!-- t3-route: rules pointer v` with a lower number has an old block. Replace the text from the opening marker through `<!-- /t3-route -->`, and nothing else.
- A file without the marker gets the block at its end, after one blank line.
- Never change text outside the markers. That text is the user's.
- Before you change an existing file, copy it to `~/.claude/model-router/backups/<driverKind>-<file name>-<YYYYMMDD-HHMMSS>`. A new file needs no backup.
- If the file plus the block would go over the harness's size cap, the harness cuts off the end, and the block sits at the end. Don't write it. Report the file, its size and the cap, and suggest the user shorten the file or move the block nearer the top by hand.

## Claude Code

- `driverKind`: `claudeAgent`
- Loads `~/.claude/CLAUDE.md`, the repository's `CLAUDE.md` files and `.claude/rules/` on its own.
- Pointer: none needed.
- Tools: Claude Code's own tools, its plugins and skills, and the MCP servers in its settings.

## Grok CLI

- `driverKind`: `grok`
- Global rules: the folder `~/.grok/`. It reads files named `Agents.md`, `Claude.md`, `AGENT.md` and `AGENTS.md`.
- Project rules: the same file names, in each folder from the repository root to the working folder. On a file system that ignores case, such as the macOS default, `Claude.md` also matches `CLAUDE.md`.
- Size cap: 10,000 characters per file. Grok cuts off the rest with a warning.
- Pointer file: the first of `~/.grok/AGENTS.md`, `~/.grok/AGENT.md`, `~/.grok/Claude.md` or `~/.grok/Agents.md` that exists. If none exists, create `~/.grok/AGENTS.md`. On a file system that ignores case, `AGENTS.md` and `Agents.md` are the same file.
- Tools: Grok also loads Claude Code skills and plugins, and the MCP servers in `~/.claude.json` and the project's `.mcp.json`. `grok inspect` lists what it loaded. In a T3 Code thread, it has T3 Code's tools with the prefix `t3-code__`.
- Source: `~/.grok/README.md`, the "AGENTS.md" and "Claude Code Compatibility" sections.

## Antigravity CLI

- `driverKind`: `antigravity`
- Project rules: `GEMINI.md` and `AGENTS.md` in each folder from the working folder up to the repository root, plus `.agents/rules/*.md`. It never reads `CLAUDE.md`.
- Global rules: Markdown files in `~/.gemini/config/rules/`. A file loads in every session only when its frontmatter has `trigger: always_on`.
- Size cap: 24,000 bytes per file. All always-on and global rules share a 20,000-token budget. Rules over that budget become file paths that the model may or may not open.
- Pointer file: `~/.gemini/config/rules/t3-route-rules-pointer.md`. The router owns this whole file, so write it with this frontmatter before the block:

  ```markdown
  ---
  trigger: always_on
  ---
  ```

- Tools: its own MCP servers in `~/.gemini/config/mcp_config.json`. It doesn't load Claude Code plugins unless the user installs one with `agy plugin install`.
- Source: the built-in `agy-customizations` skill under `~/.gemini/antigravity-cli/builtin/skills/`, its `docs/rules.md` page.

## Codex CLI

- `driverKind`: `codex`
- Global rules: `~/.codex/AGENTS.md`. Project rules: `AGENTS.md` from the repository root to the working folder. It never reads `CLAUDE.md`.
- Size cap: 32 KiB for all project rules together, by default (`project_doc_max_bytes`).
- Pointer file: `~/.codex/AGENTS.md`. Create it if it's missing.
- Tools: its own MCP servers in `~/.codex/config.toml`.
- Source: the Codex documentation on `AGENTS.md`.
