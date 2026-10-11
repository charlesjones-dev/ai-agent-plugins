---
name: security-audit
description: "Evidence-based repository security audit with attack-surface coverage, candidate verification, baseline reconciliation, and archived Markdown/JSON artifacts."
disable-model-invocation: true
allowed-tools: [Bash, Read, Glob, Grep, Agent, Task, TaskOutput, TaskStop, SendMessage, AskUserQuestion, Write]
---

# Security Audit

Produce a defensible audit of the requested repository. Consistent coverage, evidence,
and visible uncertainty matter more than finding counts or agreement between reviewers.
This workflow cannot guarantee identical findings or the absence of vulnerabilities.
This skill runs the audit in the current session; `/security-cvp-audit`, in this plugin, plans one for a sandboxed session on a stronger model.

## Instructions

You are the **coordinator**. Read [methodology.md](references/methodology.md) for
the checks and decision rules, and [artifacts.md](references/artifacts.md) for the
versioned data contract and commands. Follow these stages in order:

1. **Establish scope and provenance.** Honor the user's paths, exclusions, budget,
   baseline selection, and existing authorization. Default to the current repository,
   including application code, jobs, scripts, configuration, and dependencies. Resolve
   the repository root explicitly; a supplied URL alone does not authorize an external
   penetration test. Read applicable repository guidance. Record revision, relevant
   dirty state, skill/plugin versions and hashes, exposed model/reviewer/tool identities,
   budget, and restrictions. Use `unknown` or `not exposed` for unavailable information.
   Read the [plugin manifest](../../.claude-plugin/plugin.json); distinguish a file
   not inspected from one verified missing. This skill is versioned with the plugin.
   Host file-access settings are operational context: missing Claude settings or a
   count of deny rules neither blocks the audit nor establishes an application flaw.
   Default to **repository review plus practical bounded local checks**. Inspect checked-in
   deployment configuration and external-service integration code, but do not require
   live infrastructure access, vendor dashboards, service provisioning, or end-to-end
   production tests unless requested. State this boundary up front; never narrow an
   explicitly requested scope to make the status complete.
2. **Inventory attack surfaces.** Use deterministic discovery where practical, then
   trace registration, framework conventions, shared middleware, and dynamic paths.
   Create surface IDs and applicable check obligations **before** reviewing candidates.
   Record discovery gaps, including unsupported languages and generated code. Expand
   the inventory as new paths emerge; searches alone cannot establish completeness.
3. **Discover candidates.** Review assigned surface/check pairs using the methodology.
   Preserve every substantive candidate in the ledger, including uncertain ones.
   Do fresh discovery before reading prior findings when practical; record any earlier
   exposure. In blind evaluation, never read baselines or evaluator expectations.
4. **Verify and challenge.** Perform a separate pass that actively attempts to disprove
   each candidate. Trace protections and practical reachability; use bounded local
   reproductions where useful. Record counterevidence, assumptions, validation results,
   and a reasoned disposition. Independent disagreement is evidence to investigate;
   consensus is not proof. Keep potentially serious unresolved issues conspicuous.
5. **Assess severity and priority.** Apply the qualitative rubric to demonstrated impact
   and prerequisites. Record confidence separately. Consolidate duplicate root causes
   while retaining all entry points and materially different impacts. Hardening is
   separate from confirmed vulnerabilities. Artifact v1 deliberately supports no numeric
   security or CVSS scores, compliance percentages, or overall security grade.
6. **Reconcile previous findings.** After fresh discovery, select the latest relevant
   baseline or the explicitly supplied reports. Account for every prior finding with
   evidence or an explicit unresolved status. Absence never implies fixed. Preserve IDs
   across severity changes; use the legacy mapping procedure in the methodology.
7. **Validate and render.** Write matching timestamped JSON and Markdown artifacts to
   `<audited-repository>/docs/security/YYYY-MM-DD-HHMMSS-security-audit.{json,md}`
   (repository-relative, never filesystem `/docs/security`). Record timezone; avoid
   overwriting earlier runs. Run the supplied validator and renderer. Inspect the
   rendered report for unsupported claims as well as structural errors. Use the default
   concise reading copy: summary and contents first, findings before coverage. Keep the
   full ledger and commands in JSON; do not append reviewer reports or raw records to
   Markdown. Follow the [report guidance](references/artifacts.md#human-readable-report).
   Release all audit-owned reviewers before final handoff. Apply the
   stopping rule below before final handoff; validation passing is not completion.

## Continue until the work is done or genuinely blocked

Before final handoff, revisit discovery gaps, unfinished surface/check pairs, unresolved
candidates, and unfinished baseline comparisons. If an authorized, feasible check can
advance any of them, perform it and update the evidence. Do not stop merely because
reports were saved, validation passed, findings seem sufficient, or substantial time
has elapsed. Do not invent a time budget when none was supplied.

Stop when the declared obligations are satisfied, the user stops or limits the work,
an actual execution limit is reached, or no remaining work can be advanced within
available access and authorization. A blocked production check does not block unrelated
local checks: finish those first, including source tracing when runtime tests are
unavailable. Avoid repeating inconclusive checks without a new approach or evidence.

Partial reports are checkpoints while feasible work remains. Preserve progress across
context limits where the host permits continuation; do not ask the user to say
“continue” for already authorized work. If final handoff must be partial or blocked,
record for each remaining gap what was attempted, the concrete blocker or reached limit,
and the next action or access needed. Explain why the audit stopped in the final reply.
Keep unresolved checks visible; never mark them reviewed merely to reach `complete`.

Completion means the **declared review work is finished**, not that every security
question is settled. A fully traced source check is reviewed even when it finds a flaw
or an optional runtime reproduction is unavailable. Keep external/vendor uncertainties
as `needs_validation` candidates and open questions with next steps; they need not
make a finished repository review partial. Unread in-scope code, incomplete control
traces, missing inventory, or unfinished requested tests still make it partial.
Use the [artifact status rules](references/artifacts.md#completion-and-follow-up);
do not put findings or routine provenance notes into unfinished-work fields.

## Delegation and host portability

Use at most **two live reviewers at a time** by default; smaller audits can run entirely
in the coordinator. Batch related surfaces into bounded assignments, not an agent per
file or finding. Exceed this cap only if the user explicitly requests more parallelism.
Prefer one-shot subagents over persistent teammates. In Claude Code, use the available
Agent/Task tool with `subagent_type: "ai-security:security-auditor"`; omit optional
teammate names/team setup. Keep models inherited. Pass scope, surface/check IDs, stage,
methodology references, artifact contract, verification candidates, budget, isolated
output location, baseline restrictions, and the instruction to return once and end.

The [reviewer](../../agents/security-auditor.md) reads supporting methodology, **never
reinvokes this skill or delegates further**. Reviewers return structured evidence and
coverage deltas, not standalone reports; the coordinator owns IDs, consolidation,
   severity, reconciliation, and the only final report pair.

Track every audit-owned agent/task ID and assignment. On return, collect the result,
merge its evidence, and check lifecycle state: a message or an idle notification is
not proof of termination. For a still-running finished worker, use the host's stop/close
tool (Claude Code: TaskStop); for a persistent teammate, request shutdown through its
supported protocol and check acknowledgement. A one-shot worker marked done needs no
extra shutdown message. Do not send thanks or status pings to finished workers: some
hosts resume them on any message. Follow up only for a concrete remaining assignment.
Use completion notifications or bounded waits; do not poll or wait indefinitely.
If a worker stalls, retain its available evidence, stop it, and finish or reassign the
unfinished checks within the cap. On cancellation, errors, and final handoff, check all
audit-owned IDs and stop remaining workers and their audit-started background tasks.
Never kill unrelated sessions or use broad process-name kills. Disclose a failed cleanup
with the exact ID; do not claim shutdown succeeded without host confirmation.

If the host cannot reliably track and finish delegated work, review sequentially in
the coordinator. The same fallback applies when delegation is unavailable; preserve a
distinct verification pass and identical coverage/evidence obligations. More detail on
Claude's [subagents](https://code.claude.com/docs/en/sub-agents) and
[teammate shutdown](https://code.claude.com/docs/en/agent-teams#shut-down-teammates).
Named Read/Glob/Grep/Bash tools may be replaced by
equivalent file/search/shell tools. Tool unavailability becomes a disclosed limitation,
not an invented result. Without Python, follow the contract manually and disclose that
machine validation was not run; do not claim a complete validated audit.

## Execution boundaries

Use authorized local, bounded testing with timeouts and disposable state. Do not stress
production, send real email, change live billing, or contact unrelated targets without
specific authorization. Preserve source and user changes; proposed fixes are proposals
until applied and tested. Do not install dependencies or use credentials merely to
make a report look complete. Redact secrets and personal data from artifacts while
retaining enough locations and evidence for review.
