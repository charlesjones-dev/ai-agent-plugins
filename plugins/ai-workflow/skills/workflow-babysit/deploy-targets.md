# Deploy targets

The skill never deploys anything. Merging triggers the host's own Git integration or a CI workflow, and this file covers how to find that deploy and watch it to the end. Reading deploy status is the only contact with any host.

## Find the target (step 0)

Check these in order. A repo can have more than one target (a frontend on one host and an API on another), so keep every one that matches.

1. **CLAUDE.md.** A deploy section naming the host, services or URLs is authoritative. Use it, and still use the sources below to watch.
2. **GitHub deployments.** Many hosts, including Vercel and Railway, report each deploy back to GitHub:

   ```bash
   gh api "repos/{owner}/{repo}/deployments?per_page=20" \
     --jq '.[] | {id, environment, sha: .sha[0:7], ref, creator: .creator.login, created_at}'
   ```

   Note each environment name and which branch it follows. The production environment is the one whose deployments match commits on the default branch, and a staging environment matches commits on staging. The creator (`vercel[bot]`, `railway-app[bot]` and so on) names the host.
3. **GitHub Actions.** A workflow that runs on pushes to the default branch (or staging) and deploys, judging by its name, its jobs, an `environment:` key, or deploy commands such as `flyctl deploy`, `wrangler deploy`, `aws`, `gcloud` or `kubectl`:

   ```bash
   gh run list --branch <default> --event push --limit 10 --json workflowName,headSha,status,conclusion
   ```

4. **Xcode Cloud.** Apple's CI builds apps for TestFlight and the App Store, and reports each build to GitHub as check runs from the `xcode-cloud` app, named `<product> | <workflow> | <action> - <platform>`. A repo with a `ci_scripts/` folder probably uses it. Look at the latest commit on each branch:

   ```bash
   gh api "repos/{owner}/{repo}/commits/<branch>/check-runs" \
     --jq '.check_runs[] | select(.app.slug == "xcode-cloud") | {name, conclusion}'
   ```

   A workflow that runs an Archive action on commits to staging or the default branch is that branch's deploy. GitHub doesn't show whether the workflow sends the build on to TestFlight, so treat the Archive as the deploy.
5. **A host CLI linked to the repo**, used alongside the sources above when it adds detail such as per-service status or logs. Railway is covered below. For other hosts, use their CLI only if it's installed and the repo is linked to it (`.vercel/project.json`, `fly.toml`, `netlify.toml`).
6. **None found.** Merge, then report that no deploy target was found and the deploy wasn't watched.

## Snapshot (before each merge that deploys)

Record the latest deployment ID per environment, per Railway service, and the latest deploy-workflow run ID, so an older success isn't mistaken for the new deploy.

## Watch (after the merge)

Poll every 30 seconds in a background Bash loop with a 45-minute deadline. If the deadline passes with a deploy still running, report it as still in progress rather than failed.

A host may deploy a later commit than yours if someone else merged right after. That still counts when it contains your merge commit: `git merge-base --is-ancestor <merge-sha> <deployed-sha>`.

### GitHub deployments

```bash
gh api "repos/{owner}/{repo}/deployments?sha=<merge-sha>" --jq '.[] | {id, environment}'
gh api "repos/{owner}/{repo}/deployments/<id>/statuses" --jq '.[0] | {state, environment_url, log_url}'
```

- `success` means done. `failure` or `error` means it failed. `queued`, `pending` and `in_progress` mean keep waiting.
- `inactive` means a newer deployment to the same environment replaced it. Check that the newer one succeeded and contains your commit.
- A monorepo can get one deployment per project for the same commit. Wait for every deployment that appears within about 5 minutes of the merge. Hosts with path filters skip projects the change didn't touch.
- No deployment for the merge commit within about 5 minutes means this environment didn't redeploy for this change.

### GitHub Actions

```bash
gh run list --commit <merge-sha> --json databaseId,workflowName,status,conclusion
gh run watch <run-id> --exit-status --interval 30
```

Run `gh run watch` in the background. On failure, `gh run view <run-id> --log-failed | tail -100` gives the error.

### Xcode Cloud

Xcode Cloud posts its check runs on the merge commit itself, usually within a minute of the merge, so no snapshot is needed.

```bash
gh api "repos/{owner}/{repo}/commits/<merge-sha>/check-runs" \
  --jq '.check_runs[] | select(.app.slug == "xcode-cloud") | {name, status, conclusion, details_url}'
gh api "repos/{owner}/{repo}/commits/<merge-sha>/status" \
  --jq '.statuses[] | {context, state, description}'
```

- Wait for every `xcode-cloud` check run on the commit. `completed` with `success` means done. `failure`, `cancelled`, `timed_out` or `action_required` means it failed. `queued` and `in_progress` mean keep waiting.
- The commit status has one entry per workflow (`<product> | <workflow>`) covering the whole build. The workflow is done when its state is `success`, and it failed on `failure` or `error`.
- No `xcode-cloud` check runs within about 5 minutes of the merge means no workflow builds this branch.
- Build logs aren't available through `gh`. On failure, report the failing check run's name and its `details_url`, which opens the build in App Store Connect.
- After the checks pass, App Store Connect still processes a TestFlight build for a few minutes before testers get it, and GitHub doesn't report that step. Say so in the report.

### Railway

Railway posts one GitHub deployment per environment (named like `Project / production`), not one per service, so use the CLI for per-service status. Run it from the repo root, where the project is linked.

- **Services and domains**: `railway status --json` lists the environments. Each one's `serviceInstances` gives `serviceName`, `domains.customDomains` and `domains.serviceDomains` (useful for health checks), and `latestDeployment`.
- **Deployments**: `railway deployment list --service <service> --environment <env> --limit 5 --json`. Match `meta.commitHash` to the merge commit. `SUCCESS` means done, and so does `SLEEPING` (a deployed service that went idle). `FAILED` and `CRASHED` mean it failed. `QUEUED`, `WAITING`, `INITIALIZING`, `BUILDING` and `DEPLOYING` mean keep waiting. `REMOVED` means a newer deployment replaced it, so check that the newer one succeeded and contains your commit. `SKIPPED`, or no new deployment within about 5 minutes of the merge, means the service's watch patterns didn't match the change, so don't wait on it.
- **Logs**: `railway logs --build --lines 100 <deployment-id>` for a failed build, or `railway logs --deployment --lines 100 <deployment-id>` for a crash after the build.

If CLAUDE.md lists services that must be running before a staging deploy (a database, a cache), check them with `railway deployment list` and start them first, as it says.

## Health check

Use a URL in this order: CLAUDE.md, then the service's custom domain or generated domain from the host, then `environment_url` from the GitHub deployment status. Skip `environment_url` when it points at the host's dashboard instead of the app; Railway's points at railway.com.

```bash
curl -fsS -o /dev/null -w '%{http_code} %{time_total}s\n' --max-time 20 "<url>"
```

Try up to 3 times, 10 seconds apart, since a CDN can take a moment to pick up a new deploy.

- 2xx or 3xx passes.
- 401 or 403 is inconclusive: the URL is behind a login or deployment protection (common on Vercel preview URLs). Say so in the report and carry on.
- Anything else, or no response, is a failed health check. Stop and report it. Don't revert.

## When a deploy or health check fails

Stop. Report the service, the deployment ID and status, the health-check result, and the last 50 or so log lines. Don't redeploy or revert. Offer to open a PR that reverts the merge.
