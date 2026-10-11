# AI Modernize Plugin

Codebase modernization assessment that finds technical debt, anti-patterns and quality issues in older AI-generated or legacy code.

## Overview

Codebases built with older AI tools (Claude 3-era models, early Cursor, GPT-4 in 2024) or through "vibe coding" sessions can contain patterns that newer models avoid. This plugin finds those issues and produces a prioritized remediation roadmap with time estimates that assume AI-assisted work. It runs in Claude Code, Codex and Cursor.

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-modernize@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-modernize@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-modernize`. See the [Cursor install steps](../../README.md#cursor).

## Skills

### `/modernize-audit`

Audits the whole repository, a directory or a single file, and saves a scored report with a phased roadmap.

It takes optional arguments after the command: a path for the scope, `key=value` settings that answer the setup questions, and `--defaults`. Quote values that contain spaces. In Codex and Cursor, type the same text after the skill name.

| Argument | Sets | Values |
|----------|------|--------|
| A path | Scope | A file or directory. `.` means the whole repository |
| `ai=` | AI tool history | Tool names separated by commas, or `unsure` or `none` |
| `era=` | When the code was written | A period such as `2024`, or `unsure` |
| `stack=` | Technology stack | The stack, or `auto` to use the detected one |
| `categories=` | Assessment categories | `all`, or category numbers or names separated by commas, such as `security,performance` |
| `severity=` | Severity threshold | `all`, `medium` (Medium and above) or `high` (High and Critical only) |
| `--defaults` | Everything the other arguments leave out | No value. Skips the setup questions and uses the defaults |

**Usage:**
```bash
/modernize-audit
/modernize-audit src/api categories=security,performance
/modernize-audit . ai=copilot era=2024 stack=auto categories=all severity=medium
/modernize-audit src/services --defaults
/modernize-audit src/services/auth.ts --defaults severity=high
```

With no arguments, the skill asks about:
1. AI tools and models used to build the codebase
2. When the codebase was written
3. Technology stack confirmation (auto-detected first)
4. Which of the 12 assessment categories to run
5. Audit scope (entire solution, or a specific file or directory)
6. Severity threshold for the report

It asks only about what the arguments leave out, and asks nothing when all six are given. With `--defaults`, or in an unattended run, it asks nothing and uses defaults for anything missing: AI tools and era "not sure", the detected stack, all categories, the entire solution and all findings. When it runs all categories, it skips any that can't apply to the scope, such as Frontend Debt for backend-only code, and lists them as not applicable.

`/modernize-scan` is now `/modernize-audit <path> --defaults` (since version 2.0.0). It writes the full audit report rather than the shorter scan report.

## Assessment Categories

| # | Category | What It Checks |
|---|----------|---------------|
| 1 | SOLID/DRY/KISS Violations | God classes, duplicated logic, over-engineering, mixed paradigms, YAGNI |
| 2 | Type Safety & Language Misuse | `any` overuse, missing type guards, loose typing, language idiom violations |
| 3 | Error Handling | Empty catch blocks, swallowed errors, missing error boundaries, console.log debugging |
| 4 | Security Anti-patterns | Hardcoded secrets, missing validation, injection risks, insecure defaults |
| 5 | Performance Anti-patterns | N+1 queries, sync bottlenecks, missing pagination, full library imports |
| 6 | Testing Gaps | Implementation-coupled tests, over-mocking, missing edge cases, no integration tests |
| 7 | Architecture Debt | Tight coupling, circular deps, business logic in UI, missing abstraction layers |
| 8 | Frontend Debt | Prop drilling, state mismanagement, useEffect misuse, inline styles, missing a11y |
| 9 | Dependency Health | Deprecated packages, vulnerable versions, unnecessary imports, missing lock files |
| 10 | AI Hallucination Artifacts | Non-existent APIs, wrong signatures, hallucinated packages, deprecated methods |
| 11 | Modern Pattern Gaps | Missing modern syntax, outdated patterns, old CSS, legacy build tools |
| 12 | Configuration & DevOps Debt | Hardcoded config, missing env validation, no health checks, poor Docker practices |

## Report Output

Reports are saved to `docs/modernize/` in the repository, with timestamped filenames: `YYYY-MM-DD-HHMMSS-modernize-audit.md`.

### Report Includes

- Modernization Score (0-100) with category breakdown
- Findings grouped by severity (Critical, High, Medium, Low)
- Exact file paths and line numbers for every finding
- Before/after code examples for remediation
- Time estimates that assume AI-assisted work
- Phased modernization roadmap with prioritized checklist
- A "Why Older AI Models Did This" note on each finding

## Supported Technology Stacks

The plugin auto-detects the stack and adds language-specific checks for:

- **JavaScript/TypeScript**: React, Vue, Nuxt, Next.js, Angular, Svelte, Express, Fastify, Node.js
- **C#/.NET**: nullable reference types, async I/O, records, pattern matching, minimal APIs
- **Python**: type hints, f-strings, context managers, match statements, dataclasses

## Plugin Details

| Field | Value |
|-------|-------|
| Version | 2.0.0 |
| Author | [Charles Jones](https://charlesjones.dev) |
| License | MIT |
| Repository | [ai-agent-plugins](https://github.com/charlesjones-dev/ai-agent-plugins) |

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
