# Reviewers

Every PR gets each of Claude Code, Codex and Cursor Bugbot that is on. Work out which are on before waiting on anything. Other review bots that show up on a PR (`coderabbitai[bot]`, `copilot-pull-request-reviewer[bot]` and so on) are triaged like the rest, but never waited on.

In the commands below, `{owner}/{repo}` comes from `gh repo view --json nameWithOwner`.

## Claude Code (GitHub Action)

### Is it on?

Check once per run, in step 0. It is on only if all three hold:

1. **Workflow on the default branch.** Find a workflow that runs `anthropics/claude-code-action` on pull requests:

   ```bash
   git fetch origin <default>
   git grep -l "anthropics/claude-code-action" "origin/<default>" -- .github/workflows
   ```

   Keep the files that trigger on `pull_request` or `pull_request_target`. Claude Code's built-in `/install-github-app` opens a PR that adds `claude.yml` (job `claude`), which answers `@claude` mentions, and optionally `claude-code-review.yml` (job `claude-review`), which reviews PRs. Ignore the first. The action only runs a workflow whose file matches the default branch, so a copy that exists only on a PR branch doesn't count.
2. **Credentials.** `gh secret list --repo {owner}/{repo} --json name` includes the secret that workflow reads: `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`. If the repo belongs to an organization and the secret isn't there, check `gh secret list --org <owner> --json name,visibility` as well, since an organization secret can serve the repo. Workflows that set `use_bedrock` or `use_vertex` authenticate through the cloud provider instead, so skip this check for them. If a call is refused (no admin rights), say you couldn't verify the secret and rely on the other two checks.
3. **Enabled.** `gh workflow list --all --json path,state` shows that path with `state` `active`, not `disabled_manually` or `disabled_inactivity`.
4. **Posts to the PR.** The review job has a way to put its findings on the PR: its prompt passes `--comment` to `/code-review`, it sets `use_sticky_comment` or `track_progress`, or its allowed tools include `mcp__github_inline_comment__create_inline_comment` or `gh pr comment`. Without one of those, the findings stay inside the Actions run, and a successful run with nothing on the PR would look like a clean review. Treat Claude Code as off, and tell the user to run `/install-github-app` again and pick "Update workflow file with latest version". Since Claude Code v2.1.229, the review workflow it writes posts inline comments, or one summary comment when it finds nothing.

The check run to wait on is named after the review job: its `name:` if it has one, otherwise the job ID (`claude-review` in the default workflow).

If the PR's diff edits that workflow file, the action will refuse to run on this PR (see below), so treat Claude Code as off for this run and ask in step 0.

Also note whether it re-runs on pushes. A `pull_request` trigger with no `types:` list runs on `synchronize` (a push to the PR). A `types:` list without `synchronize` means it reviews only when the PR opens. In that case, don't wait for it after a push. Run the local review fallback on the new commits instead, for the rest of that PR's rounds.

### Is it done?

It's done when the review check run on the head SHA has completed:

```bash
gh api "repos/{owner}/{repo}/commits/<sha>/check-runs" \
  --jq '.check_runs[] | select(.name=="<review job>") | {status, conclusion, details_url}'
```

A `success` conclusion doesn't prove a review happened. Find the run (`gh run list --commit <sha> --workflow <file> --json databaseId`) and grep its log (`gh run view <run-id> --log`) for `Skipping action due to workflow validation`. If it's there, Claude Code didn't review this PR. That happens when the PR edits the workflow file or the file isn't on the default branch yet.

Give it 30 minutes. A skipped review, a `failure` conclusion (often an expired token) or no result in time means Claude Code is off on this PR. Follow the step 0 answer if there was one. If step 0 found it on, so nobody was asked, don't stall: run the local review below in its place and say so in the report, unless CLAUDE.md says to stop.

### Findings

Inline review comments from `claude[bot]`, plus any findings in its top-level summary comment on the PR. A review workflow from `/install-github-app` in Claude Code v2.1.229 or later posts one summary comment when it finds nothing. That comment is a clean pass, not a finding. When it re-runs on pushes, never ask it for a re-review. After each push, wait for its check run on the new head commit and triage what that run posts.

It re-reviews the whole PR each time, not just the new commits, so it can raise a finding again after it was already fixed, deferred or answered "by design". Treat a repeat as already answered: reply with a link to the earlier thread or issue, resolve it, and leave the code alone. Raise it again only if the new commits really changed the answer.

## Codex (`chatgpt-codex-connector[bot]`)

### Is it on?

It is on if it reacts, comments or reviews on the PR within 3 minutes of the PR opening:

```bash
gh api "repos/{owner}/{repo}/issues/<N>/reactions" --jq '.[] | select(.user.login=="chatgpt-codex-connector[bot]") | .content'
gh pr view <N> --json comments,reviews \
  --jq '[.comments[], .reviews[]] | map(select(.author.login=="chatgpt-codex-connector")) | length'
```

The REST API reports the login as `chatgpt-codex-connector[bot]`, while `gh pr view` drops the `[bot]` suffix. If the PR is already older than 3 minutes with no Codex activity, or 3 minutes pass with none, treat Codex as off for the rest of the run, release PR included, and don't wait on it. Codex being off is not a reason to stop.

### Is it done?

A 👀 (`eyes`) reaction means Codex received the request, not that it finished. A pass is done when any of these shows up for the head commit:

- a Codex review or comment that says `Reviewed commit:` followed by a prefix of the head SHA;
- its pinned "Codex Review Summary" comment showing the Code Review row as Completed with the short SHA;
- a 👍 (`+1`) reaction from Codex and nothing else. When it finds no issues it may post no review at all, only that reaction, on the PR description or on the `@codex review` comment that asked for the pass. Check both. This counts as a clean pass.

Codex posts findings as several comments a few seconds apart. Don't act on the first one. Wait for its summary, or for two polls 30 seconds apart that show the same number of Codex comments.

Give it 15 minutes from the request: the PR opening, or your `@codex review` comment. Don't wait for the 👀 to start the clock. If no done signal arrives by then, say in the report that Codex didn't finish on that commit, and carry on without it for this round.

Codex reviews a PR by itself when it opens, not on later pushes. If Codex is on but the head commit has no pass and none was requested (a PR that got new commits before this run, or a reused release PR), request one as below.

### Re-review

After a round of fixes, or when the head commit has no pass, post one PR comment: `@codex review the latest commit (<sha>); scope strictly to this PR's diff`. Post exactly one per round, never one per thread, and never `@codex fix` or any other command. Claude makes every fix itself.

### Findings

Inline review comments from `chatgpt-codex-connector[bot]`, labelled P0, P1 or P2. Handle P0 first.

## Cursor Bugbot (`cursor[bot]`)

### Is it on?

It is on if a check run named `Cursor Bugbot` (app `cursor`) appears on the head commit within 5 minutes of the PR opening or of a push, or the PR already has a Bugbot review for any commit. In the second case, if the head commit has no run, request one as under Re-review:

```bash
gh api "repos/{owner}/{repo}/commits/<sha>/check-runs" \
  --jq '.check_runs[] | select(.name=="Cursor Bugbot") | {status, conclusion, title: .output.title, summary: .output.summary}'
```

If neither shows up, treat Bugbot as off for the rest of the run and don't wait on it. Bugbot being off is not a reason to stop. In step 0, a `Cursor Bugbot` check on the repo's last few PRs, or a `.cursor/BUGBOT.md` or `.cursor/config/bugbot.yaml` file, says it's probably on.

### Is it done?

It's done when the `Cursor Bugbot` check run on the head commit has completed and a Bugbot review names that commit. Bugbot reviews start with `<!-- BUGBOT_REVIEW -->` and end with `Reviewed by Cursor Bugbot for commit <full sha>`:

- `✅ Bugbot reviewed your changes and found no new issues!` is a clean pass. The check's conclusion is `success` when there are no issues and no unresolved Bugbot threads from earlier runs.
- `Cursor Bugbot has reviewed your changes and found N potential issues.` means findings, posted as inline comments. The check's conclusion is `neutral`, or `failure` if the repo makes unresolved findings fail the check.
- A `neutral` check with no review for the head commit means the run was cancelled by a newer push or hit an error. Wait for the run on the newer commit, or, if the head hasn't moved, carry on without Bugbot for this round and say so in the report.
- Reviews whose body has `<!-- BUGBOT_REVIEW_STALE -->` ("Stale Bugbot comment from a previous run.") are old runs. Ignore them.

Give it 20 minutes from the PR opening or the push.

### Re-review

By default Bugbot runs on every push and reviews only what changed since its last review, so it usually needs no request. If no `Cursor Bugbot` check run appears for the new head commit within 5 minutes (the repo runs it once per PR, or only when asked), post one PR comment: `bugbot run`. Post exactly one per round.

Don't write `@cursor` in any comment. A mention starts a Cursor agent that can push to the branch, and `@cursor remember` saves a review rule for the repo. `bugbot run` is the only Bugbot command the skill posts.

If the repo requires the Bugbot check and it ends in `failure` because findings are unresolved, resolving the threads doesn't change that run's result. Once every Bugbot thread is answered and resolved, post `bugbot run` so a new run can pass. A `neutral` conclusion counts as passing for a required check.

### Findings

Inline review comments from `cursor[bot]` that contain `<!-- BUGBOT_BUG_ID: ... -->`. Each one has:

- a `### <title>` heading and a `**High Severity**`, `**Medium Severity**` or `**Low Severity**` line. Handle High first;
- the description between `<!-- DESCRIPTION START -->` and `<!-- DESCRIPTION END -->`;
- any further locations in a `<!-- LOCATIONS START ... LOCATIONS END -->` block, listed under "Additional Locations". Check every location, not just the line the comment sits on.

Ignore the "Fix in Cursor" and "Fix in Web" links. Claude makes the fixes itself.

`cursor[bot]` posts other things too, and none of them are findings: Cursor Automations reviews (marked `<!-- CURSOR_AUTOMATION_ID`, sometimes an approval), Autofix results, and replies from Cursor agents. Only comments with a `BUGBOT_BUG_ID` go through triage. An approval from `cursor[bot]` isn't a person's approval.

Bugbot resolves its own thread when a later run sees the problem fixed. Still reply in each finding's thread with what happened and resolve it yourself, so the run doesn't depend on Bugbot's next pass. Bugbot reads the PR's comments as context, so a "by design" reply keeps it from raising the same thing again.

Bugbot may write a summary into the PR description. Don't overwrite it when editing the PR body.

### Autofix

With Bugbot Autofix on, a Cursor cloud agent fixes findings by itself. Its progress shows as a `Cursor Bugbot Autofix` check run, and its results as a `cursor[bot]` review or comment describing the fix (for example "Fixed the unit mismatch.") over the changed lines. It works in one of two modes:

- **Commit to existing branch**: it pushes commits to the PR branch. Before fixing Bugbot findings, wait for the `Cursor Bugbot Autofix` check on the head commit to complete. Then `git pull --ff-only` and read its commits, and only fix what it didn't. Its commits are part of the PR: the other reviewers review them, and you triage them like your own changes. If one is wrong, undo it with a normal commit. Before every push, `git pull --rebase` in case it pushed meanwhile, and never force push.
- **Create new branch**: it pushes the fix to a separate branch. Don't merge that branch or its PR. Fix the finding in this PR, and mention the Autofix branch in the report.

## Local review fallback

Use this when the user chose it in step 0, or when Claude Code turns out to be off on a PR mid-run.

After CI passes, invoke Claude Code's built-in `code-review` skill on the PR at `high` effort, for example with the arguments `high <N>`. Triage what it reports with the same bar as bot findings and fix what needs fixing. Then post one PR comment listing each finding and what happened to it, so the PR records the review. After each round of fixes, run it again on the new commits only, within the same 3-round limit. If the `code-review` skill isn't available, review `gh pr diff <N>` yourself with the same bar.

## Threads

List the findings with `gh api --paginate "repos/{owner}/{repo}/pulls/<N>/comments"`. Without `--paginate` you only get the first 30. Top-level findings have `in_reply_to_id == null`. Use `original_commit_id`, not `commit_id`, to tell which commit a finding was made against, because `commit_id` moves forward with each push.

Reply in the thread:

```bash
gh api "repos/{owner}/{repo}/pulls/<N>/comments/<comment-id>/replies" -f body="Fixed in <sha>: <what changed>"
```

Resolving needs GraphQL, because the REST API can't resolve a thread:

```bash
# list threads with their IDs and state
gh api graphql -f query='
  query($owner:String!,$repo:String!,$pr:Int!){
    repository(owner:$owner,name:$repo){
      pullRequest(number:$pr){
        reviewThreads(first:100){ nodes { id isResolved comments(first:1){ nodes { databaseId author { login } body path } } } }
      }
    }
  }' -F owner=<owner> -F repo=<repo> -F pr=<N>

# resolve one thread
gh api graphql -f query='
  mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread { isResolved } } }' -F id=<thread-id>
```

## Default triage

Use this unless CLAUDE.md has its own triage rules.

- **Fix now** only a correctness, data-loss, security or regression bug in code this PR changed. Push the fix and reply with the commit SHA and what changed.
- **Otherwise**, open a follow-up issue (`gh issue create`) and reply with its link, or reply "by design" with the reason.
- If a finding is wrong, say why instead of changing the code to make it go away.
- Every finding gets a reply, and every thread gets resolved.
