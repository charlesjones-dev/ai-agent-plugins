---
name: workflow-claude-actions
version: 1.0.0
description: |
  Sets up or updates the Claude Code GitHub Actions in the current repo so PR
  reviews post inline comments and both workflows run on the newest Opus. Edits
  existing workflows in place, copies the bundled ones when they're missing, and
  opens one PR after the user approves the diff. Use when the user wants Claude
  Code review set up, fixed or moved to the latest Opus on a repo, or when
  /workflow-babysit reports that Claude Code review is off.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - AskUserQuestion
---

# /workflow-claude-actions - Claude Code GitHub Actions on the newest Opus

This builds on Claude Code's built-in `/install-github-app`. The result is two workflows:

- a **review workflow** that runs the `code-review` plugin on every PR and posts its findings as inline comments;
- a **mention workflow** that answers `@claude` in issues, PR comments and reviews.

Both pass `--model opus`. The alias resolves to the newest Opus that the action's bundled Claude Code knows about, and `anthropics/claude-code-action@v1` is a floating tag, so new Opus releases are picked up without editing the files. Pinning the action to a SHA or exact version, or setting `ANTHROPIC_MODEL` or `ANTHROPIC_DEFAULT_OPUS_MODEL`, stops that.

The bundled workflows are in `${CLAUDE_SKILL_DIR}/assets/`: `claude-code-review.yml` and `claude.yml`.

This skill may create one branch, change workflow files under `.github/workflows/`, push the branch and open one PR, and it does that only after the user approves the diff in step 3. It never merges, never changes other files, and never changes repo settings or secrets. The user sets any secret themselves.

## 1. Look at the repo

1. `gh repo view --json nameWithOwner,defaultBranchRef,viewerPermission,isPrivate`.
2. `git status --porcelain` must be empty. If it isn't, stop and ask the user to commit or stash first. Record the current branch so you can switch back at the end.
3. **Base branch**: if the repo's CLAUDE.md names an integration branch that work lands on, or recent PRs into the default branch come from a `staging` (or `develop`) branch, target that branch. Otherwise target the default branch.
4. **Existing workflows**: find the Claude workflows on the base branch by content, not filename:

   ```bash
   git fetch origin <base>
   git grep -l "anthropics/claude-code-action" "origin/<base>" -- .github/workflows
   ```

   - A file that triggers on `pull_request` (or `pull_request_target`) and reviews PRs is a **review workflow**.
   - A file that triggers on `issue_comment`, `pull_request_review_comment`, `pull_request_review` or `issues` and checks for `@claude` is a **mention workflow**.
   - One file can be both. It counts as both, so don't copy the other bundled file.
   - Other Claude workflows (issue triage, CI fixes, scheduled jobs) are out of scope. Leave them alone, and mention them in the report.
5. For each review or mention workflow, look at **every** step that uses the action (a file can have several jobs or steps) and note:
   - **The action ref.** `@v1` floats. A SHA or an exact version such as `@v1.0.12` is pinned.
   - **Pre-v1.** `@beta`, `@v0` or any `v0.x` ref, or pre-v1 inputs (`direct_prompt`, `override_prompt`, `model`, `allowed_tools`, `disallowed_tools`, `custom_instructions`, `mode`, `max_turns`, `claude_env`, `mcp_config`, `timeout_minutes`) mean the old action, which has no `claude_args` input.
   - **The auth setup.** `claude_code_oauth_token`, `anthropic_api_key`, or another setup: `use_bedrock`, `use_vertex`, `use_foundry`, or `anthropic_federation_rule_id` (workload identity federation). The other setups also rely on env vars or credential steps.
   - **The model.** `claude_args` and any `--model` (or `--model=`) in it, and any `ANTHROPIC_MODEL` or `ANTHROPIC_DEFAULT_OPUS_MODEL` in the step's, job's or workflow's `env:`. `ANTHROPIC_MODEL` overrides `--model`.
   - **For the review workflow, whether it posts to the PR.** It does if it has `--comment` in a `/code-review` prompt, the `mcp__github_inline_comment__create_inline_comment` tool, or a custom prompt that comments with `gh pr comment`.
   - **For the review workflow on a public repo, whether it skips fork PRs and bot PRs.** Fork PRs get no OIDC token or secrets, and the action refuses PRs from bots such as Dependabot, so without a guard those PRs get a red check.
   - **Its state** in `gh workflow list --all --json path,state`.
6. **Claude GitHub App**: a user token can't see whether the app is installed. A recent comment or review by `claude[bot]` in the repo proves it is:

   ```bash
   gh api "repos/{owner}/{repo}/issues/comments?sort=created&direction=desc&per_page=100" --jq '[.[] | select(.user.login=="claude[bot]")] | length'
   gh api "repos/{owner}/{repo}/pulls/comments?sort=created&direction=desc&per_page=100" --jq '[.[] | select(.user.login=="claude[bot]")] | length'
   ```

   A successful run doesn't prove it, because a run skipped by workflow validation also ends in `success`.

## 2. Ask everything at once

Collect what applies and ask it in one AskUserQuestion call:

- **Claude GitHub App**: unless step 1.6 proved it's installed, ask whether it's installed on this repo. If not, or they're unsure, send them to https://github.com/apps/claude to add the repo, and wait for them to confirm.
- **Auth for new workflows**: when you're copying a bundled workflow and no existing Claude workflow sets the auth, ask which they use:
  - **Claude subscription token (Recommended)**: `CLAUDE_CODE_OAUTH_TOKEN`. Runs count against their Claude plan.
  - **Anthropic API key**: `ANTHROPIC_API_KEY`. Runs bill to their API account, and Opus costs more per review than smaller models.
- **A different model already set**: if `--model` names something other than `opus`, or `ANTHROPIC_MODEL` or `ANTHROPIC_DEFAULT_OPUS_MODEL` is set, show it and ask whether to switch to `opus` or keep it.
- **Pinned action**: if a v1 action is pinned to a SHA or exact version, say the Opus alias won't pick up new releases while it's pinned, and ask whether to move it to `@v1`.
- **Pre-v1 action**: don't migrate it by hand, because the inputs changed. Recommend running the built-in `/install-github-app` to regenerate the workflows on `@v1` and then running this skill again. Ask whether to stop here for that, or skip that workflow.
- **Fork and bot guard** (public repos): if the review workflow has no guard, ask whether to add one.
- **A review workflow that can't post**: if it uses a custom prompt with no way to comment, show the bundled review workflow and ask whether to replace the file with it, keeping their auth setup.

## 3. Make the changes

1. `git switch -c update-claude-github-actions origin/<base>` (use `add-claude-github-actions` when nothing existed). Add a numeric suffix if the branch exists. From here on, whenever the skill stops early, switch back to the branch recorded in step 1 and delete the new branch if nothing was pushed.
2. **Workflows that exist: edit in place.** Keep their triggers, filters, permissions, auth and comments. For every action step in the review and mention workflows, only:
   - **Model**: if there's no `--model`, add `--model opus` to `claude_args`. If there's no `claude_args`, add `claude_args: '--model opus'` to the step's `with:` block, at the same indent as the other inputs. If the user chose to switch, replace the existing value (`--model x` or `--model=x`) with `opus`, and remove `ANTHROPIC_MODEL` and `ANTHROPIC_DEFAULT_OPUS_MODEL` from the env. If they chose to keep it, leave the model alone.
   - **Posting** (review workflow running the `code-review` plugin): add `--comment` right after `/code-review:code-review` in the prompt if it's missing. Make sure `claude_args` allows `mcp__github_inline_comment__create_inline_comment`: add it to an existing `--allowedTools` or `--allowed-tools` list, or add `--allowedTools mcp__github_inline_comment__create_inline_comment`. The tool name needs no quotes, so don't add any; quotes inside a double-quoted YAML string would end it.
   - **Block scalars**: if `claude_args` is a block scalar (`|` or `>`), add each new flag as its own line at the block's existing indent.
   - **Comment**: put `# \`opus\` tracks the newest Opus the action's bundled Claude Code knows about.` on the line above `claude_args`, as in the bundled files.
   - **Guard and ref**: apply what the user chose in step 2. For the guard, add `github.event.pull_request.head.repo.full_name == github.repository && github.event.pull_request.user.type != 'Bot'` to the review job's `if:`, joined with `&&` if it already has one, or copy the bundled file's `if:` line.
3. **Workflows that are missing: copy the bundled file** to `.github/workflows/`, verbatim. Use the same name unless a different file of that name exists. The auth line is the only change:
   - For API-key auth, replace `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` with `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`.
   - When the other Claude workflow already exists, match its auth. For a token or key, that's the one input. For Bedrock, Vertex, Foundry or federation, copy its whole auth setup (the inputs, the `env:` and any credential steps), or ask the user if it isn't clear what to copy.
4. **Check the YAML**: parse every edited or copied file with whatever is installed, for example `ruby -ryaml -e 'YAML.load_file(ARGV[0])' <file>`, `yq '.' <file>`, or `python3 -c 'import sys, yaml; yaml.safe_load(open(sys.argv[1]))' <file>`. Run `actionlint` too if it's installed. Fix anything that fails before going on.
5. If nothing needs to change, because every workflow already runs `opus`, the review workflow posts to the PR and nothing else was chosen, say so, switch back, delete the new branch, and stop.
6. **Approval**: show the full diff and ask with AskUserQuestion whether to commit it and open the PR. If the user declines, switch back, delete the branch, and stop.

## 4. Check the secret

Skip this when the workflows use Bedrock, Vertex, Foundry or federation.

1. Work out which secret the workflows read: `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`.
2. Check the repo: `gh secret list --repo <owner/repo> --json name`. If it isn't there and the owner is an organization, check `gh secret list --org <owner> --json name,visibility,selectedReposURL`. An organization secret counts as set when its visibility is `all`, or `private` on a private repo, or `selected` with this repo in `gh api <selectedReposURL> --jq '.repositories[].full_name'`.
3. If a list call is refused, the user doesn't have the access to see secrets. Say so and ask them to confirm with a repo admin that the secret exists. Don't block on it.
4. If the secret is missing, the user sets it. Setting a repo secret needs admin access (`viewerPermission` `ADMIN`). Never ask for the token or key in chat, never echo it, and never pass it on a command line. Tell them to run, in their own terminal:

   ```sh
   # Subscription token
   claude setup-token                                          # skip if they already have one; one token works for every repo
   gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <owner/repo>   # paste the token at the prompt

   # Or an API key from the Anthropic Console
   gh secret set ANTHROPIC_API_KEY --repo <owner/repo>         # paste the key at the prompt
   ```

   Then re-run `gh secret list` to confirm before going on.

## 5. Commit, push, PR

1. Follow the repo's own pre-commit rules (its CLAUDE.md, a verify gate before every commit). Never `--no-verify`. If a hook fails and you can't fix it within `.github/workflows/`, stop.
2. Commit with a message in the repo's style, such as "Run the Claude Code workflows on the latest Opus" or "Add Claude Code workflows on the latest Opus". Follow CLAUDE.md and your client's instructions on attribution.
3. `git push -u origin HEAD`. If GitHub refuses with "refusing to allow an OAuth App to create or update workflow … without `workflow` scope", have the user run `gh auth refresh -h github.com -s workflow`, then push again.
4. `gh pr create --base <base> --title "<title>" --body "<body>"`, with a body of two or three lines saying what changed. When the base isn't the default branch, add that Claude Code reviews will skip every PR into that branch until this change is promoted to the default branch. If your client has a tool for linking pull requests to the session, link the PR.
5. Switch back to the branch recorded in step 1.

## 6. Tell the user what to expect

- **This PR's review check passes without reviewing anything.** The log says "Workflow validation failed. The workflow file must exist and have identical content to the version on the repository's default branch." The action only runs a workflow whose file matches the default branch, so the new setup takes effect once this reaches the default branch. In repos that merge through staging, Claude Code reviews skip every PR into staging from the moment this lands there until it's promoted, so promote it soon. Any later edit to these files skips the review on the PR that makes the edit, for the same reason.
- **Bot reviewers may flag `pull-requests: read` or `contents: read` as a serious finding** ("can't post comments" or "can't push changes"). That's a false positive. With no `github_token` input, the action exchanges the OIDC token (`id-token: write`) for a Claude GitHub App token and posts as `claude[bot]`. That token's access comes from the app installation. The job's `permissions:` block only scopes `GITHUB_TOKEN`, which these workflows never use to write. Reply with that and don't grant write.
- **A disabled workflow** (state `disabled_manually` or `disabled_inactivity`) won't run even after this merges. Tell the user to re-enable it with `gh workflow enable <file>`. Don't do it yourself.
- **To confirm the model**: on the first real review run after the merge, search the review job's log for `modelUsage`. It should list a `claude-opus-*` model. A Haiku entry beside it is normal, because Claude Code uses Haiku for small background tasks.

## Rules

- One branch and one PR, opened only after the user approves the diff. Never merge it, and never change files outside `.github/workflows/`.
- Never ask for, print or pass a token or API key. The user sets secrets in their own terminal.
- Never change repo settings: don't enable workflows, install apps or set secrets.
- Keep the user's existing workflow customizations. Edit only the lines step 3 names.
- Whenever the run stops after creating the branch, switch back to the original branch.
- The bundled files are the template for new repos. To roll a later change out to repos that already have the workflows, run this skill again in each one.
