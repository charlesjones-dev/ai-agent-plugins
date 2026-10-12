---
name: workflow-babysit
version: 1.0.0
description: |
  Takes the current branch to production in one unattended run: commits and
  opens the PR if needed, waits for Claude Code, Codex and Cursor Bugbot
  reviews, fixes or triages every finding, merges, promotes staging to production when the repo
  uses a staging branch, and watches the deploy until it is live. With
  --to staging it stops once the change is merged and deployed to staging.
  Use when the user says "babysit this to prod", "babysit to production",
  "babysit this to staging" or runs /workflow-babysit. Merging is part of the
  job, so don't use it when the user only wants a PR opened or reviewed.
argument-hint: "[PR number] [--to staging] [what to do once it is live]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
---

# /workflow-babysit - Babysit a change to production

Run the whole release path for the current branch without stopping for approval at each hop. Invoking this skill, by slash command or by asking to babysit a change to production, is the approval to commit, open PRs, reply on review threads, merge and promote to production.

Assume the user has walked away. Ask every question in step 0, before any waiting starts. After that, only stop for the cases under "When to stop".

User provided: $ARGUMENTS

The arguments may name a PR number to babysit instead of the current branch's PR, may say where the run ends, and may say what to do once the change is live.

## Where the run ends

By default the run ends on production: merged into the default branch and deployed. `--to staging` ends it on staging instead. The PR merges into staging, the staging deploy is watched (step 4), and the release into the default branch is left for later. This suits repos where staging builds go to testers first, such as an internal TestFlight group, and production waits for their sign-off. To promote later, the user runs the skill again from the staging branch, which starts at the release step.

- `--to` takes `staging` or the staging branch's name (`develop` when that's the repo's staging branch). `production`, `prod` and the default branch's name mean the full run. For any other value, stop in step 0 and say which values the repo accepts.
- Plain wording works the same way: "babysit this to staging", "only to staging" or "stop at staging" mean `--to staging`.
- A resumed run (step 0) only promotes staging, so with `--to staging` it has nothing to do. Say so and stop.

## Repo settings

Read the project's CLAUDE.md and the user's `~/.claude/CLAUDE.md` first. When they say anything about how this repo reviews, merges or deploys, it wins over the defaults in this skill. Look for:

- **Review triage**: what to fix before merging and what to defer. Replaces the default triage bar in [reviewers.md](reviewers.md).
- **What to do when Claude Code review is off**: use the local review, proceed without it, or stop. Answers the step 0 question ahead of time.
- **Deploy**: the host, which services to watch, health-check URLs for production and staging, and anything that must happen before or after a deploy (for example, starting a staging database before merging into staging, or tearing staging down afterwards).
- **Merge method** for feature PRs.

## 0. Set up (once per run, all questions here)

Collect everything below, then ask all the questions it raises in one AskUserQuestion call.

1. **Repo**: `gh repo view --json nameWithOwner,defaultBranchRef,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,deleteBranchOnMerge`, `git branch --show-current`, `git status --short`.
2. **Where this run starts**:
   - If the arguments name a PR, or the branch has an open PR, read its `baseRefName`.
   - If you're on the staging branch with nothing uncommitted, no local commits ahead of `origin/staging`, and staging ahead of the default branch, this is a resumed run: go straight to step 5 after step 0.
   - Otherwise a new PR will be opened in step 1.
3. **Branch flow**: the repo has a staging flow if a `staging` (or `develop`) branch exists on origin and recent PRs into the default branch come from it (`gh pr list --state merged --base <default> --limit 5 --json headRefName`). An existing PR's own base decides what happens to it: a PR into staging goes through steps 4 and 5, and a PR straight into the default branch skips them. A new PR targets staging when the repo has a staging flow, and the default branch otherwise. With `--to staging`, a staging branch on origin is enough to count as a staging flow, even with no release PRs yet. If there's no staging branch, or an existing PR targets the default branch, stop before asking anything: the run would never stop at staging.
4. **Merge method**: for feature PRs, CLAUDE.md first, then what recent merged PRs used, then whichever single method the repo allows. Release PRs from staging use a merge commit so staging and the default branch don't diverge. If the repo doesn't allow merge commits, use the method past release PRs used.
5. **Uncommitted changes**: list them. They'll be committed into the PR in step 1. If some look unrelated to the change (scratch files, logs, local config, work in progress elsewhere), ask which to leave out.
6. **Unreleased staging work** (staging flow only, and skipped with `--to staging`, which promotes nothing): list the commits staging would promote, with their GitHub logins:

   ```bash
   gh api "repos/{owner}/{repo}/compare/<default>...staging" \
     --jq '.commits[] | {sha: .sha[0:7], login: .author.login, subject: (.commit.message | split("\n")[0])}'
   ```

   If any commit belongs to someone other than the current user (`gh api user --jq .login`), or has no login, the release PR would ship it too. Ask whether to promote everything in staging or to stop after merging into staging.
7. **Branch rules**: for each branch this run merges into, read its rulesets (`gh api "repos/{owner}/{repo}/rules/branches/<branch>"`) and whether it has classic protection (`gh api "repos/{owner}/{repo}/branches/<branch>" --jq .protected`). For a PR that's already open, `gh pr view <N> --json reviewDecision` returning `REVIEW_REQUIRED` means it needs an approval. If a `pull_request` rule or the PR says approvals are required, warn the user that the run will stop at that merge unless someone approves the PR first. If `deleteBranchOnMerge` is on and staging isn't protected, GitHub may delete staging when the release PR merges. Note the staging head SHA before that merge, so step 5 can restore it.
8. **Reviewers**: work out whether Claude Code review is on, using [reviewers.md](reviewers.md). If it is off, and CLAUDE.md doesn't already say what to do, ask. Say which check failed, and whether Codex or Cursor Bugbot reviewed the repo's last few PRs. Offer:
   - **Use local /code-review (Recommended)**: run Claude Code's built-in `/code-review` on each PR in place of the GitHub Action.
   - **Proceed without it**: Codex and Bugbot, if they're on, are the only reviewers. If both are off too, nothing reviews the PRs.
   - **Stop**: set up the action with Claude Code's built-in `/install-github-app` and run this skill again. To fix an existing workflow, run `/install-github-app` again and pick "Update workflow file with latest version".

   One answer covers the whole run, release PR included. Codex and Bugbot can only be detected once a PR is open (step 2), and their being off is never a reason to stop.
9. **Deploy target**: find it now with [deploy-targets.md](deploy-targets.md), so a missing target is known before anything merges. With `--to staging`, only staging's target matters. If there is none, the run ends after the last merge and says so.

## 1. Get a PR open

If the arguments name a PR, `gh pr checkout <N>`. Otherwise look for one: `gh pr view --json number,url,state,baseRefName,headRefOid`.

If the branch has no open PR:

1. If you're on the default branch or the staging branch, create a branch from HEAD named the way the repo's recent PR branches are (`feat/...`, `fix/...`, a username prefix), describing the change. Never push to the default branch directly.
2. Commit the uncommitted changes from step 0, minus anything the user left out. Stage specific files (never `.env` files, credentials or keys) and write the message in the style of `git log --oneline -10`. Follow CLAUDE.md and your client's instructions on attribution.
3. If there is nothing to commit and the branch has no commits ahead of its base, stop: there's nothing to ship.
4. Push with `git push -u origin HEAD` and open the PR against the base from step 0: a title under 70 characters, and a body with a short summary and a test plan made only of what you know was run (commands you ran or testing the user described). Use `.github/pull_request_template.md` if the repo has one.
5. If your client has a tool for linking pull requests to the session, link the PR. Linking and notifications are optional, so skip them if they would need a permission prompt nobody is there to answer.

If the PR already exists and there are uncommitted changes on its branch, commit and push them into the PR the same way and mention it in the report.

## 2. Review gate

Run this on every PR the skill merges: the feature PR, any fix PRs into staging, and the release PR.

1. **Wait** for each reviewer that is on to finish on the head commit, and for CI. [reviewers.md](reviewers.md) says how to tell when each reviewer is done and how long to wait. Poll every 30 seconds in a background Bash loop with a deadline, never faster:

   ```bash
   deadline=$((SECONDS + 1800))
   until <done-check> || [ "$SECONDS" -ge "$deadline" ]; do sleep 30; done
   ```

   For CI, poll `gh pr checks <N> --json name,bucket,workflow,link`. Leave out the reviewers' own check runs (the Claude Code review job, `Cursor Bugbot` and `Cursor Bugbot Autofix`), which reviewers.md handles. Checks can take a minute or two to register after a push, so don't count "no checks" or "nothing pending" as done until 2 minutes after the push, and every required check (`gh pr checks <N> --required --json name,bucket`) has appeared. CI is done when no check is `pending`. If the deadline passes first, stop.
2. **CI failures**: if a check fails because of the PR, fix it and push. If it fails for an unrelated reason (a flaky test, a runner outage), rerun it once with `gh run rerun <run-id> --failed`. If it fails again, stop.
3. **Humans first**: if a person (not a bot) has requested changes or left an unanswered question on the PR, stop. Don't merge over a teammate, and never resolve a person's thread.
4. **Triage** every bot finding, from Claude Code, Codex, Bugbot or any other review bot, using the triage bar in [reviewers.md](reviewers.md) unless CLAUDE.md has its own. Reply in each finding's thread and resolve it.
5. **Re-review**: if code changed, push and get one re-review scoped to the new commits from each reviewer that is on. Claude Code re-runs by itself on every push; if its workflow doesn't trigger on pushes, the local review covers the new commits instead ([reviewers.md](reviewers.md)). Codex needs one `@codex review` comment per round. Bugbot re-runs on pushes by itself, or gets one `bugbot run` comment when it doesn't. If Bugbot Autofix pushes its own fixes to the branch, pull them before fixing anything yourself (reviewers.md). The 3-round limit counts rounds of fixes, whichever reviewer raised them. Docs-only follow-up commits need no re-review. Stop after 3 rounds. If only non-blocking findings remain, merge and post a "Known limitations" comment on the PR. A finding is blocking when the triage bar puts it under "Fix now". If a blocking finding is still open, stop.

## 3. Merge into the PR's base

1. If merging into this branch deploys, follow any pre-deploy rules from CLAUDE.md first, and snapshot the current deployments ([deploy-targets.md](deploy-targets.md)).
2. Merge with `gh pr merge <N> --<method> --delete-branch --match-head-commit <head SHA when the gate passed>`. Leave out `--delete-branch` when the head is staging. The SHA check stops anything pushed after the gate from slipping in.
3. If the repo uses a merge queue, add `--auto` and poll the PR's state with a 60-minute deadline. If the queue drops the PR because CI failed, fix it and queue it once more. If it's dropped again or the deadline passes, stop.
4. Never pass `--admin`. If GitHub refuses the merge because branch protection needs an approval or a check you can't provide, stop and say what's missing.
5. Fetch, check out the base branch and `git pull --ff-only`. If that fails because the merge squashed commits that were on your local copy, carry on, tell the user in the report, and don't reset it. Create any later branches from `origin/<branch>`, not the local copy.

## 4. Watch staging (PRs into staging only)

If the merge into staging deploys (the deploy target shows a deployment that includes the merge commit within about 5 minutes), watch it until it succeeds, then run the staging health check if a URL is known. If the deploy or the health check fails, stop: don't promote a broken staging deploy to production. If nothing deploys staging, move on.

If the run ends at staging (`--to staging`, or the user chose in step 0 to stop after staging), it ends here: go to step 7. Don't run the cleanup CLAUDE.md asks for once staging is done, such as taking staging services down, because people are about to test on staging. The report lists it as still pending.

## 5. Promote to production (PRs into staging, and resumed runs)

1. Reuse an open PR from staging into the default branch if one exists (`gh pr list --base <default> --head staging --state open`). Otherwise open one titled `Release: <one line>`, with a body listing what it promotes (`git log --oneline origin/<default>..origin/staging`). Link it as in step 1.
2. Run the review gate (step 2) on it with the same reviewers. A finding that needs code goes through a new branch off `origin/staging` and a PR into staging, which gets its own review gate and merge, and updates the release PR.
3. Merge it as in step 3 with the release merge method from step 0, without deleting staging. Record the merge commit SHA.
4. Check that staging still exists (`git ls-remote --heads origin staging`). If GitHub deleted it, recreate it at the head SHA recorded before the merge (`git push origin <sha>:refs/heads/staging`) and say so in the report.

## 6. Watch the production deploy

Using [deploy-targets.md](deploy-targets.md), poll every 30 seconds in a background Bash loop until every affected service reports a successful deployment that includes the merge commit, or one fails. Only services whose files changed may redeploy, so don't wait on the others. Then run the production health check when a URL is known, and follow any post-deploy rules from CLAUDE.md.

If the deploy or the health check fails, stop. Report the failing service and the end of its logs. Don't redeploy or revert on your own; offer to open a revert PR.

## 7. Report

Tell the user:

- what merged, with PR links and merge commit SHAs;
- which reviewers ran on each PR, which were off, and what the local review found if it ran;
- findings fixed, deferred (with issue links) or answered "by design", and any Known limitations;
- which services deployed, their status, and the health-check result;
- for a run that ended at staging: what staging now holds that production doesn't (`git log --oneline origin/<default>..origin/staging`), any staging cleanup from CLAUDE.md still pending, and how to promote it: check out staging, `git pull`, and run `/workflow-babysit`.

Then do whatever the arguments asked for once the change is live, which for a run that ended at staging means live on staging. If your client has a push-notification tool, send a one-line notification when the run finishes or stops.

## When to stop

Stop, say exactly where the run stopped and what it needs, and send a notification if you can, when:

- the user chose to stop in step 0;
- a person requested changes or asked a question on the PR;
- a blocking finding is still open after 3 review rounds, or can't be fixed;
- CI fails for a reason you can't fix, fails twice for an unrelated reason, or doesn't finish in time;
- GitHub refuses the merge, or the merge queue drops the PR twice;
- a rebase onto commits a bot pushed hits a conflict you can't resolve;
- a staging or production deploy or health check fails.

When stopping, also list any cleanup that CLAUDE.md asks for after a deploy and that hasn't run yet (for example, staging services still up), so the user can decide. Don't run it on a failed run, since the user may want to look at the failure first. To resume, the user runs the skill again: it picks up the open PR, or the release step when it's run from staging. A run that stopped on its way to staging needs `--to staging` again to end there.

## Rules

- Never force push, never merge with `--admin`, and never delete the staging or default branch.
- Never push to the default branch directly. Everything goes through a PR.
- Run `git pull --rebase` before every push, since a bot such as Bugbot Autofix may have pushed to the branch. It only replays your unpushed commits on top. If the rebase hits a conflict you can't resolve cleanly, `git rebase --abort` and stop.
- The only bot commands the skill posts are `@codex review` and `bugbot run`. Never mention `@cursor`, and never ask a bot to make a fix.
- Never commit secrets.
- The skill doesn't deploy, restart, scale or change environment variables on any host. Merging is what triggers the deploy. The only exception is a step CLAUDE.md asks for, such as starting staging services before a staging deploy.
- Poll no faster than every 30 seconds, and give every wait a deadline.

## Additional resources

- [reviewers.md](reviewers.md): detecting Claude Code, Codex and Cursor Bugbot, knowing when each is done, Bugbot Autofix, threads, triage and the local review fallback.
- [deploy-targets.md](deploy-targets.md): finding the deploy target, snapshots, watching GitHub deployments, GitHub Actions and Railway, and health checks.
