---
name: workflow-preflight
description: "Runs the project's configured typecheck, lint, format, security and test checks and offers to fix what fails. Use when the user asks for preflight checks or to check code before committing, and when /workflow-ship runs it."
argument-hint: "[--fix | --check-only | --verbose]"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Preflight Code Quality Checks

You are running a comprehensive preflight check on this codebase. This command discovers and runs configured quality checks including type checking, linting, and tests.

## Arguments

- `--fix` - Automatically attempt to fix issues without prompting
- `--check-only` - Only report issues, never prompt to fix
- `--verbose` - Show detailed output from all commands
- No arguments - Interactive mode (default): prompt before fixing

User provided: $ARGUMENTS

## Step 1: Discovery Phase

First, analyze the project to discover configured quality tools. Check for:

### Package Manager & Config Files
- `package.json` - Check for scripts: `lint`, `typecheck`, `type-check`, `tsc`, `test`, `check`, `validate`
- `tsconfig.json` / `jsconfig.json` - TypeScript/JavaScript configuration
- `.eslintrc*`, `eslint.config.*` - ESLint configuration
- `biome.json`, `biome.jsonc` - Biome configuration
- `.prettierrc*`, `prettier.config.*` - Prettier configuration
- `deno.json` / `deno.jsonc` - Deno configuration
- `.stylelintrc*` - Stylelint configuration

### Python Projects
- `pyproject.toml` - Check for ruff, mypy, pytest, black, isort configs
- `setup.py` / `setup.cfg` - Legacy Python config
- `requirements.txt` / `requirements-dev.txt` - Dependencies
- `mypy.ini` / `.mypy.ini` - MyPy configuration
- `ruff.toml` / `.ruff.toml` - Ruff configuration
- `pytest.ini` / `pyproject.toml [tool.pytest]` - Pytest configuration
- `tox.ini` - Tox configuration

### .NET Projects
- `*.csproj` / `*.fsproj` / `*.vbproj` - .NET project files
- `*.sln` - Solution files
- `.editorconfig` - Editor configuration with .NET analyzers
- `Directory.Build.props` - MSBuild properties

### Go Projects
- `go.mod` - Go module
- `.golangci.yml` / `.golangci.yaml` - GolangCI-Lint configuration

### Rust Projects
- `Cargo.toml` - Check for clippy, rustfmt
- `rustfmt.toml` / `.rustfmt.toml` - Rustfmt configuration
- `clippy.toml` / `.clippy.toml` - Clippy configuration

### Security Scanning
- `pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` - Dependency audit support
- `.semgreprc.yml` / `.semgrep.yml` / `semgrep.yml` / `.semgrep/` - Semgrep configuration
- `.github/workflows/*.yml` - Check for semgrep CI jobs (extract config flags)
- `eslint-plugin-security` in devDependencies - ESLint security rules
- `package.json` scripts containing `audit` or `semgrep` - Custom security scripts
- `README.md` / `CONTRIBUTING.md` - Check for documented security scanning commands

### Other
- `Makefile` / `makefile` - Check for lint/test/check targets
- `.pre-commit-config.yaml` - Pre-commit hooks
- `justfile` - Just command runner

## Step 2: Report Discovery

Present a summary of what was discovered:

```
Preflight Discovery Summary

Project Type: [Node.js / Python / .NET / Go / Rust / Multi-language]

Type Checking: [tool name] via [config file]
Linting: [tool name] via [config file]
Testing: [tool name] via [config file]
Formatting: [tool name] via [config file]
Security Scanning: [tool name(s)] via [config file/method]
Not configured: [any missing categories]

Ready to run checks?
```

## Step 3: Execute Checks

Run the discovered checks in this order:
1. **Type checking** (fastest feedback on type errors)
2. **Linting** (code quality issues)
3. **Formatting check** (style consistency - check only, don't auto-fix yet)
4. **Security scanning** - MANDATORY if any security tools detected:
   - Dependency audit (npm audit, pnpm audit, etc.)
   - **Semgrep SAST** - MUST run if detected in CI workflows or config files
5. **Tests** (run last as they take longest)

**CRITICAL: If Semgrep was detected in discovery (CI workflows, config files, or README), you MUST run it. Do NOT skip Semgrep and report "All checks passed" without running it.**

For each check, report:
- Pass - no issues found
- Warnings - non-blocking issues
- Fail - blocking issues found

### Common Commands by Ecosystem

**Node.js/TypeScript:**
- TypeScript: `npx tsc --noEmit` or `npm run typecheck`
- ESLint: `npx eslint . --max-warnings=0` or `npm run lint`
- Biome: `npx biome check .`
- Tests: `npm test` or `npx jest` or `npx vitest run`

**Python:**
- MyPy: `mypy .` or `mypy src/`
- Ruff: `ruff check .`
- Pytest: `pytest` or `python -m pytest`
- Black check: `black --check .`

**.NET:**
- Build with warnings: `dotnet build --warnaserror`
- Format check: `dotnet format --verify-no-changes`
- Tests: `dotnet test`

**Go:**
- Type check: `go build ./...`
- Lint: `golangci-lint run`
- Tests: `go test ./...`

**Rust:**
- Check: `cargo check`
- Clippy: `cargo clippy -- -D warnings`
- Tests: `cargo test`
- Format check: `cargo fmt --check`

### Security Scanning Commands

**Dependency Audits (run based on detected package manager):**
- pnpm: `pnpm audit` or `pnpm audit:check` (if script exists in package.json)
- npm: `npm audit`
- yarn: `yarn audit`
- pip: `pip-audit` (if installed) or `safety check` (if installed)
- cargo: `cargo audit` (if installed)

**Semgrep (static analysis - MUST run if detected in CI or config):**

IMPORTANT: If Semgrep is detected in CI workflows or config files, you MUST run it as part of preflight checks. Do not skip it.

Detection order:
1. Check for custom script in package.json (e.g., `pnpm run semgrep` or `npm run semgrep`)
2. Check for semgrep config files: `.semgreprc.yml`, `.semgrep.yml`, `semgrep.yml`, or `.semgrep/` directory
3. Check `.github/workflows/*.yml` for semgrep jobs - extract `--config` flags used in CI
4. **Check `README.md` for documented semgrep commands** - ALWAYS check this before trying generic Docker commands, as projects often document the exact command needed for their setup
5. Check if `semgrep` CLI is available locally: `semgrep --version`
6. Check if Docker is available: `docker --version`
7. If Docker available but no semgrep CLI, use Docker (see platform-specific commands below)

**Semgrep execution:**
- With config file: `semgrep scan --config .semgreprc.yml` (or detected config)
- Without config (auto rules): `semgrep scan --config auto`
- With language-specific rules: `semgrep scan --config auto --config p/javascript --config p/typescript`

**Docker execution (AUTOMATIC PLATFORM DETECTION):**

CRITICAL: You MUST detect the platform and use the correct command automatically. Check the platform from the environment context.

- **If platform is `win32` (Windows):** ALWAYS use `MSYS_NO_PATHCONV=1` prefix for Docker commands:
  ```bash
  MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/src" semgrep/semgrep semgrep scan --config auto /src
  ```

- **If platform is `darwin` (macOS) or `linux`:** Use standard Docker command:
  ```bash
  docker run --rm -v "$(pwd):/src" semgrep/semgrep semgrep scan --config auto /src
  ```

**Why this matters on Windows:** Git Bash/MSYS2 performs automatic POSIX-to-Windows path conversion. Without `MSYS_NO_PATHCONV=1`, the Docker volume mount `/src` gets incorrectly converted to `C:/Program Files/Git/src`, causing Semgrep to fail with "Invalid scanning root" error.

DO NOT try the command without the prefix first on Windows - use the correct platform-specific command immediately.

**ESLint Security Plugin:**
- If `eslint-plugin-security` is detected in devDependencies, security rules are already included in the linting step
- No separate command needed, but note in discovery output that security linting is active

## Step 4: Results Summary

Present results in a clear summary:

```
Preflight Results

Type Checking     Passed
Linting           3 errors, 2 warnings
Formatting        5 files need formatting
Security Audit    2 vulnerabilities found
Security SAST     Passed (semgrep)
Tests             42 passed, 0 failed

Overall: Issues found
```

## Step 5: Fix Prompt (Interactive Mode)

If issues were found AND user didn't pass `--check-only`:

**If `--fix` was passed:** Proceed directly to fixing without prompting.

**Otherwise, ask:**

```
Would you like me to attempt fixes?

[1] Fix all auto-fixable issues (lint --fix, format, etc.)
[2] Fix only linting issues
[3] Fix only formatting issues
[4] Show me the specific issues first
[5] Skip fixes - I'll handle it manually

Enter choice (1-5):
```

Wait for user input before proceeding.

## Step 6: Apply Fixes (if requested)

When fixing:
1. Run auto-fix commands (e.g., `eslint --fix`, `ruff --fix`, `prettier --write`)
2. Re-run the checks to verify fixes
3. Report what was fixed and what still needs manual attention

```
Fix Results

Auto-fixed:
  3 linting errors resolved
  5 files formatted

Still needs attention:
  1 type error in src/utils.ts:42
     Property 'foo' does not exist on type 'Bar'
```

## Important Guidelines

1. **Never run fix commands without user consent** unless `--fix` was explicitly passed
2. **Preserve user's working state** - don't modify files unexpectedly
3. **Respect existing configuration** - use project's own scripts when available (e.g., `npm run lint` over raw `eslint`)
4. **Handle missing tools gracefully** - if a tool isn't installed, note it and continue
5. **Provide actionable feedback** - include file paths and line numbers for manual fixes
6. **Consider CI alignment** - mention if checks match CI configuration

## Error Handling

If a tool fails to run:
```
Could not run [tool]: [error message]
   Suggestion: [how to install or configure]
```

If no quality tools are configured:
```
No quality tools detected in this project.

Would you like me to help set up:
[1] TypeScript type checking
[2] ESLint for linting
[3] Prettier for formatting
[4] A testing framework
[5] Skip setup
```

---

# Preflight Code Quality Checks

This skill provides comprehensive guidance for discovering and running code quality checks across different project types.

## Overview

Preflight checks are the quality gates that verify code before commits, PRs, or deployments. They typically include:

1. **Type Checking** - Static type verification (TypeScript, MyPy, etc.)
2. **Linting** - Code quality and style enforcement
3. **Formatting** - Consistent code style
4. **Security Scanning** - Dependency audits and static analysis (SAST)
5. **Testing** - Unit, integration, and e2e tests

## Quick Reference

### Node.js / TypeScript Projects

| Check | Command | Auto-fix |
|-------|---------|----------|
| TypeScript | `npx tsc --noEmit` | N/A (manual) |
| ESLint | `npx eslint .` | `npx eslint . --fix` |
| Biome | `npx biome check .` | `npx biome check . --write` |
| Prettier | `npx prettier --check .` | `npx prettier --write .` |
| Jest | `npx jest` | N/A |
| Vitest | `npx vitest run` | N/A |

**Prefer npm scripts when available:**
```bash
# Check package.json scripts first
npm run lint        # if exists
npm run typecheck   # if exists
npm run test        # if exists
npm run check       # often runs all checks
```

### Python Projects

| Check | Command | Auto-fix |
|-------|---------|----------|
| MyPy | `mypy .` | N/A (manual) |
| Ruff lint | `ruff check .` | `ruff check . --fix` |
| Ruff format | `ruff format --check .` | `ruff format .` |
| Black | `black --check .` | `black .` |
| isort | `isort --check .` | `isort .` |
| Pytest | `pytest` | N/A |

**With pyproject.toml (modern Python):**
```bash
# Check for [tool.X] sections
ruff check . && ruff format --check .  # Ruff (fast, recommended)
mypy src/                               # Type checking
pytest                                  # Tests
```

### .NET Projects

| Check | Command | Auto-fix |
|-------|---------|----------|
| Build | `dotnet build` | N/A |
| Build strict | `dotnet build --warnaserror` | N/A |
| Format check | `dotnet format --verify-no-changes` | `dotnet format` |
| Tests | `dotnet test` | N/A |
| Analyzers | Configured in `.editorconfig` | N/A |

**.NET specific considerations:**
- Warnings as errors: Add `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` to `.csproj`
- Enable nullable: `<Nullable>enable</Nullable>` for null safety
- Analyzers run during build automatically

### Go Projects

| Check | Command | Auto-fix |
|-------|---------|----------|
| Build | `go build ./...` | N/A |
| Vet | `go vet ./...` | N/A |
| golangci-lint | `golangci-lint run` | `golangci-lint run --fix` |
| gofmt | `gofmt -l .` | `gofmt -w .` |
| Tests | `go test ./...` | N/A |

### Rust Projects

| Check | Command | Auto-fix |
|-------|---------|----------|
| Check | `cargo check` | N/A |
| Clippy | `cargo clippy -- -D warnings` | `cargo clippy --fix` |
| Format | `cargo fmt --check` | `cargo fmt` |
| Tests | `cargo test` | N/A |

### Security Scanning (Cross-Platform)

| Tool | Purpose | Command |
|------|---------|---------|
| pnpm audit | Dependency CVE scan | `pnpm audit` or `pnpm audit:check` |
| npm audit | Dependency CVE scan | `npm audit` |
| yarn audit | Dependency CVE scan | `yarn audit` |
| eslint-plugin-security | JS/TS security patterns | Runs with ESLint |
| Semgrep | SAST scanning | `semgrep scan --config auto` |
| Semgrep (Docker) | SAST scanning | See platform-specific commands below |
| pip-audit | Python dependency scan | `pip-audit` |
| cargo-audit | Rust dependency scan | `cargo audit` |

**IMPORTANT: If Semgrep is detected in CI workflows or config files, you MUST run it as part of preflight checks. Do not skip it.**

**Semgrep Detection Priority:**
1. Package.json scripts (e.g., `pnpm run semgrep`)
2. Config files: `.semgreprc.yml`, `.semgrep.yml`, `semgrep.yml`, `.semgrep/`
3. CI workflows: `.github/workflows/*.yml` (extract `--config` flags)
4. **README.md documentation** - ALWAYS check this before trying generic Docker commands
5. Local CLI: `semgrep --version`
6. Docker fallback (see platform-specific commands below)

**Semgrep Docker Commands (AUTOMATIC PLATFORM DETECTION):**

CRITICAL: Detect the platform from environment context and use the correct command automatically.

- **Windows (`win32`):** ALWAYS use `MSYS_NO_PATHCONV=1` prefix:
  ```bash
  MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/src" semgrep/semgrep semgrep scan --config auto /src
  ```
- **macOS (`darwin`) / Linux:** Standard command:
  ```bash
  docker run --rm -v "$(pwd):/src" semgrep/semgrep semgrep scan --config auto /src
  ```

**Why `MSYS_NO_PATHCONV=1` is required on Windows:** Git Bash/MSYS2 auto-converts POSIX paths to Windows paths. Without this prefix, `/src` becomes `C:/Program Files/Git/src`, causing "Invalid scanning root" error. DO NOT try without the prefix first on Windows.

## Discovery Strategy

### Step 1: Identify Project Type(s)

Check for presence of key files:

```
# JavaScript/TypeScript
package.json, tsconfig.json, deno.json

# Python
pyproject.toml, setup.py, requirements.txt, Pipfile

# .NET
*.csproj, *.sln, *.fsproj

# Go
go.mod

# Rust
Cargo.toml
```

### Step 2: Check for Configured Scripts/Tasks

**package.json scripts (Node.js):**
```json
{
  "scripts": {
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "check": "npm run lint && npm run typecheck && npm run test"
  }
}
```

**pyproject.toml (Python):**
```toml
[tool.ruff]
line-length = 100

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Makefile targets:**
```makefile
lint:
    ruff check .

test:
    pytest

check: lint test
```

### Step 3: Detect CI Configuration

Check for CI files to align local checks with CI:
- `.github/workflows/*.yml` - GitHub Actions (also check for semgrep jobs)
- `.gitlab-ci.yml` - GitLab CI
- `azure-pipelines.yml` - Azure DevOps
- `Jenkinsfile` - Jenkins
- `.circleci/config.yml` - CircleCI

### Step 4: Detect Security Tools

Check for security scanning configuration:
- `package.json` devDependencies for `eslint-plugin-security`
- `package.json` scripts containing `audit` or `semgrep`
- Semgrep config files: `.semgreprc.yml`, `.semgrep.yml`, `semgrep.yml`
- CI workflows for semgrep jobs (extract `--config` flags for local replication)
- `README.md` for documented security commands (often in Security sections)
- Lock files (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`) for audit support

## Best Practices

### Execution Order

Run checks in order of speed and feedback value:
1. **Format check** (fastest, catches style issues)
2. **Type checking** (fast, catches type errors)
3. **Linting** (medium, catches quality issues)
4. **Security scanning** (medium, catches vulnerabilities)
5. **Tests** (slowest, catches logic errors)

This order provides fastest feedback on failures.

### Handling Monorepos

For monorepos, check for workspace configuration:
- `pnpm-workspace.yaml`
- `lerna.json`
- `package.json` with `workspaces` field
- `Cargo.toml` with `[workspace]`

Run checks at workspace root or iterate through packages.

### CI Alignment

Ensure local preflight matches CI:
```bash
# Good: Use same commands as CI
npm run lint    # Same as CI step

# Avoid: Different commands locally vs CI
eslint . --max-warnings=0  # If CI uses npm run lint
```

### Exit Codes

Respect exit codes for CI integration:
- `0` - Success, no issues
- `1` - Failure, issues found
- `2` - Configuration error

### Caching

For faster subsequent runs:
- ESLint: Uses `.eslintcache` with `--cache` flag
- TypeScript: Uses `tsconfig.tsbuildinfo` with `incremental: true`
- Pytest: Uses `.pytest_cache`
- Rust: Uses `target/` directory

## Error Messages Reference

### TypeScript Common Errors

```
TS2339: Property 'x' does not exist on type 'Y'
-> Add property to interface or use type assertion

TS2322: Type 'X' is not assignable to type 'Y'
-> Check type definitions, may need union type

TS7006: Parameter 'x' implicitly has an 'any' type
-> Add explicit type annotation
```

### ESLint Common Errors

```
@typescript-eslint/no-unused-vars
-> Remove unused variable or prefix with _

@typescript-eslint/no-explicit-any
-> Replace 'any' with specific type

import/order
-> Auto-fixable: eslint --fix
```

### Python Common Errors

```
mypy: Incompatible return value type
-> Check return type annotation matches actual return

ruff: E501 Line too long
-> Auto-fixable or configure line-length

ruff: F401 Module imported but unused
-> Remove unused import
```

## Integration with Pre-commit Hooks

Preflight checks can be configured as pre-commit hooks:

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: local
    hooks:
      - id: preflight
        name: Preflight Checks
        entry: npm run check
        language: system
        pass_filenames: false
```

**Husky (Node.js):**
```bash
# .husky/pre-commit
npm run lint
npm run typecheck
```

## When to Skip Checks

Some scenarios where partial checks are acceptable:
- `--no-verify` for emergency fixes (use sparingly)
- WIP commits on feature branches
- Exploratory/spike work

Always run full preflight before:
- Opening PRs
- Merging to main/master
- Deploying to production
