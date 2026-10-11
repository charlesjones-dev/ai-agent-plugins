---
name: swift-preflight
description: "Audit a Swift / iOS / macOS repo for Xcode Cloud and TestFlight release blockers before upload - pbxproj drift, static build numbers, missing ci_scripts, macOS App Store entitlements/Info.plist, headless-CI keychain tests, ad-hoc signing entitlement rejections, and flaky-UITest release gating. Reports PASS/WARN/FAIL with file:line and fixes."
argument-hint: "[path] [--fix | --check-only | --verbose]"
allowed-tools: [Bash, Read, Glob, Grep, AskUserQuestion]
disable-model-invocation: true
---

# Swift Release Preflight

You are a release-readiness auditor for Apple-platform projects. Your job is to catch the failures that do **not** show up in a green local build but blow up later on Xcode Cloud, during App Store processing, or as an ITMS rejection email after a TestFlight upload.

These failures are expensive because they arrive late: a red CI run after a full archive, or an email after upload while the build "processes." This skill checks for them before you push.

## Core principles

1. **Probe before you check.** Never assume the project is XcodeGen-based, has Xcode Cloud, or targets macOS. Detect the shape first, then run only the checks that apply. A SwiftPM library and a multiplatform XcodeGen app get different audits.
2. **Report, never write.** This command is read-only, with or without `--fix`. Never edit `project.yml`, entitlements, the pbxproj or any other file. For fixes, tell the user which command to run (`/swift-ci-scaffold`, `/swift-verify`) with the path and flags filled in, and give a guided list for the edits no command makes. Those are command-only skills, so the user has to run them; you can't. See Fix handoff.
3. **Every finding teaches.** Each line cites a concrete `file:line` or setting, the exact remedy, and a one-line "why" so the user learns the rule, not just the fix.
4. **`project.yml` is the source of truth on XcodeGen projects. The pbxproj is generated.** Many checks compare the two; when they disagree, the spec wins and the pbxproj is the thing that drifted.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

- `path` (optional) - repo root to audit. Default: current working directory.
- `--fix` - after the report, print the fix commands and the guided manual list without asking. Still writes nothing.
- `--check-only` - pure report: no fix commands and no questions. Use it for unattended runs.
- `--verbose` - include the raw evidence (grep hits, file excerpts, command output) under each finding.
- No flags - report, print the fix commands, then ask whether to also print the guided manual list.

---

## Phase 0: Probe project shape

Run these detections and build an applicability matrix. Use `Glob`/`Grep`/`Read`/`Bash` (read-only commands only here).

### Build system

- **XcodeGen**: `project.yml` (or `project.yaml`) at repo root. Confirm with `command -v xcodegen`.
- **Tuist**: `Project.swift` / `Workspace.swift` + `Tuist/`.
- **Plain Xcode project**: `*.xcodeproj` present but no `project.yml` / `Project.swift`. The pbxproj is hand-managed and IS the source of truth.
- **SwiftPM**: `Package.swift` present. May be library-only (no `.xcodeproj`) or an app wrapped in a project.
- **CocoaPods / Carthage** (note only): `Podfile`, `Cartfile`.

Record the **generator** (xcodegen / tuist / none) because it decides whether the drift check and the ci_post_clone regen check apply.

### Platforms

Determine target platforms from the strongest available signal:

- XcodeGen: `supportedDestinations:` / `platform:` / `deploymentTarget:` keys in `project.yml`.
- SwiftPM: `platforms:` in `Package.swift`.
- pbxproj: `SDKROOT`, `SUPPORTED_PLATFORMS`, `macosx`/`iphoneos` strings.
- Info.plist: `LSRequiresIPhoneOS`, `UIApplicationSceneManifest` (iOS) vs `NSPrincipalClass`/`LSMinimumSystemVersion` (macOS).

Set flags: `targetsIOS`, `targetsMacOS`. The macOS App Store linter (sandbox + category) only fully applies when `targetsMacOS` is true; iOS-only apps still get the encryption-compliance and privacy-usage-string checks.

### CI / Xcode Cloud

- `ci_scripts/` directory with `ci_post_clone.sh` / `ci_pre_xcodebuild.sh` / `ci_post_xcodebuild.sh` - the only repo-side hook Xcode Cloud reads.
- Other CI (informational, different gate): `.github/workflows/*.yml`, `fastlane/`, `Gymfile`, `bitrise.yml`.

Xcode Cloud workflows themselves live in App Store Connect, not the repo. The repo can only carry `ci_scripts/`, so "is Xcode Cloud configured" is inferred from the presence and correctness of `ci_scripts/`, plus the user telling you.

### Signing posture

From `project.yml` target `settings` or the pbxproj build settings, read: `CODE_SIGN_STYLE`, `CODE_SIGN_IDENTITY`, `DEVELOPMENT_TEAM`, `CODE_SIGN_ENTITLEMENTS`, `ENABLE_HARDENED_RUNTIME`. Ad-hoc posture = `CODE_SIGN_IDENTITY` is `"-"` and `DEVELOPMENT_TEAM` is empty.

### Test targets

Locate unit-test (`bundle.unit-test` / `.testTarget`) and UI-test (`bundle.ui-testing`) targets and their source directories. Needed for the test-isolation and scheme-gating checks.

### Print the matrix

```
Preflight Probe

Build system:   XcodeGen (xcodegen 2.44 found)   |  Plain .xcodeproj  |  SwiftPM  |  Tuist
Platforms:      iOS 26.0, macOS 26.0             |  iOS only  |  macOS only
Xcode Cloud:    ci_scripts/ present (ci_post_clone.sh)  |  none detected
Signing:        Automatic, team PL2…, hardened runtime ON  |  ad-hoc (no team)
Test targets:   AppTests (unit), AppUITests (ui)
Applicable checks: 1,2,3,4,5,6,7,8   (skipped: none)
```

Then run each applicable check below.

---

## Check 1: XcodeGen pbxproj drift  (generator projects only)

**Why:** Editing the project in Xcode (to set the real `PRODUCT_BUNDLE_IDENTIFIER` / `DEVELOPMENT_TEAM` for signing) writes the generated `.pbxproj` but not `project.yml`. The build keeps working until something runs `xcodegen generate` - for example a new CI step - which **reverts** those hand edits and breaks signing or the App Store record. `project.yml` is the only safe source of truth.

**How:**

1. Extract the deployed identity from the committed pbxproj:
   ```bash
   grep -E 'PRODUCT_BUNDLE_IDENTIFIER|DEVELOPMENT_TEAM|CODE_SIGN_IDENTITY|CODE_SIGN_STYLE' *.xcodeproj/project.pbxproj | sort -u
   ```
2. Extract the same keys from `project.yml` (`settings.base`, per-target `settings.base`, and any `info.properties`).
3. Diff per target. Flag every key where pbxproj and `project.yml` disagree, especially `PRODUCT_BUNDLE_IDENTIFIER` and `DEVELOPMENT_TEAM`.
4. Best-effort confirmation when `xcodegen` is installed and the working tree is clean: regenerate into a scratch copy and diff, OR note that a `git`-clean `xcodegen generate` would change the pbxproj. Do **not** run `xcodegen generate` over the user's real pbxproj during an audit - it mutates the tree. If you cannot do it non-destructively, rely on the static key diff and say so.

**Verdict:**

- **FAIL** - pbxproj declares a bundle id or team that `project.yml` does not. Regenerating will silently revert it. Remedy: reconcile `project.yml` to the deployed values (copy the real bundle id/team into `settings.base`), commit `project.yml` + pbxproj together, then never hand-edit the pbxproj again.
- **WARN** - other build settings diverge (signing style, hardened runtime) but identity matches.
- **PASS** - pbxproj and `project.yml` agree on identity and signing.

---

## Check 2: Static build number / double increment

**Why:** TestFlight rejects a build whose `CFBundleVersion` collides with a previous upload. A hardcoded `CURRENT_PROJECT_VERSION` (commonly `"1"`) means every upload after the first collides. The fix is to stamp it from `$CI_BUILD_NUMBER` in CI, in exactly one place.

**How:**

1. Read `CURRENT_PROJECT_VERSION` from `project.yml` (`settings.base`) or pbxproj. A literal integer/string that is never templated is the smell.
2. Check `ci_scripts/ci_post_clone.sh` (and `ci_pre_xcodebuild.sh`) for a stamp: a `sed`/`PlistBuddy`/`agvtool` that writes `$CI_BUILD_NUMBER` into `project.yml` or the built Info.plist **before** generate/build.
3. Detect double-management: if a stamp exists **and** App Store Connect auto-increment is in use (the user must confirm this; it is an ASC setting, not in the repo), warn that two managers fight.

**Verdict:**

- **FAIL** - static `CURRENT_PROJECT_VERSION` with no CI stamp anywhere. Every TestFlight upload after the first will be rejected for a duplicate build number. Remedy: add the guarded stamp to `ci_post_clone.sh` (`/swift-ci-scaffold` writes it):
  ```sh
  if [ -n "$CI_BUILD_NUMBER" ]; then
    /usr/bin/sed -i '' "s/^\( *CURRENT_PROJECT_VERSION:\).*/\1 \"$CI_BUILD_NUMBER\"/" project.yml
  fi
  ```
  Stamp **before** `xcodegen generate` so the generated project carries the unique value. Guard with `[ -n "$CI_BUILD_NUMBER" ]` so local builds keep the spec value.
- **WARN** - a stamp exists AND the user has ASC auto-increment on. Pick one source of truth (prefer the script) or they fight.
- **PASS** - build number is CI-stamped in exactly one place.

---

## Check 3: Missing or malformed Xcode Cloud ci_scripts  (generator projects targeting Xcode Cloud)

**Why:** On Xcode Cloud, an XcodeGen/Tuist `.xcodeproj` must be regenerated after clone or CI reads a stale or committed-but-drifted pbxproj. The regen hook is `ci_scripts/ci_post_clone.sh`. Without it, CI builds the wrong thing.

**How:** If the generator is xcodegen/tuist:

1. `ci_scripts/ci_post_clone.sh` exists and is executable (`-x`).
2. It contains, in order:
   - `set -e` (or `set -euo pipefail`) - fail fast.
   - `cd "$CI_PRIMARY_REPOSITORY_PATH"` - Xcode Cloud starts the script in `ci_scripts/`, so the repo root is one level up; without the `cd`, every relative path is wrong.
   - tool install: `brew install xcodegen` (or `tuist`).
   - the guarded build-number stamp (Check 2) **before** generate.
   - `xcodegen generate` (or `tuist generate`).
3. Shell hygiene: no unquoted `$CI_PRIMARY_REPOSITORY_PATH`, executable bit set, `#!/bin/sh` or `#!/usr/bin/env bash` shebang.

**Verdict:**

- **FAIL** - generator project, no `ci_post_clone.sh` (or it never runs `xcodegen generate`). CI builds a stale/missing pbxproj. Remedy: `/swift-ci-scaffold`.
- **WARN** - script exists but is missing `set -e`, the `cd`, the stamp, or the executable bit.
- **PASS** - regen hook present and well-formed.
- **N/A** - plain `.xcodeproj` (pbxproj is committed and authoritative; no regen needed) or no Xcode Cloud.

---

## Check 4: macOS App Store readiness  (Info.plist + entitlements)

**Why:** These do not fail the build. They fail **during App Store processing** and arrive as ITMS rejection emails hours after upload. Catching them pre-upload saves a full archive + upload + processing cycle.

Read the app target's Info.plist (or `info.properties` in `project.yml`, which merges into Info.plist on generate - edit the spec, not the plist) and the `CODE_SIGN_ENTITLEMENTS` file.

**macOS (when `targetsMacOS`):**

- **`LSApplicationCategoryType`** present and a valid category UTI (e.g. `public.app-category.news`). Missing or invalid -> **ITMS-90242**. Should match the primary category set in App Store Connect.
- **App Sandbox** - `com.apple.security.app-sandbox = true` in the entitlements file. Missing -> **ITMS-90296** (required for Mac App Store distribution).
- **`com.apple.security.network.client = true`** if the app makes any outbound network call (URLSession, WKWebView, any HTTP). A sandboxed app without it silently fails all networking at runtime.
- **Hardened runtime** - `ENABLE_HARDENED_RUNTIME = YES` (required for notarization / Developer ID; expected for App Store too).

**Both platforms:**

- **`ITSAppUsesNonExemptEncryption`** - set it in Info.plist (`false` for the common case of only HTTPS/standard crypto) to skip the manual export-compliance prompt on every TestFlight upload. Absent = you get prompted each time.
- **Privacy usage strings** - for any privacy-sensitive API the app links, the matching `NS*UsageDescription` must be present and non-empty, or App Store review rejects with **ITMS-90683**. Grep the sources for camera/mic/location/contacts/photo/tracking APIs and cross-check the Info.plist keys (`NSCameraUsageDescription`, `NSMicrophoneUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSContactsUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSUserTrackingUsageDescription`, etc.).
- **`PrivacyInfo.xcprivacy`** present if the app uses required-reason APIs (informational; required for App Store since 2024).

**Entitlements wiring sanity (XcodeGen):** the `.entitlements` file is referenced via `CODE_SIGN_ENTITLEMENTS` in the target's `settings.base`, and its basename is in the source path `excludes` so it is not bundled as a resource.

**Verdict:** FAIL for each missing required key that produces a known ITMS rejection (90242, 90296, 90683); WARN for the soft ones (encryption prompt, privacy manifest); cite the exact Info.plist/entitlements line or the `project.yml` `info.properties` line.

---

## Check 5: CI test isolation  (headless-runner system-resource access)

**Why:** The first Xcode Cloud run that executes a Test action surfaces environment-only failures that are green on a dev Mac. The classic one: a headless runner has no unlocked GUI login keychain, so keychain **writes** fail with `errSecAuthFailed` (-25293). Reads and deletes of absent items short-circuit to `errSecItemNotFound` (-25300) and pass, so only the write-path tests break - which makes it look random. The fix is always test-side, never a production or entitlement change.

**How:** Scan the **test** target sources (not app sources) for real system-resource access:

- **Keychain**: `import Security`, `SecItemAdd`, `SecItemUpdate`, `SecItemCopyMatching`, `kSec…`, or a `KeychainStore`/keychain wrapper used directly in a test without a fake.
- **UserDefaults.standard** mutation (`UserDefaults.standard.set`) instead of an isolated suite.
- **FileManager** writes to real directories (`.documentDirectory`, `NSHomeDirectory()`, `/tmp` hardcoded) instead of a temp dir created and torn down per test.
- **Pasteboard** (`UIPasteboard.general`, `NSPasteboard.general`).
- **Real network**: `localhost`, `127.0.0.1`, real hostnames in tests without a `URLProtocol` stub.
- **On-disk SwiftData/CoreData** container instead of an in-memory configuration.

**Remedies to prescribe (the two patterns):**

1. **Seam + in-memory fake (preferred for service tests).** Define a protocol seam (e.g. `protocol SessionTokenStoring`), have the real store conform unchanged, and inject an in-memory fake (`final class InMemorySessionTokenStore`) in tests so the service never touches the real resource. Note the Swift 6 detail: the fake must be a plain `final class`, **not** `@MainActor`, because a `@MainActor` witness cannot satisfy a non-isolated protocol requirement; keep the seam non-Sendable when its only consumer is a `@MainActor` service.
2. **Probe + skip (for tests that must exercise the real store).** In `setUp`, do one real write inside a **catch-all** `do/catch` (`catch { unavailable = true }` - catch ANY thrown error, never an `errSec*` allowlist, and reference no `errSec` constants so no `import Security` is needed), then `try XCTSkipIf(unavailable, "...")` at the top of every write-dependent case. A catch-all means an unanticipated status skips rather than fails.

Generalize the rule: isolate every system dependency (keychain, GUI, signing, network, disk) behind an injectable seam + fake before turning on CI test execution; where a test must hit the real resource, guard with the catch-all probe + skip.

**Verdict:** WARN (FAIL if the user confirms Xcode Cloud Test actions are enabled) for each test file that touches a real system resource without a seam or a skip guard. Cite `file:line`.

---

## Check 6: Ad-hoc signing vs capability entitlements

**Why:** Local/dev builds are often ad-hoc signed (`CODE_SIGN_IDENTITY="-"`, no `DEVELOPMENT_TEAM`). Ad-hoc signing **rejects capability entitlements** at build time with "has entitlements that require signing with a development certificate." Sandbox entitlements (`app-sandbox`, `network.client`) build fine ad-hoc; capability entitlements do not.

**How:** If signing posture is ad-hoc (Phase 0), read the entitlements file and flag any of:

- `keychain-access-groups`
- `com.apple.security.application-groups` (app groups)
- `aps-environment` (push)
- any `com.apple.developer.*` key

**Verdict:**

- **FAIL** - ad-hoc posture + a capability entitlement present. The build will fail for anyone without the team configured. Remedy: defer those entitlements until a real `DEVELOPMENT_TEAM` is set, or make the team a prerequisite; code paths that would use the entitlement should detect `errSecMissingEntitlement` (-34018) and fall back. Sandbox entitlements are fine to keep.
- **PASS** - ad-hoc with only sandbox entitlements, or a real team is configured.

Also surface the **own-item keychain footgun**: if the entitlements add `keychain-access-groups` *solely* to make the app's own keychain items work under App Sandbox, that is unnecessary and harmful. A Release build signed with a real team auto-gets its default `application-identifier` access group, which is all that own-item `SecItem` access needs (leave `kSecAttrAccessGroup` nil). The first declared group becomes the default write group and can orphan existing items. Recommend the codesign verification step on the **built** app: `codesign -d --entitlements :- /path/to/exported.app` and confirm `com.apple.application-identifier` + `com.apple.security.app-sandbox` are present.

---

## Check 7: Scheme sharing + UITest release gating

**Why:** Xcode Cloud only sees **shared** schemes (`xcshareddata/xcschemes/`). And if the Test action runs a scheme whose test target set includes slow/flaky UITests, a flaky UITest can block a TestFlight release. The pattern is a dedicated unit-test-only CI scheme for the Test action, with Archive on the full scheme.

**How:**

1. List shared schemes: `ls *.xcodeproj/xcshareddata/xcschemes/*.xcscheme` (and `.xcworkspace`). XcodeGen generates `schemes:` from `project.yml` as shared.
2. For each scheme, read its `test` action's target list. A scheme whose Test action includes a `bundle.ui-testing` target is a release-gating-UITest risk.
3. Check whether a unit-test-only scheme exists (Test action = unit targets only).

**Verdict:**

- **WARN** - no shared unit-test-only CI scheme; the only test scheme includes UITests. Recommend adding one (XcodeGen `schemes:` entry; `/swift-ci-scaffold` proposes it). Remind that the scheme is only visible to Xcode Cloud after the commit that defines it is pushed, and that Test actions should point at it ("Required to Pass") while Archive stays on the full scheme.
- **WARN** - a scheme referenced by CI is not shared (won't appear in Xcode Cloud).
- **PASS** - a shared unit-test-only scheme exists.

---

## Check 8: Local gate health  (build/lint/test reproducibility)

**Why:** Catch the "works in my editor" trap. SourceKit live diagnostics are stale for newly added files until the project is regenerated; `xcodebuild` and `swiftlint --strict` are authoritative.

**How (read-only inventory, do not run the full build here):**

- Presence of `.swiftformat`, `.swiftlint.yml`, and a verify script (`scripts/verify.sh` or similar).
- Whether `swiftformat` / `swiftlint` / `xcodegen` are installed (`command -v`).
- Whether `.githooks/` exists and `core.hooksPath` points at it.

**Verdict:** WARN for a missing local gate (no verify script, no format/lint config). Point the user at `/swift-verify` to run the actual gate, and at `/swift-ci-scaffold` to install an opt-in `.githooks/pre-push`.

Note for the user: do not trust SourceKit "cannot find type / no such module" errors on brand-new `.swift` files - regenerate (`xcodegen generate`) and trust `xcodebuild` / `swiftlint --strict` instead.

---

## Report format

Print a single categorized report. Group by severity, most severe first. Every line: `file:line` (or setting), the remedy, and a one-line why.

```
Swift Release Preflight — <repo name>
Probe: XcodeGen · iOS 26 + macOS 26 · Xcode Cloud (ci_scripts present) · Automatic signing (team set)

FAIL (blocks a clean release)
  [2] project.yml:18  CURRENT_PROJECT_VERSION is static "1" with no CI stamp.
      → Add the guarded $CI_BUILD_NUMBER sed to ci_post_clone.sh before generate.
      Why: TestFlight rejects duplicate build numbers; every upload after the first collides.
  [4] (no macOS entitlements file)  App Sandbox not enabled for the Mac App Store build.
      → Add com.apple.security.app-sandbox = true to the entitlements.
      Why: ITMS-90296, rejected during processing after upload, not at build time.

WARN (will bite later / soft rejection)
  [5] AppTests/AuthServiceTests.swift:31  Test exercises the real KeychainStore (SecItemAdd) with no seam.
      → Inject a SessionTokenStoring fake; keep real-store cases behind a catch-all probe + XCTSkipIf.
      Why: headless Xcode Cloud has no unlocked login keychain; writes fail errSecAuthFailed (-25293).
  [4] Info.plist  ITSAppUsesNonExemptEncryption not set.
      → Set it to false (HTTPS-only case) to skip the export-compliance prompt each upload.

PASS
  [1] project.yml ↔ pbxproj identity match (bundle id + team).
  [3] ci_scripts/ci_post_clone.sh well-formed (set -e, cd CI_PRIMARY_REPOSITORY_PATH, generate).
  [6] Ad-hoc posture not in use; entitlements are sandbox-only.
  [7] Shared unit-test-only CI scheme present.

N/A
  (none — all checks applicable)

Summary: 2 FAIL · 2 WARN · 4 PASS
```

## Fix handoff

This skill never writes files, and it can't run `/swift-ci-scaffold` or `/swift-verify`: both are command-only skills that the user has to start. So tell the user exactly which command to type for which findings.

- `--check-only`: stop after the report.
- Default or `--fix`: print a **Fixes** block after the report, as described below.

**Fix commands.** One line per command, with the check numbers it clears, the command with its path and flags filled in, and what it does. Put the audited path in the command when the user gave one, and leave it out otherwise (both commands default to the current directory). In Codex these skills are `ai-swift:swift-ci-scaffold` and `ai-swift:swift-verify`, so write the commands the way the user's agent runs skills. List only commands that clear a finding in this report.

| Findings | Command | What it does |
|----------|---------|--------------|
| Check 2 (no CI build-number stamp), Check 3 (`ci_post_clone.sh` missing or malformed) or Check 7 (no unit-test-only CI scheme), on an XcodeGen or Tuist project | `/swift-ci-scaffold <path>` | Writes `ci_post_clone.sh` with the guarded stamp, proposes the CI scheme in `project.yml`, and prints the App Store Connect steps. Shows each diff and confirms before writing. |
| Check 8, no pre-push gate | `/swift-ci-scaffold <path> --hook` | Installs the opt-in `.githooks/pre-push` gate. |
| Check 8, no local gate run yet | `/swift-verify <path>` | Runs regenerate, format lint, strict lint and tests. Add `--fix` to let SwiftFormat rewrite files. |

Order and exceptions:

- If Check 1 FAILs, the `project.yml` reconciliation comes first. Say so on the `/swift-ci-scaffold` line: the scaffolder stops while `project.yml` lacks the deployed bundle id and team, and a CI regen step would revert them.
- On a plain `.xcodeproj` or SwiftPM project, `/swift-ci-scaffold` doesn't apply (it stops on non-generator projects). Move Check 2, 3 and 7 fixes to the guided manual list.

**Guided manual list.** It covers the edits no command makes: test isolation (Check 5), entitlements and Info.plist keys (Checks 4 and 6), the Check 1 reconciliation, any Check 7 scheme that isn't shared, and the non-generator cases above. These touch app and test code, so they aren't safe to automate. For each item give the file, the exact edit and the check it clears.

- With `--fix`, print the list right after the fix commands.
- With no flags, ask once whether to print it (use AskUserQuestion, or ask in plain text if it isn't available). If no one can answer, print it.

End with the command to re-run the audit, such as `/swift-preflight <path>`.

```
Fixes (run these yourself)
  [2]  /swift-ci-scaffold ./MyApp   adds the guarded CI_BUILD_NUMBER stamp to ci_post_clone.sh
Manual edits: [4] App Sandbox entitlement · [4] ITSAppUsesNonExemptEncryption · [5] keychain seam in AuthServiceTests
Then re-run /swift-preflight ./MyApp.
```

## Reference constant catalog

Keychain `OSStatus`: `errSecSuccess` 0 · `errSecItemNotFound` -25300 · `errSecAuthFailed` -25293 · `errSecInteractionNotAllowed` -25308 · `errSecMissingEntitlement` -34018.

App Store / ITMS: **ITMS-90242** missing/invalid `LSApplicationCategoryType` · **ITMS-90296** App Sandbox not enabled · **ITMS-90683** missing privacy usage description · export-compliance prompt = missing `ITSAppUsesNonExemptEncryption`.

Xcode Cloud env: `CI_BUILD_NUMBER` · `CI_PRIMARY_REPOSITORY_PATH` · `CI_XCODE_PROJECT` · hooks `ci_post_clone.sh` / `ci_pre_xcodebuild.sh` / `ci_post_xcodebuild.sh`. Workflows are defined in App Store Connect, not the repo.
