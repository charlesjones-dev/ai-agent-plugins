# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the `ai-agent-plugins` marketplace (GitHub: `charlesjones-dev/ai-agent-plugins`, renamed from `claude-code-plugins-dev` in 3.0.0). Every plugin runs in Claude Code, and the portable ones also run in Codex and Cursor. Each plugin is self-contained with its own metadata and skills.

## Official Documentation

Consult these before changing plugin structure or metadata:

1. **[Claude Code plugins](https://code.claude.com/docs/en/plugins)**, the **[marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)** and **[hosting a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace)**
2. **[Agent Plugins specification](https://agent-plugins.org/)** (root `plugin.json`, skills and MCP only) and the **[Agent Skills specification](https://agentskills.io/specification)** (`SKILL.md` format)
3. **[Codex plugins](https://learn.chatgpt.com/docs/plugins)** and **[Codex skills](https://learn.chatgpt.com/docs/build-skills)**
4. **[Cursor plugins](https://cursor.com/docs/plugins)** and **[Cursor skills](https://cursor.com/docs/skills)**

## Architecture

### Marketplace Structure

There are three catalogs, one per agent, all named `ai-agent-plugins`:

1. **`.claude-plugin/marketplace.json`** (Claude Code): lists all 13 plugins, plus a `renames` map for retired plugin names (`ai-writing` → `ai-slop`, `ai-aeo` and `ai-geo` → `ai-seo`, `ai-cvp` → `ai-security`). Treat `renames` as append-only history. Codex also falls back to this file when its own catalog is missing, so the Codex catalog must stay in place.
2. **`.agents/plugins/marketplace.json`** (Codex): lists only the portable plugins. Each entry needs `source` (`{"source": "local", "path": "./plugins/{name}"}`), `policy.installation`, `policy.authentication` and `category`.
3. **`.cursor-plugin/marketplace.json`** (Cursor): lists only the portable plugins, with `source: "plugins/{name}"`, `description` and `version`.

Each plugin has a Claude Code manifest at `plugins/{plugin-name}/.claude-plugin/plugin.json`. Portable plugins also have an Agent Plugins 1.0 manifest at `plugins/{plugin-name}/plugin.json`, which Codex and Cursor read first and Claude Code ignores. Its schema is closed: only `$schema`, `name`, `version`, `description`, `author` (`name`/`email`/`url`), `homepage`, `repository`, `license`, `keywords` and `extensions`.

`python3 scripts/check-manifests.py` checks that all of these agree. Run it after any manifest, catalog or skill frontmatter change.

`python3 scripts/test-statusline.py` runs ai-statusline's Bash and PowerShell templates (the fenced blocks in `statusline-wizard/SKILL.md`) against sample payloads. Run it after changing either template. It skips the PowerShell cases when `pwsh` isn't installed.

### Plugin Organization

Plugins are organized under the `plugins/` directory:
```
plugins/
  {plugin-name}/
    .claude-plugin/
      plugin.json          # Claude Code manifest
    plugin.json            # Agent Plugins manifest (portable plugins only)
    skills/
      {skill-name}/
        SKILL.md           # Skill implementation
        agents/
          openai.yaml      # Codex policy; required when disable-model-invocation is true
    agents/                # Optional Claude Code subagents
      {agent-name}.md      # Subagent definition
```

### Portable and Claude Code-only Plugins

Portable (in all three catalogs): ai-accessibility, ai-compliance, ai-git, ai-modernize, ai-performance, ai-seo, ai-slop, ai-swift.

Claude Code-only: ai-security (`/security-init` writes Claude Code settings, `/security-audit` fans out to `security-auditor` subagents, and `/security-cvp-audit` uses `${CLAUDE_SKILL_DIR}`), ai-ado (stores config in CLAUDE.md), ai-knowledge (stores its knowledge base as Claude Code rules in `.claude/rules/`, and ships a SessionStart hook for auto-capture), ai-workflow (`/workflow-babysit` depends on Claude Code review and `/code-review`, and `/workflow-rules` edits CLAUDE.md) and ai-statusline (configures Claude Code's status line).

Before adding a plugin to the Codex and Cursor catalogs, check that its skills don't depend on Claude Code subagents, hooks, settings files, `${CLAUDE_PLUGIN_ROOT}`/`${CLAUDE_SKILL_DIR}`, or CLAUDE.md. Agent Plugins v1 covers only skills and MCP servers.

Supported agents are Claude Code, Codex and Cursor. Don't add catalogs, manifests or docs for VS Code or GitHub Copilot; the owner doesn't want to support them. (Both read `.claude-plugin/marketplace.json` on their own, which is fine.)

### Invocation Control Across Agents

- **Claude Code** and **Cursor** both honor `disable-model-invocation: true` in `SKILL.md` frontmatter.
- **Codex** ignores that field. A skill with it must also have `skills/{skill-name}/agents/openai.yaml` containing `policy:` / `allow_implicit_invocation: false`, or Codex can start the skill unprompted. Skills Claude may invoke (no `disable-model-invocation`) must not have the file. The check script enforces both.
- Codex names plugin skills `{plugin-name}:{skill-name}` and users run them with `$` or `/skills`.

### Plugin Types

Plugins can include:
- **Skills**: Markdown files in `skills/{skill-name}/SKILL.md` directories that define executable skills invoked as slash commands
- **Agents**: Markdown files in `agents/{agent-name}.md` that define Claude Code subagents. Only add one for a distinct worker role with its own instructions, such as `security-auditor`, which `/security-audit` runs in parallel. Never write an agent whose job is to load one of the plugin's skills: a skill with `disable-model-invocation: true` can't be loaded through the Skill tool, so the agent never sees its instructions. Five such wrapper agents were removed in 3.0.0 for this reason. For unattended runs, let the skill take its settings as arguments; for an isolated context in Claude Code, use the skill's `context: fork` setting. Agents should use `model: inherit` rather than hardcoding a model ID, and skills that delegate to an agent must reference one that actually ships with the plugin (`{plugin-name}:{agent-name}`)
- Each skill is a markdown file with instructions for Claude Code to execute

## Development Workflow

### Recommended Setup

Before developing plugins in this repository, it's recommended to:

1. **Initialize security settings** using the ai-security plugin:
   ```bash
   /security-init
   ```
   This configures `.claude/settings.json` to prevent Claude Code from reading sensitive files (credentials, secrets, build artifacts, etc.) based on your project's technology stack.

   **Important**: Restart Claude Code after running this command for the settings to take effect.

### Adding a New Plugin

1. Create the plugin directory structure under `plugins/{plugin-name}/`
2. Add plugin metadata in `.claude-plugin/plugin.json` with:
   - name, version, description
   - author information
   - keywords for discoverability
   - repository and license
3. Implement skills in the `skills/{skill-name}/SKILL.md` directory structure. Each skill's frontmatter `name` must match its folder name
4. Register the plugin in the root `.claude-plugin/marketplace.json`
5. If the plugin is portable (see above), add a root `plugin.json` and list it in `.agents/plugins/marketplace.json` and `.cursor-plugin/marketplace.json`
6. Add `agents/openai.yaml` to every skill with `disable-model-invocation: true`, then run `python3 scripts/check-manifests.py`

### Skill Development

Skills are markdown files located at `skills/{skill-name}/SKILL.md` that provide instructions to Claude Code. They should:
- Have a clear title and description
- Include step-by-step instructions under an "## Instructions" section
- Specify any important constraints or requirements (e.g., what NOT to include in outputs)
- Never tell the agent to run another command-only skill (`disable-model-invocation: true`). Claude Code can't load one through the Skill tool, so tell the user which command to type instead. A skill can run a skill Claude may invoke, as `/git-commit-push-pr --preflight` runs `git-preflight`

Example from the git-commit-push-pr skill (plugins/ai-git/skills/git-commit-push-pr/SKILL.md):
```
4. Add no AI attribution to the commit: no `Co-Authored-By` trailer, no "Generated with" line, and nothing else that credits Claude, Codex, Cursor or another agent.
```

## Key Conventions

### Git Commit Messages

This repository has specific requirements for git commit messages:
- Follow the repository's existing commit message style (check recent commits with `git log`)
- Use conventional commit prefixes if the repository uses them (fix:, feat:, docs:, etc.)
- Do NOT include Claude Code attribution or co-author tags

### Plugin Metadata

When creating or updating plugins, ensure consistency between:
1. The plugin's own `.claude-plugin/plugin.json` file
2. Its entry in `.claude-plugin/marketplace.json`
3. For portable plugins, the root `plugin.json` and the entry in `.cursor-plugin/marketplace.json`

These should have matching:
- name
- version
- description
- author information
- keywords and repository (Claude Code catalog and both manifests)

`python3 scripts/check-manifests.py` reports any mismatch.

### Plugin Versioning

This repository follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
- **MAJOR** (x.0.0): Breaking changes or incompatible API changes
- **MINOR** (0.x.0): New features added in a backward-compatible manner
- **PATCH** (0.0.x): Backward-compatible bug fixes

#### Updating Plugin Versions

When adding new features or fixing bugs in a plugin, follow this workflow:

1. **Update Plugin Metadata** (`plugins/{plugin-name}/.claude-plugin/plugin.json`, plus the root `plugin.json` for portable plugins):
   - Increment version number appropriately
   - Update description if the functionality changed significantly

2. **Update Marketplace Registry** (`.claude-plugin/marketplace.json`, plus `.cursor-plugin/marketplace.json` for portable plugins):
   - Update the plugin's version in the plugins array
   - Update the plugin's description to match plugin.json
   - Increment marketplace metadata version if this is a significant update, in both catalogs
   - Run `python3 scripts/check-manifests.py`

3. **Update CHANGELOG.md**:
   - Add a new version section with the release date
   - Document all added, changed, deprecated, removed, fixed, or security-related changes
   - Follow Keep a Changelog format
   - Update version comparison links at the bottom

4. **Update README.md**:
   - Update the marketplace version in the badge at the top (e.g., `version-2.0.1-blue`)
   - Add any new commands to the Commands column, and keep the "Runs in" column accurate
   - Update usage examples if new commands were added

5. **Update Plugin README** (`plugins/{plugin-name}/README.md`):
   - Document new features, skills, or agents
   - Update version in Plugin Details section
   - Add usage examples for new functionality

**Example:** When ai-security plugin added `/security-init` command:
- Plugin version: 1.0.0 → 1.1.0 (new feature = minor bump)
- Marketplace version: 1.0.1 → 1.1.0 (significant update)
- Updated all the files listed above to maintain consistency

### Documentation Style

These rules came from an AI slop audit (October 2026). They apply to READMEs, manifest descriptions, and skill and agent descriptions:

- Open plugin descriptions and README taglines with what the plugin does. Don't write "AI-powered" (every plugin name already starts with `ai-`) or use the "Noun phrase - Clause" shape.
- No emoji in headings. Functional markers are fine: 🧪 experimental flags in ai-seo's AEO and GEO material, 🗑️ status in the Deprecated & Removed table, and icons that appear in real program output.
- No unmeasured figures: no "Time Savings" sections, estimated hours saved, or percentages nobody measured.
- No roadmaps of skills that don't exist.
- No slogan closers such as "Built with ❤️ for the Claude Code community". A plugin README's Contributing section is one line: "Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md)."
- Contributions are issues and fix PRs only. New plugins, skills and features start as an issue.
- Examples in skills and docs must be generic. Don't quote the owner's sites, clients, products or business details.
- Avoid em dashes in README prose. CHANGELOG entries keep their "**Name** — description" lead-ins.
- Cut "comprehensive", "intelligent", "professional" and "streamline" unless the sentence needs them.
- Before a release that changes docs, run `/slop-audit` from the ai-slop plugin.

### Third-party Material

When a plugin adapts someone else's skills, scripts or docs, as ai-workflow and ai-git do with Theo Browne's [tstack](https://github.com/t3dotgg/tstack) (MIT):

1. Check that the source's license allows it, and keep its copyright and permission notice. Ship `plugins/{plugin-name}/THIRD-PARTY-NOTICES.md` with the full license text, the source URL and commit, and a table of the adapted files. Plugins install one at a time, so the notice must sit inside the plugin's own folder.
2. End each adapted `SKILL.md` with a credit line that names the source, its author and its license, and points to `THIRD-PARTY-NOTICES.md`.
3. Keep the copyright header in an adapted script, and add a line on what changed.
4. Credit the source in the plugin README's Credits section, the root README's Credits section and the CHANGELOG entry.

### Deprecating or Removing Plugins and Skills

When Claude Code ships a native feature that supersedes a plugin or skill (e.g., native Dynamic Workflows superseded `/workflow-plan-phases`, the native Learning output style superseded ai-learn):

1. **Prefer removal over deprecation notices for skills** — a deprecated skill still appears in users' slash-command dropdowns; git history preserves the content
2. **Removing a skill is a breaking change**: MAJOR version bump for the plugin (e.g., ai-workflow 1.5.0 → 2.0.0)
3. **Removing an entire plugin**: delete its directory and its entry in each catalog (`.claude-plugin/`, `.agents/plugins/` and `.cursor-plugin/`), and add its name to the Claude Code catalog's `renames` map, pointing at the plugin that replaces it or at `null`. Claude Code then rewrites users' enabled setting, but a replacement plugin still needs one `/plugin install`, so say that in the README
4. **Record it in the root README's "Deprecated & Removed" table** with a dated status (e.g., "Removed (July 2026)") and the native feature that supersedes it — use concrete dates, not "recently"
5. **Document in CHANGELOG.md** under a "Removed" heading
6. **Add it to the command map**: every renamed, merged or removed command, plugin name or report folder gets a row in `plugins/ai-knowledge/skills/kb-migrate/command-map.md` (`Old | New | Kind | Notes`, with Kind `rename`, `changed` or `removed`). `/kb-migrate` uses it to fix knowledge bases and project docs that still name the old command, and the check script confirms that every plugin command in the New column exists
7. When a plugin is only *partially* superseded, reframe its README and manifest description against the native feature (state what the plugin adds on top) instead of deprecating it
