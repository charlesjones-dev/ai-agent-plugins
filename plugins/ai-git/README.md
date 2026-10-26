# AI-Git Plugin

**Git skills for Claude Code, Codex and Cursor.** Generate a .gitignore, run your project's checks before you commit, and commit, push and open a PR with a message in your repo's style.

---

## Available Skills

### `/git-init`

Create or update `.gitignore` with patterns for your project's technology stack.

**What it does:**

- Detects technologies in your project (Node.js, Python, .NET, Go, Rust, PHP, Ruby, Java, Docker, etc.)
- Adds ignore patterns for each detected technology
- Handles environment files, build artifacts, dependencies, OS files, and IDE files
- Merges with an existing .gitignore, keeping your custom patterns and comments
- Groups patterns into commented sections
- Shows a preview and asks before writing

**Usage:**

```
/git-init
```

### `/git-commit-push-pr`

Commit, push and open a pull request in one interactive flow. Two flags change what it does:

- `--preflight` runs `/git-preflight --fix` first. If preflight applied fixes, it stops so you can review them before running the command again. If problems remain that preflight couldn't fix, it stops and reports them.
- `--no-pr` commits and pushes without opening a PR.

**What it does:**

- Reads `git status`, the diff and your last five commit subjects. Stops early if there's nothing to commit
- Asks whether to commit to the current branch or a new one. On main, master or the default branch, it creates a new branch
- Stages the changed files by name, skipping secrets (`.env`, `credentials.*`, `*.key`, `*.pem`, etc.)
- Writes a concise message that says what changed and why, with conventional commit prefixes (`feat:`, `fix:`, `docs:`) if your repo uses them. It adds no AI attribution to the commit
- Pushes, setting upstream with `-u` if needed. It never force pushes
- Asks for the PR target, offering staging first when it exists on origin, then the default branch
- Opens the PR with a title that says what the change does for the user, a summary that starts with the problem and then the fix, a test plan that lists only what was run, and a last line naming the agent that ran the skill (Claude Code, Codex or Cursor)
- Checks the title and body for secrets, and opens the PR through GitHub's REST API when the GraphQL rate limit is used up. If the branch already has an open PR, the push updates it and you get its URL

`/git-commit-push` is now `/git-commit-push-pr --no-pr`.

**Usage:**

```
/git-commit-push-pr                      # Commit, push and open a PR
/git-commit-push-pr --no-pr              # Commit and push only
/git-commit-push-pr --preflight          # Run /git-preflight --fix first, then commit, push and open a PR
/git-commit-push-pr --preflight --no-pr  # Run the checks, then commit and push
```

### `/git-preflight`

Run your project's code quality checks before a commit, PR or deploy.

**What it does:**

- Detects the quality tools each ecosystem in the project has configured
- Runs checks in this order: typecheck, lint, format check, security, tests
- Detects security tools: pnpm/npm/yarn audit, pip-audit, cargo audit, eslint-plugin-security and Semgrep
- Finds Semgrep through package.json scripts, config files, CI workflows or README docs, with a Docker fallback
- Reports each check as pass, warning or fail
- Asks before fixing, or fixes without asking with `--fix`
- Uses the project's own scripts (`npm run lint` over raw `eslint`)

The agent also runs it when you ask to check code before committing.

**Usage:**

```
/git-preflight                  # Interactive mode (default)
/git-preflight --fix            # Auto-fix all fixable issues
/git-preflight --check-only     # Report only, no fixes
/git-preflight --verbose        # Show detailed output
```

In Codex, run it as `$ai-git:git-preflight`.

**Supported ecosystems:**

| Ecosystem | Type Check | Lint | Format | Security | Test |
|-----------|------------|------|--------|----------|------|
| **Node.js/TypeScript** | tsc | ESLint, Biome | Prettier | pnpm/npm/yarn audit, eslint-plugin-security, Semgrep | Jest, Vitest |
| **Python** | MyPy | Ruff | Black, Ruff | pip-audit, safety, Semgrep | Pytest |
| **.NET** | dotnet build | Analyzers | dotnet format | Semgrep | dotnet test |
| **Go** | go build | golangci-lint | gofmt | Semgrep | go test |
| **Rust** | cargo check | Clippy | cargo fmt | cargo audit, Semgrep | cargo test |

Use `--fix` locally and `--check-only` in CI, and keep local checks in line with your CI configuration.

### Removed and moved skills (October 2026)

| Skill | Status |
|-------|--------|
| `/git-commit-push` | Merged into `/git-commit-push-pr`. Run `/git-commit-push-pr --no-pr` |
| `/git-pr-codex-loop` | Removed. Claude Code's built-in `/code-review --fix` covers review-and-fix loops, and `/workflow-babysit` in ai-workflow (Claude Code only) still answers Codex Code Review findings while it takes a branch through merge and deploy |
| `/workflow-ship` (ai-workflow) | Moved here as `/git-commit-push-pr --preflight` |
| `/workflow-preflight` (ai-workflow) | Moved here as `/git-preflight` |

---

## Quick Start

### Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-git@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-git@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-git`. See the [Cursor install steps](../../README.md#cursor).

### Requirements

- Opening a PR needs the GitHub CLI (`gh`), installed and authenticated. `--no-pr` doesn't
- `/git-preflight` runs the tools your project already has. It doesn't install them

---

## Example Commits

The plugin adapts to your repository's style:

**For repos using conventional commits:**

```
feat: add user authentication middleware
fix: resolve memory leak in websocket handler
docs: update API endpoint documentation
refactor: simplify error handling logic
```

**For repos with simple style:**

```
Add user authentication middleware
Fix memory leak in websocket handler
Update API endpoint documentation
Simplify error handling logic
```

---

## How It Works

`/git-commit-push-pr` runs these steps:

1. **Preflight** (with `--preflight`): Runs `/git-preflight --fix`. Stops if it applied fixes or if problems remain.
2. **Analyze**: Runs `git status`, `git diff` and `git log -5` to see your changes and your recent commit style. Stops early if there's nothing to commit.
3. **Branch**: Asks whether to commit to the current branch or a new one. On main, master or the default branch, it creates a new one.
4. **Stage**: Stages the changed files by name, skipping secrets.
5. **Commit**: Writes the message in your repo's style, with no AI attribution.
6. **Push**: Pushes to origin, setting upstream with `-u` if needed. It never force pushes. With `--no-pr`, it stops here and shows the commit hash.
7. **PR**: Asks for the target branch, opens the PR and returns its URL.

---

## Best Practices

Write the commit message yourself for:

- Major releases or version bumps
- Breaking changes that need a detailed explanation
- Merge commits with conflicts
- Commits that need specific issue references

---

## Configuration

There's nothing to configure.

---

## Plugin Details

- **Name:** AI-Git Plugin
- **Type:** AI Instruction Plugin (Skills)
- **Version:** 2.1.0
- **Skills:** `/git-init`, `/git-commit-push-pr`, `/git-preflight`
- **License:** MIT
- **Author:** Charles Jones

---

## Credits

The guidance `/git-commit-push-pr` follows for PR titles and descriptions is adapted from `file-pr` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne, under the MIT license. [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) has the license.

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
