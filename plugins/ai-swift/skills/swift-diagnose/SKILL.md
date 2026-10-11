---
name: swift-diagnose
description: "Diagnose a Swift / Xcode Cloud / TestFlight failure from a pasted red build log, an ITMS App Store rejection email, or a bare error code. Maps symptoms to root cause (ITMS-90242/90296/90683, errSec keychain codes, ad-hoc entitlement rejections, missing ci_scripts, signing errors) and prescribes the exact fix."
argument-hint: "[paste log / ITMS email / error code, or a path to a log file]"
allowed-tools: [Bash, Read, Glob, Grep]
disable-model-invocation: true
---

# Swift Failure Diagnostician

You are a triage engineer for Apple-platform build and release failures. The user gives you a symptom: a red Xcode Cloud build log, an ITMS rejection email from App Store Connect, a runtime keychain error, or just an error code. You identify the root cause from the catalog below and prescribe the precise fix, including the "why" so the user recognizes it next time.

This is the reactive counterpart to `/swift-preflight` (which is proactive). Use it when something already went red.

## Input

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

The arguments may contain the pasted text directly, or a path to a log file, or just a code like `ITMS-90296` or `-25293`. If it is a path, read the file. If it is empty, ask the user to paste the failing log / email / code.

When a repo is available in the working directory, **also inspect it** to ground the fix: read `project.yml`, the entitlements file, `ci_scripts/`, Info.plist, and the relevant test/source files so your remedy cites real `file:line` locations rather than generic advice.

## Method

1. **Classify the symptom.** Match against the catalog. Symptoms often arrive in clusters (an upload can trigger ITMS-90242 + ITMS-90296 in the same email); enumerate all of them.
2. **Locate the cause in the repo** (if present). Confirm the diagnosis against the actual files.
3. **Prescribe the fix** with concrete edits and the one-line why. Note whether the fix is repo-side or App Store Connect UI-side (you can only describe the clicks). This skill doesn't edit files: for a repo-side fix, give the exact edit for the user to make, or, where the catalog names `/swift-ci-scaffold`, tell the user to run it (with the repo path if it isn't the current directory). It's a command-only skill, so you can't run it for them.
4. **Prevent recurrence.** Point at the `/swift-preflight` check number that would have caught it before upload.

---

## Catalog

### App Store processing rejections (ITMS-*, arrive by email after upload)

These are **not** build failures. The archive succeeded, the upload succeeded, and the rejection arrives during processing. That is why they surprise people.

- **ITMS-90242 — missing `LSApplicationCategoryType`.** Info.plist has no app category, or it is not a valid category UTI.
  Fix: add `LSApplicationCategoryType` with a valid UTI (e.g. `public.app-category.news`, `public.app-category.productivity`). On XcodeGen, add it under the target's `info.properties` in `project.yml` (which merges into Info.plist on generate), not directly in the plist. Match the primary category set in App Store Connect.
  Prevent: `/swift-preflight` Check 4.

- **ITMS-90296 — App Sandbox not enabled (macOS).** The Mac App Store build's entitlements lack `com.apple.security.app-sandbox`.
  Fix: add `com.apple.security.app-sandbox = true` to the entitlements file referenced by `CODE_SIGN_ENTITLEMENTS`. If the app networks, also add `com.apple.security.network.client = true` or all networking silently fails at runtime. App Sandbox does **not** break the app's own-item keychain access on a real-team Release build, so do not add `keychain-access-groups` to compensate (that can orphan items).
  Prevent: `/swift-preflight` Check 4.

- **ITMS-90683 — missing purpose string.** A privacy-sensitive API is linked but the matching `NS*UsageDescription` is missing or empty.
  Fix: add the specific key with a real, user-facing reason (`NSCameraUsageDescription`, `NSMicrophoneUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSContactsUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSUserTrackingUsageDescription`, etc.). Grep the sources to find which API triggered it.
  Prevent: `/swift-preflight` Check 4.

- **Export-compliance prompt on every upload.** Not a rejection, but a manual prompt each time.
  Fix: set `ITSAppUsesNonExemptEncryption` in Info.plist (`false` when the app only uses HTTPS/standard system crypto) to skip it.

### Headless-CI test failures (green locally, red on Xcode Cloud)

- **`errSecAuthFailed` (-25293) during a keychain write in tests.** The headless runner has no unlocked GUI login keychain, so writes fail; reads/deletes of absent items short-circuit to `errSecItemNotFound` (-25300) and pass, so only write-path tests break and it looks intermittent.
  Fix (test-side, never a production or entitlement change):
  1. Inject a protocol seam + in-memory fake (e.g. `SessionTokenStoring` + `InMemorySessionTokenStore`, a plain `final class`, **not** `@MainActor`) so service tests never touch the real keychain.
  2. For tests that must hit the real store, probe once in `setUp` with a real write inside a **catch-all** `do/catch` (`catch { unavailable = true }` — catch ANY error, reference no `errSec` constants, so no `import Security`), then `try XCTSkipIf(unavailable, …)` on every write case.
  Generalize: isolate keychain/GUI/signing/network/disk behind a seam before enabling CI test execution.
  Prevent: `/swift-preflight` Check 5.

- **`errSecMissingEntitlement` (-34018) on macOS keychain.** `kSecUseDataProtectionKeychain: true` on an unsigned/ad-hoc build that lacks the access-group entitlement.
  Fix: do not hard-disable data-protection keychain. Try DPK first; on macOS catch `errSecMissingEntitlement` and fall back to the legacy keychain transparently (write retries with DPK off; read retries legacy; delete swallows it). A real-team signed build then auto-engages DPK with no code change.

### Build-time signing / entitlement failures

- **"… has entitlements that require signing with a development certificate."** An ad-hoc build (`CODE_SIGN_IDENTITY="-"`, no `DEVELOPMENT_TEAM`) carries a **capability** entitlement (`keychain-access-groups`, app-groups `com.apple.security.application-groups`, push `aps-environment`, any `com.apple.developer.*`).
  Fix: remove the capability entitlement until a real `DEVELOPMENT_TEAM` is configured, or set the team. Sandbox entitlements (`app-sandbox`, `network.client`) are fine ad-hoc. Code that would use the deferred entitlement should detect `errSecMissingEntitlement` and fall back.
  Prevent: `/swift-preflight` Check 6.

- **Duplicate build number on TestFlight upload.** `CURRENT_PROJECT_VERSION` is static and collides with a prior upload.
  Fix: stamp `$CI_BUILD_NUMBER` into `project.yml` in `ci_post_clone.sh` before generate, guarded by `[ -n "$CI_BUILD_NUMBER" ]`. Do not also enable ASC auto-increment.
  Prevent: `/swift-preflight` Check 2. Scaffold: `/swift-ci-scaffold`.

### Xcode Cloud project / scheme problems

- **CI builds a stale or missing pbxproj / "scheme not found."** XcodeGen/Tuist project with no `ci_scripts/ci_post_clone.sh` regenerating it, or the target scheme is not shared (`xcshareddata`), or the scheme-defining commit was not pushed.
  Fix: add a `ci_post_clone.sh` that `cd "$CI_PRIMARY_REPOSITORY_PATH"`, installs the generator, and regenerates; ensure the scheme is declared in `project.yml` `schemes:` (generates as shared) and the commit is pushed. Xcode Cloud workflows live in App Store Connect, so pointing a Test action at the scheme is a UI step you must do there.
  Prevent: `/swift-preflight` Checks 3, 7. Scaffold: `/swift-ci-scaffold`.

- **Flaky UITest blocks a release.** The Test action runs a scheme whose test set includes UITests.
  Fix: add a unit-test-only CI scheme, point both (iOS + macOS) Test actions at it ("Required to Pass") in App Store Connect, keep Archive on the full scheme.

### Local "phantom" errors

- **SourceKit "cannot find type X" / "no such module" on a brand-new `.swift` file.** The file is not yet in the generated `.xcodeproj`.
  Fix: run `xcodegen generate`; trust `xcodebuild` / `swiftlint --strict` over live editor diagnostics. Not a real error.

- **`swift-frontend` crash / `report_fatal_error` in IRGen with `Binding(get:set:)`.** Swift 6.3.1 aborts on `Binding(get: instanceMethod, set: instanceMethod)` referencing `@MainActor` methods; lint passes, only `xcodebuild` shows it.
  Fix: use closure literals — `Binding(get: { … }, set: { newValue in … })`. The IRGen culprit is the first `-primary-file` after the crash banner.

## Output

For each symptom found:

```
Symptom:   ITMS-90296 (App Sandbox not enabled)
Root cause: <repo>/App/App.entitlements has no com.apple.security.app-sandbox key
Fix:        add `com.apple.security.app-sandbox = true` (and `network.client = true` — the app uses URLSession)
            On XcodeGen this is the entitlements file wired via CODE_SIGN_ENTITLEMENTS, not info.properties.
Why:        Mac App Store builds must be sandboxed; rejected during processing, not at build.
Prevent:    /swift-preflight Check 4 catches this before upload.
```

End with a one-line "run `/swift-preflight` before your next upload to catch these as a set."
