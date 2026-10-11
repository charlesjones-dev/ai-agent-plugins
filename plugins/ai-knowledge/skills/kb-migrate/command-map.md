# Command map

Every command, skill, subagent, plugin, marketplace name and report path from the ai-agent-plugins marketplace (formerly claude-code-plugins-dev) that was renamed, merged or removed, built from the marketplace's CHANGELOG and README. `/kb-migrate` uses it to find stale references in a project's notes.

## Format

The table below keeps this format, so a script can check it:

- One Markdown table with the header `| Old | New | Kind | Notes |`.
- Items in Old and New are in backticks and separated by commas.
- A marketplace command is written in full as `/plugin:skill`, followed by any arguments inside the same backticks.
- A Claude Code built-in has no plugin prefix and is followed by `(built-in)` after its closing backtick, or is plain text ending in `(built-in)`.
- Kind is one of:
  - `rename`: swap old for new, one to one;
  - `changed`: the replacement needs arguments or works differently;
  - `removed`: no plugin replacement. New names the built-in alternative, except for `/kb-auto`, which ai-knowledge's auto-capture replaces.

## How to match

- A command row such as `/ai-writing:writing-humanize` matches all the ways people write it: `/writing-humanize`, `/ai-writing:writing-humanize`, Codex's `$ai-writing:writing-humanize`, `ai-writing:writing-humanize`, and the bare name `writing-humanize` when it's in backticks or next to "skill", "command" or "subagent". Write the replacement in the same form: `/slop-rewrite`, `/ai-slop:slop-rewrite`, `$ai-slop:slop-rewrite` or `slop-rewrite`, keeping New's arguments. New always carries the plugin prefix so it can be checked; when the old text had no prefix, leave it off the replacement too (`/modernize-scan src` becomes `/modernize-audit src --defaults`).
- A name never matches inside a longer name: `/git-commit-push` doesn't match `/git-commit-push-pr`, and `/preflight` doesn't match `/git-preflight`.
- `learn`, `learn-review`, `ship` and `preflight` are ordinary words, so they match only with a leading `/` or `$` or a plugin prefix.
- Plugin names match as whole words, in install IDs (`ai-geo@claude-code-plugins-dev`) and in `plugins/<name>/` paths.
- Paths match where they name a folder or file pattern. A link to a specific report that already exists stays as it is, because old reports stay in the old folder.
- Leave history alone: statements about what happened on a past date ("On 2026-05-01 we ran /geo-audit"), log entries, changelogs, release notes, and sentences that describe the rename itself.

## Map

| Old | New | Kind | Notes |
|---|---|---|---|
| `@claude-code-plugins-dev` | `@ai-agent-plugins` | rename | Marketplace renamed in 3.0.0. Applies to install IDs such as `ai-git@claude-code-plugins-dev`. Leave the migration step `/plugin marketplace remove claude-code-plugins-dev` as it is |
| `charlesjones-dev/claude-code-plugins-dev` | `charlesjones-dev/ai-agent-plugins` | rename | Repository renamed in 3.0.0, in `/plugin marketplace add`, `codex plugin marketplace add` and GitHub URLs. GitHub redirects the old URL |
| `ai-writing` | `ai-slop` | rename | Plugin merged into ai-slop in 3.0.0. Users install ai-slop once |
| `ai-aeo`, `ai-geo` | `ai-seo` | rename | Plugins merged into ai-seo in 3.0.0. Users install ai-seo once |
| `ai-cvp` | `ai-security` | rename | Plugin merged into ai-security in 3.0.0. Users install ai-security once |
| `ai-learn` | Learning output style: `/config` (built-in) | removed | Plugin removed in July 2026. In `/config`, set "Output style" to "Learning" |
| `ai-plugins` | ask Claude Code to create the plugin (built-in) | removed | Plugin removed in 2.0.0 because Claude Code handles plugin creation natively |
| `accessibility-auditing` | `/ai-accessibility:accessibility-audit` | rename | Skill name before 2.0.0 |
| `accessibility-auditor` | `/ai-accessibility:accessibility-audit` | changed | Subagent removed in 3.0.0. The skill runs the audit itself and takes `[WCAG version] [level] [path or URL]` |
| `/ai-ado:ado-create-feature` | `/ai-ado:ado-create feature` | changed | Merged into `/ado-create` in 3.0.0 |
| `/ai-ado:ado-create-story` | `/ai-ado:ado-create story` | changed | Merged into `/ado-create` in 3.0.0 |
| `/ai-ado:ado-create-task` | `/ai-ado:ado-create task` | changed | Merged into `/ado-create` in 3.0.0 |
| `/ai-ado:ado-work-items` | `/ai-ado:ado-create` | changed | Its guidelines moved into `/ado-create` in 3.0.0. It never loaded by itself; running `/ado-init` rewrites a CLAUDE.md section that says it does |
| `/ai-git:git-commit-push`, `/ai-git:commit-push` | `/ai-git:git-commit-push-pr --no-pr` | changed | `/commit-push` became `/git-commit-push` in 1.2.0, then `/git-commit-push-pr --no-pr` in 3.0.0 |
| `/ai-git:git-pr-codex-loop` | `/code-review --fix` (built-in), `/autofix-pr` (built-in) | removed | Removed in 3.0.0. Both loop on review comments and CI failures. `/workflow-babysit` still triages Codex Code Review findings |
| `/ai-knowledge:kb-ingest`, `/ai-knowledge:kb-import` | `/ai-knowledge:kb-add <path>` | changed | Merged into `/kb-add` in 3.0.0. Nothing needs registering any more; a path inside the knowledge base checks a hand-added article |
| `/ai-knowledge:kb-harvest` | `/ai-knowledge:kb-add <path, glob or URL>` | changed | Merged into `/kb-add` in 3.0.0, with provenance kept in `source` |
| `/ai-knowledge:kb-absorb` | `/ai-knowledge:kb-add --absorb` | changed | Merged into `/kb-add` in 3.0.0 |
| `/ai-knowledge:kb-search` | `/ai-knowledge:kb-query search <terms>` | changed | Merged into `/kb-query` in 3.0.0. Tag search is `/kb-query tag:<tag>` |
| `/ai-knowledge:kb-list` | `/ai-knowledge:kb-query list` | changed | Merged into `/kb-query` in 3.0.0 |
| `/ai-knowledge:kb-organize` | `/ai-knowledge:kb-prune organize` | changed | Merged into `/kb-prune` in 3.0.0 |
| `/ai-knowledge:kb-remove` | `/ai-knowledge:kb-prune remove <article>` | changed | Merged into `/kb-prune` in 3.0.0 |
| `/ai-knowledge:kb-upgrade` | `/ai-knowledge:kb-migrate` | rename | Replaced in 3.0.0. `/kb-migrate` also checks a migrated knowledge base |
| `/ai-knowledge:kb-obsidian` | `/ai-knowledge:kb-migrate` | changed | Absorbed into `/kb-upgrade` in 2.3.4. Obsidian support was removed in 3.0.0 |
| `/ai-knowledge:kb-auto` | auto-capture: `/ai-knowledge:kb-init auto=on` | removed | Removed in 3.0.0. Auto-capture saves team knowledge as it comes up and is on unless turned off with `auto=off` |
| `/ai-knowledge:kb-load` | @-mention the article (built-in) | removed | Removed in 3.0.0. Scoped and pinned articles load by themselves as rules. In CLAUDE.md or a rule, write an example mention in backticks, because a bare `@path` there is an import that loads the file every session |
| `/ai-modernize:modernize-scan` | `/ai-modernize:modernize-audit <path> --defaults` | changed | Removed in 3.0.0. `--defaults` runs without questions |
| `modernize-auditor` | `/ai-modernize:modernize-audit` | changed | Subagent removed in 3.0.0. The skill runs the audit itself |
| `performance-auditing` | `/ai-performance:performance-audit` | rename | Skill name before 2.0.0 |
| `performance-auditor`, `performance-optimizer` | `/ai-performance:performance-audit` | changed | Subagent removed in 3.0.0 (it was `performance-optimizer` before 1.5.0). The skill runs the audit itself and takes `[path]` |
| `/ai-cvp:cvp-defense-audit` | `/ai-security:security-cvp-audit` | rename | Moved into ai-security in 3.0.0 |
| `security-auditing` | `/ai-security:security-audit` | rename | Skill name before 2.0.0 |
| `security-dependency-scanning` | `/ai-security:security-scan-dependencies` | rename | Skill name before 2.0.0 |
| `security-dependency-scanner` | `/ai-security:security-scan-dependencies` | changed | Subagent removed in 3.0.0. The skill runs the scan itself and takes `[URL] [frontend, cms, headers or all]` |
| `/ai-aeo:aeo-audit` | `/ai-seo:seo-audit aeo` | changed | Merged into `/seo-audit` in 3.0.0. `/seo-audit` with no lens audits SEO, AEO and GEO |
| `/ai-geo:geo-audit` | `/ai-seo:seo-audit geo` | changed | Merged into `/seo-audit` in 3.0.0. `/seo-audit` with no lens audits SEO, AEO and GEO |
| `/ai-aeo:aeo-fix`, `/ai-geo:geo-fix` | `/ai-seo:seo-fix` | rename | Merged into `/seo-fix` in 3.0.0. It applies the newest report for each lens; pass a report path to apply an older AEO or GEO report |
| `/ai-aeo:aeo-faq` | `/ai-seo:seo-faq` | rename | Moved into ai-seo in 3.0.0 |
| `/ai-aeo:aeo-questions` | `/ai-seo:seo-questions` | rename | Moved into ai-seo in 3.0.0 |
| `/ai-geo:geo-llms-txt` | `/ai-seo:seo-llms-txt` | rename | Moved into ai-seo in 3.0.0 |
| `/ai-writing:writing-humanize` | `/ai-slop:slop-rewrite` | rename | Moved into ai-slop in 3.0.0. `type=docs`, `readme`, `blog` or `pr` and `level=light`, `standard` or `heavy` skip its questions |
| `swift-release-auditor` | `/ai-swift:swift-preflight --check-only` | changed | Subagent removed in 3.0.0 |
| `/ai-workflow:workflow-preflight`, `/ai-workflow:preflight` | `/ai-git:git-preflight` | rename | `/preflight` became `/workflow-preflight` in 1.6.1, then moved to ai-git as `/git-preflight` in 3.0.0. Users install ai-git |
| `/ai-workflow:workflow-ship`, `/ai-workflow:ship` | `/ai-git:git-commit-push-pr --preflight` | changed | `/ship` became `/workflow-ship` in 2.0.0, then `/git-commit-push-pr --preflight` in ai-git in 3.0.0. Users install ai-git |
| `/ai-workflow:workflow-claude-actions` | `/install-github-app` (built-in) | removed | Removed in 3.0.0. To refresh older workflows, run it again and pick "Update workflow file with latest version" |
| `/ai-workflow:workflow-principles` | `/init` (built-in) | removed | Removed in 3.0.0. `/init` writes CLAUDE.md from the project's own build commands and conventions |
| `/ai-workflow:workflow-plan-phases`, `/ai-workflow:plan-phases`, `/ai-workflow:workflow-implement-phases`, `/ai-workflow:implement-phases` | Dynamic Workflows (built-in) | removed | Removed in July 2026 (ai-workflow 2.0.0). The `plan-phases` and `implement-phases` names were renamed with a `workflow-` prefix in 1.6.1 |
| `/ai-learn:learn`, `/ai-learn:learn-review` | Learning output style: `/config` (built-in) | removed | Plugin removed in July 2026. In `/config`, set "Output style" to "Learning" |
| `/ai-plugins:plugins-scaffold`, `/ai-plugins:scaffold-plugin`, `skills-scaffold` | ask Claude Code to create the plugin (built-in) | removed | Plugin removed in 2.0.0. `/scaffold-plugin` was renamed `/plugins-scaffold` in 1.2.0 |
| `docs/aeo-audit/`, `docs/geo-audit/` | `docs/seo-audit/` | changed | `/seo-audit` writes new reports here since 3.0.0, and still reads the old folders for trends. Old reports stay where they are. In `.gitignore`, add the new folder next to the old line rather than replacing it |
| `docs/security/<date>-cvp-security-audit.md` | `docs/security/<date>-security-cvp-audit.md` | changed | Report name from `/security-cvp-audit` since 3.0.0. Old reports keep their names |
