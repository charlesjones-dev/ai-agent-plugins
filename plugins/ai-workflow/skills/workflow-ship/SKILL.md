---
name: workflow-ship
version: 1.0.1
description: |
  Runs preflight checks (typecheck, lint, tests), auto-fixes issues,
  then commits, pushes, and creates a PR. Bails early if preflight fixes were
  needed so you can review before shipping. Prompts for branch and PR target
  using quick multi-choice questions.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
disable-model-invocation: true
---

# /workflow-ship - Preflight, Commit, Push, PR

You are a shipping assistant. Your job is to get the current branch shipped by running quality checks, committing, pushing, and opening a PR. Use `AskUserQuestion` for all user prompts so the flow is fast with minimal typing.

## Process

### Step 1: Preflight checks

Invoke the `workflow-preflight` skill with the Skill tool, passing `--fix` as its arguments, to run the typecheck, lint, format, security and test checks. With `--fix`, preflight applies the auto-fixes it can (lint --fix, format, etc.) without asking and re-runs the failing checks.

- If preflight applied fixes, **STOP HERE** and tell the user:
  - What failed and what was fixed
  - Ask them to review the fixes before shipping
  - Tell them to run `/workflow-ship` again once they're satisfied
- If issues remain that preflight couldn't fix, **STOP HERE** and report them

If all checks pass with no fixes needed, proceed to Step 2.

### Step 2: Branch + Commit

First, determine the current branch:
```bash
git branch --show-current
```

Then run `git status` (never -uall) and `git diff` to understand changes. If there are no changes, tell the user and stop.

**Branch prompt:** Use `AskUserQuestion` to ask the user where to commit:

- If on `main` or `master`: Do NOT allow committing directly. Present options:
  - "Create new branch" (description: "Create a feature/fix branch for these changes")
  - The user picks "Other" to type a custom branch name

- If on any other branch (staging, feature/*, fix/*, etc.): Present options:
  - "Current branch ({branch_name})" (description: "Commit directly to {branch_name}") - mark as first/recommended option
  - "Create new branch" (description: "Create a new branch off {branch_name} for these changes")

If the user chooses "Create new branch" or types a custom name via "Other":
1. Create and checkout the new branch: `git checkout -b <branch_name>`

Then proceed with the commit:
1. Run `git log --oneline -5` to match the repo's commit message style
2. Stage relevant files (prefer specific files over `git add -A`)
3. Draft a concise commit message focused on the "why"
4. Do NOT include any Claude attribution in the commit message (no "Generated with Claude Code" lines or Co-Authored-By trailers)
5. Use a HEREDOC for the commit message to ensure proper formatting

### Step 3: Push

1. Check if the current branch tracks a remote: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null`
2. Push to remote with `-u` flag if no upstream is set, otherwise a normal push
3. Verify the push succeeded

### Step 4: Create PR

First, gather context:
```bash
# Current branch
git branch --show-current

# Check if staging exists on origin
git ls-remote --heads origin staging

# Check if main exists on origin
git ls-remote --heads origin main
```

**PR target prompt:** Use `AskUserQuestion` to ask where the PR should merge into. Build the options dynamically based on what exists:

- If the current branch is `staging`: only offer `main` (and "Other" is always available for custom input)

- If the current branch is anything else (feature/*, fix/*, etc.):
  - If `staging` exists on origin: offer these options:
    - "staging" (description: "Merge into staging for pre-production review") - mark as first/recommended
    - "main" (description: "Merge directly into main/production")
  - If `staging` does NOT exist on origin: offer these options:
    - "main" (description: "Merge into main") - mark as first/recommended

The user can always pick "Other" to type any custom branch name.

Then create the PR:
1. Run `git log <target>..HEAD --oneline` to understand all commits being included
2. Run `git diff <target>...HEAD` to see the full diff
3. Create a PR using `gh pr create` with:
   - `--base <target_branch>` to set the merge target
   - A short title (under 70 characters)
   - A body with Summary bullets and Test plan
   - Use HEREDOC format for the body
   - Include the Claude Code attribution footer

Format:
```
gh pr create --base <target_branch> --title "the pr title" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Test plan
<checklist of testing steps>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

4. Return the PR URL to the user

## Important rules

- Always use `AskUserQuestion` for branch and PR target prompts (never assume)
- Never skip preflight checks
- Never force push
- Never commit or push directly to main/master
- If there are no changes to commit, tell the user and stop
- Do not commit files that look like secrets (.env, credentials, etc.)
