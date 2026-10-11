---
name: git-commit-push-pr
description: "Commits the current changes with a message in the repo's style, pushes, and opens a PR. Asks which branch to commit to and which branch the PR targets. --preflight runs /git-preflight --fix first, and --no-pr stops after the push."
argument-hint: "[--preflight] [--no-pr]"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
disable-model-invocation: true
---

# /git-commit-push-pr - Commit, Push, PR

Commit the current changes, push them, and open a pull request. Ask the user where to commit and where the PR should merge, and never assume either.

Ask every question with the AskUserQuestion tool when it's available, so the user can answer with one pick. Otherwise ask in plain text, number the options, and wait for the answer.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

- `--preflight`: run the git-preflight skill with `--fix` before anything else (Step 1).
- `--no-pr`: commit and push, then stop without opening a PR.

The two can be combined. Ignore anything else in the arguments, including a commit message, and say in one line that you did: the message comes from the diff.

## Step 1: Preflight (only with `--preflight`)

Run the git-preflight skill from this plugin with `--fix` as its arguments. It runs the project's typecheck, lint, format, security and test checks, applies the auto-fixes it can without asking, and re-runs what failed.

- **Claude Code**: call the Skill tool with skill `ai-git:git-preflight` and args `--fix`.
- **Codex and Cursor**: load the `git-preflight` skill from this plugin (Codex lists it as `ai-git:git-preflight`), and follow its instructions with `--fix` as its arguments.

If the skill can't be loaded, stop and tell the user to run `/git-preflight --fix` (`$ai-git:git-preflight --fix` in Codex), then run this command again without `--preflight`.

When preflight finishes:

- **It applied fixes**: stop. Tell the user what failed and what was fixed, ask them to review the fixes, and tell them to run this command again once they're satisfied.
- **Problems remain** that it couldn't fix: stop and report them.
- **Every check passed** with no fixes: continue. If the project has no checks configured, say so and continue.

## Step 2: Analyze the changes

1. `git branch --show-current`
2. `git status` (never `-uall`, which can exhaust memory on large repos). If there is nothing to commit (no untracked files and no modifications), tell the user and stop.
3. `git diff` and `git diff --staged` to see the changes.
4. `git log -5 --format='%s'` to see the repo's commit message style.

## Step 3: Pick the branch

Ask where to commit:

- **On `main`, `master` or the repo's default branch**: don't commit there. Offer:
  - "Create new branch" (description: "Create a feature/fix branch for these changes")
  - The user can type a branch name instead ("Other" in AskUserQuestion).
- **On any other branch** (staging, feature/*, fix/*, etc.), offer:
  - "Current branch ({branch_name})" (description: "Commit directly to {branch_name}"), first and recommended
  - "Create new branch" (description: "Create a new branch off {branch_name} for these changes")

If the user picks "Create new branch", name it after the change in the style of the repo's branches (`feat/...`, `fix/...`). If they typed a name, use it. Then `git checkout -b <branch_name>`.

## Step 4: Stage and commit

1. Stage the changed files by name. Don't use `git add .` or `git add -A`.
2. Never stage files that look like secrets: `.env`, `.env.*`, `credentials.*`, `*.key`, `*.pem`, `*.secret` and similar. If any are present, skip them and warn the user.
3. Write a concise commit message that says what changed and why, follows the style from Step 2, and uses conventional commit prefixes (`feat:`, `fix:`, `docs:`) if the repo uses them.
4. Add no AI attribution to the commit: no `Co-Authored-By` trailer, no "Generated with" line, and nothing else that credits Claude, Codex, Cursor or another agent.
5. Pass the message through a HEREDOC:

   ```bash
   git commit -m "$(cat <<'EOF'
   your commit message here
   EOF
   )"
   ```

## Step 5: Push

1. Check for an upstream: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null`
2. With no upstream, `git push -u origin <branch>`. Otherwise `git push`.
3. If the push is rejected, report why and stop. Never force push.

With `--no-pr`, show the branch and commit hash, and stop here.

## Step 6: Pick the PR target

Opening a PR needs the GitHub CLI (`gh`), installed and authenticated. If it isn't, say so and stop: the commit is already pushed.

If the branch already has an open PR (`gh pr view --json url,state` shows `OPEN`), the push updated it. Give its URL and stop.

Gather context:

```bash
# The repo's default branch
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name

# Whether staging exists on origin
git ls-remote --heads origin staging
```

Ask where the PR should merge, with options built from what exists:

- **On `staging`**: offer only the default branch.
- **On any other branch**:
  - If `staging` exists on origin: "staging" (description: "Merge into staging for pre-production review"), first and recommended, then the default branch (description: "Merge directly into {default}").
  - Otherwise: the default branch (description: "Merge into {default}"), recommended.

The user can always type another branch name.

## Step 7: Open the PR

1. `git fetch origin <target>`, then `git log origin/<target>..HEAD --oneline` and `git diff origin/<target>...HEAD` to see everything the PR includes.
2. Create it with `gh pr create`:
   - `--base <target>`
   - A title under 70 characters.
   - A body with 1-3 summary bullets and a test plan. The test plan lists only what was actually run: the preflight checks with `--preflight`, commands run in this session, or testing the user described. If nothing was run, write "Not tested" and one sentence on what needs checking.
   - End the body with an attribution line for the agent running this skill: `🤖 Generated with [Claude Code](https://claude.com/claude-code)` in Claude Code, `🤖 Generated with [Codex](https://openai.com/codex)` in Codex, or `🤖 Generated with [Cursor](https://cursor.com)` in Cursor.
   - Pass the body through a HEREDOC:

   ```bash
   gh pr create --base <target> --title "the pr title" --body "$(cat <<'EOF'
   ## Summary
   <1-3 bullet points>

   ## Test plan
   <what was actually run>

   <attribution line for the agent running this skill>
   EOF
   )"
   ```

3. Give the user the PR URL.

## Rules

- Ask the branch and PR target questions every time. Never assume.
- Never commit or push directly to `main`, `master` or the default branch.
- Never force push.
- Never use `git status -uall`.
- Never commit files that look like secrets.
- No AI attribution in commit messages. The PR body ends with the line naming the agent that ran the skill.
- If there is nothing to commit, say so and stop.
