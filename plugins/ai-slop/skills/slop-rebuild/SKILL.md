---
name: slop-rebuild
description: "Rebuild a feature an agent just implemented as the simpler version it would write now that it knows the problem, without losing the first version. Snapshots the original to a branch, pins the tests that must still pass, lists what the first pass learned, reimplements the feature tests-first in a separate worktree, then compares diff size, complexity and test results and recommends one, including keeping the original. Changes the user's checkout only after they choose. Use when the user runs /slop-rebuild, or asks to scrap an implementation and redo it the simple or elegant way, such as 'knowing everything you know now, scrap this and implement the elegant solution'."
argument-hint: "[path or glob] [--base <ref>]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
  - Bash(git symbolic-ref *)
  - Bash(git ls-files *)
  - Bash(git check-ignore *)
  - Bash(git worktree list *)
---

# Rebuild a feature the simple way

An agent's first working version of a feature carries the uncertainty it had while it built it: abstractions it didn't need, temporary helpers, duplicated logic, extra layers, fallbacks for cases that can't happen. Once it works, the agent knows the problem. Use that knowledge to write the feature again, then let the evidence decide which version stays.

A second version isn't better by default. Keep the original safe, build the rebuild beside it, compare the two, and recommend the original when the rebuild isn't clearly better.

## Arguments

Arguments: $ARGUMENTS

Claude Code replaces the placeholder on the line above with the text typed after the command, and leaves the line empty when there is none. In agents that leave the placeholder unreplaced, use the text the user typed after the command.

- **Scope**, optional: a path or glob that narrows the rebuild to part of the feature. Without one, the scope is every file the feature changed.
- `--base <ref>`: the commit the feature started from. The default is the merge base with the default branch. `--base HEAD` covers only the uncommitted changes.

Ask questions with the AskUserQuestion tool when it's available, and in plain text otherwise, then wait for the answer.

## Guardrails

- **Never lose the user's work.** Snapshot the original before anything else. Never run `git reset --hard`, `git checkout -- .`, `git restore`, `git clean`, `git stash drop`, `git branch -D`, `git worktree remove --force` or a force push in the user's checkout, unless the user asks for that command.
- **Leave the user's checkout alone until they choose.** Run tests, edit and commit only in the rebuild worktree, on this skill's own branches.
- **Tests first.** Pin the feature's behavior with tests before you scrap any code, and watch those tests fail without the feature.
- **Keep the behavior and the public API.** Keep the same inputs, outputs, errors and side effects. Keep exported names and signatures, routes, CLI flags, config keys, schemas and file formats. If the simple version needs a change to any of them, stop and ask. If the user says no, keep the original's behavior.
- **Keep to the feature.** Change only the files the feature added or changed. You can call existing helpers, but don't change them, and don't refactor code outside the feature. List those ideas as follow-ups.
- **Do the rebuild yourself, in this conversation.** A subagent or a new session doesn't know what you learned, and the rebuild depends on it.
- Don't push, open a pull request or merge.

## When not to use it

Say which of these applies and stop. Go on only if the user insists.

- **The change is small or already simple**, such as one or two files, or a diff with no layer, helper or branch you would drop. Clean it up in place instead. In Claude Code, the built-in `/simplify` does that.
- **The change is mechanical**: a rename, a dependency upgrade, formatting, generated code, a migration or a config change.
- **The feature doesn't work yet.** Finish it first. The comparison needs two working versions.
- **The behavior can't be checked.** There are no tests, and you can't write tests for it, as with hardware or a UI the project has no test harness for. Without a check, the comparison has no evidence.
- **The code is merged, or other work builds on it.** That's a refactor of shared code. Plan it and review it as one.

## 1. Find the feature

1. Find the default branch with `git symbolic-ref --short refs/remotes/origin/HEAD`. If that fails, use `origin/main` or `origin/master`, or the local branch when there's no remote. Take `<base>` from `--base`, or from `git merge-base HEAD <default branch>`.
2. List the commits in `<base>..HEAD`, then `git diff --stat <base>` and `git status --short`. If the commits look like more than one piece of work, ask which commit the feature started from, and recommend one.
3. Say in one or two sentences what the feature does for its user. Split the changed files into code and tests. Tests include fixtures and snapshots. With a scope argument, keep only the code files that match it.
4. Say whether you built the feature in this conversation. If you didn't, the list in "4. List what you learned" comes only from the diff and its history, and the rebuild usually gains less.
5. Check the list in "When not to use it".
6. Pick a short kebab-case slug for the feature, such as `csv-export`.

## 2. Snapshot the original

The snapshot is a branch named `slop-rebuild/<slug>-original`. If the name is taken, add `-2`. Never use `git branch -f`.

- **Clean working tree:** `git branch slop-rebuild/<slug>-original HEAD`.
- **Uncommitted changes:** commit them to the snapshot branch through a temporary index, so the user's working tree, index and branch stay as they are. First read `git status --short`. If an untracked file looks like a secret or build output that `.gitignore` misses, ask before you include it. Then run these commands, with a literal path for the temporary index and no shell variable. Some agents block `rm` on a path held in a variable.

  ```bash
  GIT_INDEX_FILE=/tmp/slop-rebuild-<slug>.index git read-tree HEAD
  GIT_INDEX_FILE=/tmp/slop-rebuild-<slug>.index git add -A
  GIT_INDEX_FILE=/tmp/slop-rebuild-<slug>.index git write-tree   # prints <tree>
  git commit-tree <tree> -p HEAD -m "slop-rebuild: snapshot of <slug>"   # prints <snapshot>
  git branch slop-rebuild/<slug>-original <snapshot>
  rm /tmp/slop-rebuild-<slug>.index
  ```

  The snapshot holds staged, unstaged and untracked changes. It leaves out files that `.gitignore` excludes.

Record which of the two cases applied, because step 7 needs it. Tell the user the snapshot branch's name.

## 3. Pin the behavior

1. Create the rebuild worktree from the snapshot: `git worktree add -b slop-rebuild/<slug>-rebuild <dir> slop-rebuild/<slug>-original`. Put `<dir>` outside the checkout, such as `../<repo>-<slug>-rebuild`. If your agent can't write there, use a folder inside the checkout that `.gitignore` already excludes, and confirm it with `git check-ignore`.
2. Set up the worktree the way the project's README or CI does, such as installing dependencies. Worktrees don't share untracked files, so copy any git-ignored local config the tests need, such as `.env`. Never commit it.
3. Find the project's typecheck, lint and test commands in its scripts, Makefile, CI config, `CLAUDE.md` or `AGENTS.md`. Run them in the worktree. This is the baseline. If the feature's own tests fail, stop: the original doesn't work yet. Record any other failures, so the rebuild isn't blamed for them.
4. List what must still hold: the feature's behaviors, including errors and edge cases, and the public surface it adds or changes.
5. Write tests for each behavior that no test covers. Test through the public surface, not internal helpers. Run the new tests against the original in the worktree, and they must pass. If one fails, check the test first. If the test is right, the original has a bug. Report it, and ask whether the rebuild keeps the bug or fixes it. Commit the tests alone, such as `test: pin <feature> behavior`. Call this commit `<pinned>`. If you added no tests, `<pinned>` is the snapshot.

## 4. List what you learned

Before you write code, write this list and show it to the user:

- **Real constraints:** what the code has to handle, such as edge cases, API behavior, platform limits and ordering.
- **Helpers to reuse:** code that already exists in the project and that the original duplicated or worked around.
- **Parts that weren't needed:** an interface with one implementation, a generic type with one caller, options nobody sets, wrappers that only pass calls through, extra layers.
- **Scaffolding:** debug logging, retries or sleeps added while debugging, fallbacks for states that can't happen, defensive checks the types already rule out, code left over from an approach you dropped.
- **Duplicated logic.**
- **What the original got right**, so the rebuild keeps it.
- **Dead ends:** approaches that failed, and why, so the rebuild doesn't try them again.

If the original has code for speed, such as a cache or batching, measure both versions before you call that code unnecessary. Then sketch the rebuild in a few lines: the files, the main functions and the call path. Continue to step 5 without waiting, unless the sketch needs a change to behavior or the public API.

## 5. Scrap and rebuild

1. In the worktree, restore the feature's code files to `<base>`, but not its tests: `git restore --source=<base> --staged --worktree -- <code files>`. This removes files the feature added and brings back files it deleted.
2. Run the feature's tests. They should fail, or fail to compile. Note any test that still passes, because it doesn't test the feature.
3. Write the feature again from the step 4 list, not from the original's code. Copy a piece of the original only when it was already right, such as a tricky query or parser, and note which pieces you copied. Reuse the helpers you listed. Leave out the scaffolding and the parts that weren't needed. Add no abstraction, option or fallback that the list doesn't call for.
4. Keep every test that pins behavior. A test of an internal helper that the rebuild removes can go, but only when a behavior test covers the same case. Note each test you change or delete, and why.
5. Run the full baseline. Everything that passed on the original must pass. Rerun a failing test once before you count it as a failure.
6. Commit the rebuild as one commit on top of `<pinned>`, in the repository's commit style, so no commit in between is broken.

If the rebuild comes out as large or as complex as the original, stop there and recommend the original.

## 6. Compare and recommend

Measure both versions against `<base>`, for code files and test files separately: `git diff --shortstat <base> <pinned> -- <code paths>` and the same for the rebuild. Read `git diff <pinned> slop-rebuild/<slug>-rebuild` in full. That diff is what a reviewer reads if the user switches. Count the new files, exported names, types, dependencies and settings from the diffs. If the project has a complexity tool, such as ESLint's `complexity` rule, radon, gocyclo or lizard, run it on both versions. Otherwise, leave complexity scores out. Don't estimate them.

Recommend one of three outcomes:

- **Use the rebuild:** every check that passed on the original passes, nothing changed in behavior or the public API that the user didn't ask for, and a reviewer would see that it's simpler, with fewer concepts, layers, files or special cases. Fewer lines don't count when the code is denser or cleverer.
- **Keep the original:** the rebuild isn't clearly better, a check fails, or the behavior differs. When the two are close, keep the original. A switch costs review time and adds risk for little gain. The work spent on the rebuild isn't a reason to use it.
- **Take parts:** one or two simplifications are worth it, such as reusing a helper, and the rest isn't. Name each part.

Use this format:

```text
<One paragraph: the feature in one sentence, the base, whether you built it in this conversation, the snapshot branch, the rebuild branch and the worktree path, and "Your checkout hasn't changed.">

| | Original | Rebuild |
|---|---|---|
| Code files changed | | |
| Code lines added / removed | | |
| Test files / test cases | | |
| New files | | |
| New exported names | | |
| New types, classes or interfaces | | |
| New dependencies or settings | | |
| Call path from the entry point | <e.g. handler → service → repository → client> | <e.g. handler → client> |
| Complexity (<tool>) | | |
| Typecheck / lint / tests | <e.g. pass / pass / 48 of 48> | |

## What the rebuild dropped
- <the abstraction, helper, layer, scaffolding or duplicate>, and why it wasn't needed

## What it kept from the original
## Differences in behavior or public API
<"None found", or each one, with the test that shows it.>
## Tests changed or deleted
## Recommendation
<Use the rebuild | Keep the original | Take parts: <parts>>, and the reason in two or three sentences.
## Your choice
<The three options, with what each one does to the checkout and the branches. Recommended option first.>
```

Leave out a table row when neither version has anything for it. End your turn after the report. Without an answer, change nothing.

## 7. Apply the user's choice

Before you change the user's checkout, check that it still matches the snapshot. Run the `read-tree`, `add` and `write-tree` commands from step 2 again, delete the temporary index, and compare the printed tree with `git rev-parse slop-rebuild/<slug>-original^{tree}`. If they differ, the user has changed something since. Stop and ask. Don't apply over their new work.

- **Use the rebuild:**
  - If the working tree was clean at step 2, run `git merge --ff-only slop-rebuild/<slug>-rebuild` in the user's checkout. Their branch gains the pinned tests and the rebuild as new commits, and keeps its old ones.
  - If step 2 snapshotted uncommitted changes, run `git diff --binary slop-rebuild/<slug>-original slop-rebuild/<slug>-rebuild | git apply`. The rebuild then replaces the original as uncommitted changes, as the original was.
  - Run the baseline checks in the user's checkout.
- **Keep the original:** leave the checkout as it is. If step 3 added tests, offer to bring them over, because they still pin the behavior.
- **Take parts:** make the chosen changes in the user's checkout as targeted edits, leave them uncommitted, and run the baseline checks.

Then remove the worktree with `git worktree remove <dir>`. If git refuses because the worktree has changes, leave it and say why. Keep both branches. Tell the user their names and the command that deletes them, `git branch -D slop-rebuild/<slug>-original slop-rebuild/<slug>-rebuild`, but don't run it yourself.

End with what changed in the checkout, the check results, and the branches that remain.
