# AI-Swift Plugin

**Swift / iOS / macOS release-readiness and quality toolkit for Claude Code, Codex and Cursor.** Catches the failures that pass a green local build but blow up later on Xcode Cloud, during App Store processing, or as an ITMS rejection email after a TestFlight upload.

---

## Why this exists

Failures like these pass a local build and only show up once the build reaches CI or the App Store:

- A red Xcode Cloud run, because the generated `.xcodeproj` drifted from `project.yml` or was never regenerated.
- A duplicate-build-number rejection on the second TestFlight upload, because `CURRENT_PROJECT_VERSION` was hardcoded.
- An ITMS rejection **email** hours after upload, because the Mac App Store build was missing App Sandbox or an app category, and neither fails the build.
- Unit tests going red on the first CI Test action with `errSecAuthFailed`, because a headless runner has no unlocked login keychain and keychain writes fail there but not on a dev Mac.

This plugin turns those failures into reusable checks. It's portable: it probes the target project's shape (XcodeGen vs plain `.xcodeproj` vs SwiftPM vs Tuist; iOS / macOS / both; Xcode Cloud or not) and only runs the checks that apply.

---

## What this plugin does

- **Pre-upload audit** (`/swift-preflight`): one report covering pbxproj drift, build numbers, ci_scripts, macOS App Store entitlements/Info.plist, CI test isolation, signing, and scheme gating.
- **Failure diagnosis** (`/swift-diagnose`): paste a red CI log or an ITMS email and get the root cause + exact fix.
- **CI scaffolding** (`/swift-ci-scaffold`): generate the Xcode Cloud repo-side wiring and an opt-in pre-push hook.
- **Local gate** (`/swift-verify`): run the right regenerate / format / lint / test pipeline for the project's build system.
- **Swift 6 review** (`/swift-concurrency-review`): catch strict-concurrency and SwiftUI idiom issues before the compiler does.

---

## Available Skills

### `/swift-preflight`  (report-only)

Audit the repo for Xcode Cloud / TestFlight release blockers. Probes the project shape, then runs every applicable check and prints a categorized **PASS / WARN / FAIL** report with `file:line`, the concrete remedy, and a one-line why.

It never writes files. After the report it tells you which command to run for which findings, with the path and flags filled in: `/swift-ci-scaffold` for ci_scripts, build-number and CI-scheme fixes, and `/swift-verify` for the local gate. It also offers a guided list for the edits no command makes, such as test isolation and entitlements. `--fix` prints that list without asking, and `--check-only` skips the fix section.

**Checks:**

| # | Check | Catches |
|---|-------|---------|
| 1 | XcodeGen pbxproj drift | bundle id / team / signing hand-edited in Xcode, will be reverted by a CI regen |
| 2 | Static build number | duplicate-build-number TestFlight rejection; double-increment fights |
| 3 | ci_scripts regen hook | CI building a stale/missing pbxproj on a generator project |
| 4 | macOS App Store readiness | ITMS-90242 (category), ITMS-90296 (sandbox), ITMS-90683 (usage strings), encryption prompt, network.client |
| 5 | CI test isolation | keychain / UserDefaults / disk / network access that breaks on a headless runner (errSecAuthFailed) |
| 6 | Ad-hoc signing vs entitlements | capability entitlements that reject ad-hoc builds; harmful keychain-access-groups |
| 7 | Scheme sharing + UITest gating | unshared schemes Xcode Cloud can't see; flaky UITests blocking releases |
| 8 | Local gate health | missing verify script / format-lint config; stale SourceKit trap |

**Usage:**

```
/swift-preflight
/swift-preflight ./MyApp --verbose
/swift-preflight ./MyApp --fix   # report, fix commands and the guided manual list
/swift-preflight --check-only    # report only, no questions; use for unattended runs
```

### `/swift-diagnose`  (report-only)

Reactive triage. Give it a red Xcode Cloud build log, an ITMS rejection email, or a bare code (`ITMS-90296`, `-25293`) and it maps the symptom to root cause and prescribes the fix, grounded in your repo files when available.

```
/swift-diagnose ITMS-90296
/swift-diagnose ./ci-build.log
/swift-diagnose   # then paste the failing log / email
```

### `/swift-ci-scaffold`  (writer, diff + confirm)

Scaffold the repo side of Xcode Cloud for an XcodeGen / Tuist project: generate `ci_scripts/ci_post_clone.sh` (regen + guarded `CI_BUILD_NUMBER` stamping), propose a unit-test-only CI scheme in `project.yml`, print the exact App Store Connect workflow checklist, and optionally install an opt-in `.githooks/pre-push` gate. Shows every diff and confirms before writing. Refuses to add a CI regen step if `project.yml` is missing the real bundle id / team (which regen would revert).

```
/swift-ci-scaffold
/swift-ci-scaffold --hook
```

### `/swift-verify`  (report-only; `--fix` rewrites)

The portable local gate, adapting to the build system: `xcodegen generate` (if applicable) -> `swiftformat --lint` -> `swiftlint --strict` -> `xcodebuild test` on the cheapest valid destination (macOS for pure-Swift), or `swift build` / `swift test` for SwiftPM.

```
/swift-verify
/swift-verify --fix
/swift-verify --no-test
/swift-verify --destination="platform=iOS Simulator,name=iPhone 16"
```

### `/swift-concurrency-review`  (report-only)

Swift 6 strict-concurrency + SwiftUI idiom review of the changed files (or a given path): Sendability across actor boundaries, `@MainActor` witness vs nonisolated requirement, Combine/`ObservableObject` reintroduction, force-unwraps, `#Predicate` macro limits, the 6.3.x `Binding` IRGen crash, missing `#if os()` guards, and unsafe escape hatches. Defers general bug-finding to `/code-review`.

```
/swift-concurrency-review
/swift-concurrency-review ./MyApp/Services
```

---

## Failure-to-check map

Each check targets a failure like these:

| Failure | Surfaced as | Caught by |
|---|---|---|
| Hand-edited bundle id / team in Xcode would be reverted by CI regen | broken signing / App Store record | `/swift-preflight` 1 |
| `CURRENT_PROJECT_VERSION` hardcoded `"1"` | duplicate-build-number rejection | `/swift-preflight` 2, `/swift-ci-scaffold` |
| No `ci_post_clone.sh` on an XcodeGen + Xcode Cloud project | stale/missing pbxproj on CI | `/swift-preflight` 3, `/swift-ci-scaffold` |
| Missing `LSApplicationCategoryType` / App Sandbox | ITMS-90242 / ITMS-90296 email | `/swift-preflight` 4, `/swift-diagnose` |
| Tests writing to the real keychain | `errSecAuthFailed` (-25293) on headless CI | `/swift-preflight` 5, `/swift-diagnose` |
| `keychain-access-groups` added for own-item access under sandbox | orphaned keychain items | `/swift-preflight` 6 |
| Capability entitlement on an ad-hoc build | "requires a development certificate" | `/swift-preflight` 6, `/swift-diagnose` |
| Flaky UITests in the release Test action | blocked TestFlight release | `/swift-preflight` 7, `/swift-ci-scaffold` |
| Phantom "cannot find type" on new `.swift` files | stale SourceKit | `/swift-preflight` 8, `/swift-verify` |

---

## Plugin Details

- **Name:** AI-Swift
- **Version:** 2.0.0
- **Type:** Swift / iOS / macOS Release-Readiness & Quality Toolkit
- **Features:**
  - Skills: `/swift-preflight`, `/swift-diagnose`, `/swift-ci-scaffold`, `/swift-verify`, `/swift-concurrency-review`
- **License:** MIT
- **Author:** Charles Jones

---

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-swift@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-swift@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-swift`. See the [Cursor install steps](../../README.md#cursor).

Optional tooling the skills use when present (install with Homebrew): `xcodegen`, `swiftformat`, `swiftlint`. `xcodebuild` / `swift` ship with Xcode.

---

## Important Notes

### What this plugin doesn't do

- Create or edit Xcode Cloud workflows, which live in App Store Connect (the plugin preps the repo and tells you the UI steps)
- Upload to TestFlight or submit to the App Store
- Replace an archive + upload + processing cycle
- Manage code-signing certificates or provisioning profiles

### Conventions it assumes

The checks target Swift 6 / SwiftUI / XcodeGen projects and don't hardcode any project's identifiers. SwiftPM-only repos skip the Xcode Cloud and entitlements checks, iOS-only repos skip the macOS App Store linter, and non-generator projects skip the drift and regen checks.

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License - See [LICENSE](LICENSE) file for details.
