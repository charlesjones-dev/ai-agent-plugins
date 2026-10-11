---
name: swift-ci-scaffold
description: "Scaffold the repo side of Xcode Cloud for an XcodeGen / Tuist Swift project - generate ci_scripts/ci_post_clone.sh (regen + guarded CI_BUILD_NUMBER stamping), propose a unit-test-only CI scheme, print the exact App Store Connect workflow checklist, and optionally install an opt-in .githooks/pre-push gate. Shows diffs and confirms before writing."
argument-hint: "[path] [--hook]"
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion]
disable-model-invocation: true
---

# Swift CI Scaffolder

You prepare the **repo side** of Xcode Cloud for a generator-based Swift project, and you fix the two build-system blockers that `/swift-preflight` flags: a missing/weak `ci_post_clone.sh` and a static build number. You also optionally install a local pre-push gate.

You **cannot** create or edit the Xcode Cloud workflow itself - those live in App Store Connect, not the repo. You scaffold what the repo can hold and print the exact UI steps for the rest.

## Rules

- **Non-destructive.** Probe first, propose a diff, confirm, then write. Never overwrite an existing `ci_post_clone.sh`, `project.yml`, or hook without showing the change and getting a yes.
- **Preserve the source of truth.** On XcodeGen, edits go into `project.yml`, never the pbxproj. Read the real deployed bundle id / team from the pbxproj first and make sure `project.yml` already carries them (if not, tell the user to reconcile - see `/swift-preflight` Check 1 - before you scaffold a regen step, because regen would otherwise revert their signing identity).
- **Idempotent.** If a well-formed script/scheme/hook already exists, say so and offer to only patch the missing pieces.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

- `path` (optional) - repo root. Default: current working directory.
- `--hook` - jump straight to the pre-push hook step.

## Phase 0: Probe

Detect the generator (xcodegen / tuist), platforms, existing `ci_scripts/`, the app + unit-test + UI-test targets, and the current `CURRENT_PROJECT_VERSION`. If the project is a plain `.xcodeproj` (no generator) or SwiftPM library, tell the user this scaffolder is for generator-based app projects on Xcode Cloud and stop. Suggest they run `/swift-verify` (with the same path, if they gave one) for the local gate instead; it's a command-only skill, so you can't run it for them.

**Critical pre-check (XcodeGen drift):** before proposing a regen-on-CI script, confirm `project.yml` already declares the real `PRODUCT_BUNDLE_IDENTIFIER` and `DEVELOPMENT_TEAM` that the pbxproj uses:

```bash
grep -E 'PRODUCT_BUNDLE_IDENTIFIER|DEVELOPMENT_TEAM' *.xcodeproj/project.pbxproj | sort -u
```

If `project.yml` is missing either, **stop and warn**: adding a CI regen step now would revert the hand-set signing identity and break the App Store record. Have the user copy the real values into `project.yml` `settings.base` first.

## Phase 1: `ci_scripts/ci_post_clone.sh`

If absent or malformed, propose this (adapt generator and stamp target):

```sh
#!/bin/sh

# Xcode Cloud runs this immediately after cloning, before it resolves
# dependencies or reads the Xcode project. The .xcodeproj is generated from
# project.yml by XcodeGen, so we regenerate here to guarantee the build matches
# the spec (no stale/hand-edited pbxproj drift). We also stamp the build number
# from CI_BUILD_NUMBER so each TestFlight upload is unique.

set -e

# Xcode Cloud starts in ci_scripts/; the repo root is one level up.
cd "$CI_PRIMARY_REPOSITORY_PATH"

echo "Installing XcodeGen..."
brew install xcodegen

# Stamp the build number into the spec BEFORE generating, so the generated
# project carries a unique CFBundleVersion. Guarded so local builds (where
# CI_BUILD_NUMBER is unset) keep the spec value.
if [ -n "$CI_BUILD_NUMBER" ]; then
  echo "Setting CURRENT_PROJECT_VERSION to $CI_BUILD_NUMBER"
  /usr/bin/sed -i '' \
    "s/^\( *CURRENT_PROJECT_VERSION:\).*/\1 \"$CI_BUILD_NUMBER\"/" \
    project.yml
fi

echo "Generating Xcode project..."
xcodegen generate

echo "ci_post_clone complete."
```

After writing, set the executable bit: `chmod +x ci_scripts/ci_post_clone.sh`.

Notes to surface:

- The `sed` form above matches a `CURRENT_PROJECT_VERSION:` line in `project.yml`. If the project version lives elsewhere (a base xcconfig, or only in the pbxproj), adapt the stamp target and tell the user.
- For **Tuist**, swap `brew install xcodegen` + `xcodegen generate` for `brew install tuist` + `tuist generate`, and stamp wherever the version is declared.
- Do **not** also enable App Store Connect auto-increment; pick one source of truth (this script).

## Phase 2: Unit-test-only CI scheme

If a UI-test target exists and no unit-test-only shared scheme is present, propose adding one to `project.yml` `schemes:` (so it generates as shared). Example shape:

```yaml
schemes:
  App-CI:
    build:
      targets:
        App: all
        AppTests: [test]
    test:
      targets:
        - AppTests   # unit only — no AppUITests, so a flaky UITest can't gate a release
    run:
      config: Debug
    archive:
      config: Release
```

Explain: point the Xcode Cloud Test actions (iOS + macOS) at `App-CI`, keep the Archive action on the full `App` scheme. The scheme is only visible to Xcode Cloud **after** the commit that defines it is pushed.

## Phase 3: App Store Connect workflow checklist (print, cannot automate)

```
App Store Connect → your app → Xcode Cloud → Manage Workflows. Repo cannot hold these:

1. Start Conditions: Branch Changes on your release branch (e.g. `staging` or `main`).
2. Environment: select the Xcode version matching project.yml `xcodeVersion`.
3. Test action (iOS): scheme = App-CI, "Required to Pass". Repeat for macOS if you ship Mac.
4. Archive action: scheme = App (full), one per platform you distribute.
5. Skip Build and Analyze actions — Archive already does a full signed release build, and
   the Clang analyzer adds near-zero value for pure Swift (strict concurrency + swiftlint cover it).
6. Post action: TestFlight (internal) for iOS and/or macOS.
7. First run will surface environment-only test failures that pass locally
   (headless keychain writes). Fix test-side — see /swift-preflight Check 5 — not in production.
```

## Phase 4: Opt-in pre-push hook (only if user agrees, or `--hook`)

Offer, never force. If yes, write `.githooks/pre-push` (version-controlled, like a `.githooks/` convention) that runs the local gate before a push:

```sh
#!/bin/sh
# Pre-push gate: regenerate, format-check, lint strict, unit tests.
# Enable once per clone:  git config core.hooksPath .githooks
set -e
exec ./scripts/verify.sh   # or inline the /swift-verify pipeline if no verify.sh exists
```

If there is no `scripts/verify.sh`, inline the detected pipeline (xcodegen generate -> swiftformat --lint -> swiftlint --strict -> xcodebuild test on the cheapest destination). `chmod +x .githooks/pre-push`. Then tell the user to run `git config core.hooksPath .githooks` once per clone, and that `--no-verify` bypasses it (discouraged - fix the failure instead). Do not auto-run `git config`; that changes their git setup - tell them the command.

## Output

Summarize what was written (with the diff already shown and confirmed), what was skipped because it already existed, and the remaining manual App Store Connect steps. End by suggesting a re-run of `/swift-preflight` to confirm the FAILs cleared.
