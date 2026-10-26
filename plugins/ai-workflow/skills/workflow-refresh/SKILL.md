---
name: workflow-refresh
description: "Brings an old pull request up to date and decides whether it should still exist. It reads what changed on the base branch since the PR diverged, then recommends REFRESH (rebase, resolve conflicts, test and push), REWORK or CLOSE, with evidence. Use when the user asks to rebase, refresh, revive or modernize an old PR, or asks whether a stale PR still makes sense."
argument-hint: "[PR number or URL] [--branch <name>]"
---

# /workflow-refresh - Refresh an old PR

Refresh the idea, not just the branch. A clean rebase doesn't prove that the PR still belongs in the product.

User provided: $ARGUMENTS

The arguments may name the PR. Otherwise use the current branch's PR (`gh pr view`). If there is none, ask which PR.

The arguments may also name another branch to rebase and push, with `--branch <name>`. The workflow-takeover skill does this when it continues the work on a replacement branch. Then steps 1 to 3 still judge the PR, step 4 rebases and pushes only that branch, and the PR's own branch is left alone.

## Guardrails

- Fetch before you start: the PR's base branch, its head branch, and any other branch the work depends on.
- Treat uncommitted changes in the current checkout as the user's. If the checkout is dirty or busy with other work, use a disposable worktree: `git worktree add --detach <tmp dir> <head SHA>`.
- A request to refresh, rebase or update the PR authorizes rebasing and pushing its branch. A question such as "does this PR still make sense?" authorizes only steps 1 to 3: report the disposition, and push nothing. Neither authorizes merging, closing, changing the base branch or adding scope.
- If the PR's author isn't the user (`gh api user --jq .login`), pushing rewrites someone else's branch. Push only if the user said to push to it. Otherwise ask, or leave the rebased branch local and report it.
- Push a rebased branch only with a lease tied to the head you recorded: `git push --force-with-lease=<branch>:<recorded head SHA> <push target> HEAD:<branch>`. Never force push without a lease. A branch that isn't on the remote yet, such as a new branch from the workflow-takeover skill, needs no force: `git push -u <push target> HEAD:<branch>`.
- The push target is `origin` for a PR from the same repository. For a PR from a fork, it's the fork's URL, `https://github.com/<headRepositoryOwner>/<headRepository>.git`, and you can push only when `maintainerCanModify` is true. Otherwise stop after the local rebase and report it.
- Post no PR comment unless the user asked for one. Format any comment you post with the workflow-pr-comments skill from this plugin.

## 1. Establish the PR's intent

```bash
gh pr view <N> --json url,state,isDraft,author,baseRefName,headRefName,headRepository,headRepositoryOwner,headRefOid,maintainerCanModify,mergeStateStatus,reviewDecision,statusCheckRollup,title,body,closingIssuesReferences,commits
```

Read the title, the body, linked issues, the commits, the review threads and the complete diff (`gh pr diff <N>`). Then state, in one or two sentences, the smallest coherent goal the PR was trying to reach. Judge the implementation only after that.

Fetch the PR's head, which works for forks too: `git fetch origin pull/<N>/head`. Record the head SHA and the merge base (`git merge-base origin/<base> <head SHA>`). With both, you can compare the PR's own changes and the later base changes separately.

## 2. Check what changed around it

```bash
git log --oneline <merge base>..origin/<base>
git diff <merge base> origin/<base> -- <files the PR touches>
```

Search merged and open PRs for a replacement or a competing change: `gh pr list --state all --search "<key terms from the title>"`, and the same search for the main paths the PR touches.

Look beyond overlapping lines:

- Has the same user-facing problem already been solved?
- Did APIs, types, schemas, dependencies or architectural boundaries change?
- Do both sides now claim ownership of the same behavior or invariant?
- Was the code the PR changes deleted, moved or deliberately simplified?
- Would landing the PR restore an old behavior, or create two ways to do the same thing?
- Is the original benefit still worth its maintenance cost?

A PR isn't current just because Git reports no conflicts.

## 3. Choose a disposition before pushing

- **REFRESH**: the goal is still useful and the implementation is still the right shape. Rebase, resolve conflicts, test and update the branch.
- **REWORK**: the goal is still useful, but a mechanical rebase would keep the wrong implementation. Describe the smallest credible rewrite, and stop before pushing unless the user also asked for the rework.
- **CLOSE**: the PR is superseded, obsolete, going the wrong direction, or no longer worth its cost. Cite concrete evidence and stop. Don't rebase an obsolete branch, and don't close the PR without the user's permission.

Be willing to recommend CLOSE. Age alone isn't evidence, and sunk effort isn't a reason to keep a PR alive.

## 4. Rebase without losing intent (REFRESH only)

With `--branch`, use that branch and its own head SHA wherever these steps say the PR's branch and the recorded head.

1. Start a local branch at the recorded head SHA (`git switch -c <branch> <head SHA>`), or a disposable worktree when the checkout is dirty (`git worktree add -b <branch> <tmp dir> <head SHA>`). With `--branch`, check out that branch instead.
2. Rebase its commits onto the freshly fetched base: `git rebase origin/<base>`.
3. Resolve each conflict by the PR's intent and the base branch's newer invariants. If a conflict shows a product or architecture disagreement, stop and reconsider the disposition instead of guessing.
4. Compare the commit series before and after: `git range-diff <merge base>..<recorded head SHA> origin/<base>..HEAD`. Then read the final diff against the base. Confirm that no intended behavior disappeared and that no behavior the base already has came back.
5. Run the repository's checks for the touched area. Tell real failures apart from failures that already happen on the base and from infrastructure flakes.
6. Push as the guardrails say, if they allow a push. If the lease fails, someone pushed meanwhile: fetch and reassess instead of overwriting their work.

Don't merge the PR.

## 5. Report

Lead with REFRESH, REWORK or CLOSE and the reason. Then summarize:

- the meaningful changes on the base branch;
- conceptual conflicts, or that you found none;
- the rebase and push result, if you did them;
- the checks you ran and their results;
- the decision or work that remains, with a link to the PR.

Keep observed facts apart from judgment. Say what you couldn't verify instead of claiming confidence you don't have.

---

Adapted from `modernize` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). See THIRD-PARTY-NOTICES.md in this plugin.
