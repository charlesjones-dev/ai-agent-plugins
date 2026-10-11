---
name: swift-concurrency-review
description: "Review Swift 6 strict-concurrency and SwiftUI code for idiom and build-breaking issues - non-Sendable across actor boundaries, @MainActor witness vs nonisolated protocol requirements, Combine/ObservableObject usage, force-unwraps, #Predicate macro limits, the 6.3.x Binding IRGen crash, missing #if os() guards, and unsafe escape hatches. Reports file:line with the fix and the why."
argument-hint: "[path or files; default = changed files vs git]"
allowed-tools: [Bash, Read, Glob, Grep]
disable-model-invocation: true
---

# Swift 6 + SwiftUI Concurrency Review

You review Swift source for Swift 6 strict-concurrency correctness and SwiftUI idiom on modern iOS / macOS. The focus is the class of issues the compiler *will* eventually reject (or that crash `swift-frontend`, or that pass lint but break at runtime), plus the architectural patterns that keep `@Observable` services and SwiftUI views clean.

Scope discipline: this is **not** a general bug hunt or a style cleanup. Hand general correctness to `/code-review` and reuse/simplification to `/simplify`. Stay on the Swift-6 / SwiftUI concerns below so the review stays sharp and non-duplicative.

## What to review

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

Default to the **changed** Swift files (`git diff --name-only` + staged + untracked `*.swift`). If the arguments name a path or files, review those. If the project has a knowledge base with Swift conventions (for example `swift-6-patterns.md` under `.claude/rules/kb/`, `.claude/kb/` or `docs/kb/`), read it first - the project may have its own codified rules that supersede the generic ones here.

## Review dimensions

For each, report `file:line`, the issue, the concrete fix, and a one-line why. Cite the compiler diagnostic text where it helps the user recognize it.

### 1. Sendability across isolation boundaries

- A type sent across an actor boundary (an endpoint `body`, a value captured into a detached `Task`, anything an `actor` method returns) must be `Sendable`. Endpoint bodies that cross the boundary need `(any Encodable & Sendable)?`, not bare `any Encodable`.
- Domain models that drop `Sendable` (e.g. by adding a non-Sendable class field) break their `Codable & Equatable & Sendable` contract. Flag a new stored property that is a non-Sendable reference type.
- `CFString` and most CoreFoundation types are **not** `Sendable`. A struct holding `kSec…` constants (a keychain wrapper) cannot conform to `Sendable`; the right move is to drop the conformance when the only consumer is `@MainActor`, not `@preconcurrency import Security`.

### 2. Actor isolation mismatches

- **`@MainActor` witness vs nonisolated protocol requirement.** A `@MainActor` type (including any `static func`/`static let` on a `SwiftUI.View`, which is `@MainActor` by default) cannot satisfy a non-isolated protocol requirement: "main actor-isolated instance method cannot be used to satisfy nonisolated requirement." Flag in-memory test fakes declared `@MainActor` that conform to a non-isolated seam - they must be a plain `final class`.
- **Static helper on a `View` type read from a nonisolated context** (e.g. a plain `XCTestCase`) warns under Swift 6. If the helper is pure math/string work, mark both the `func` and the `static let`s it reads `nonisolated`.
- **`nonisolated init()` for default-param evaluation.** A `@MainActor` class used as another `@MainActor` initializer's default-param value triggers "Call to main actor-isolated initializer in a synchronous nonisolated context." Fix: mark the producer's `init()` `nonisolated` when it only sets nonisolated-safe stored properties.
- **`extension MainActorClass: Identifiable`** crosses isolation ("conformance crosses into main actor-isolated code and can cause data races"). Use a plain `Sendable` struct as the `sheet(item:)` payload instead.

### 3. Banned legacy patterns (project rules on modern stacks)

- `import Combine`, `ObservableObject`, `@Published` - replace with `@Observable` + `@State`/`@Environment`. Flag any reintroduction.
- `DispatchQueue.main.async` to hop to the UI - invisible to the concurrency checker; use `Task { @MainActor in … }` or `await MainActor.run`.
- `@unchecked Sendable`, `nonisolated(unsafe)`, `MainActor.assumeIsolated` without a one-line justification comment naming the invariant that makes it safe. These are escape hatches, not defaults.

### 4. Force-unwraps and unsafe boundaries

- `URL(string: "…")!` and other force-unwraps (SwiftLint `force_unwrapping`). Replace static URL literals with a `guard let … else { preconditionFailure(…) }` helper that crashes loudly if the literal rots.
- `try!` on `ModelContainer(...)` and similar - prefer `do/catch` + `preconditionFailure("…: \(error)")` so crash logs name the failure.
- Boundary input (`[String: Any]`, raw JSON) leaking past the networking layer instead of being decoded into typed models immediately.

### 5. SwiftData `#Predicate` macro limits

- `#Predicate` rejects `Optional<Date>` nil-coalescing combined with other clauses ("cannot convert … to closure result type 'any StandardPredicateExpression<Bool>'"). Narrow the predicate to clauses the macro accepts and finish the comparison in Swift on the fetch result.
- `#Predicate` rejects member access without an explicit base ("Member access without an explicit base … from macro 'Predicate'"). Write `Date.distantFuture`, not `.distantFuture`.
- Upserts that insert `Cached.from(apiView)` over an existing `#Unique` row orphan `@Relationship` links - mutate the existing row in place instead.
- A "never touch unread/starred" protection rule must be encoded **in** the predicate, not implied by the primary AND-chain, or protected rows get deleted when the implication does not hold.

### 6. Toolchain crash hazards

- **`Binding(get: instanceMethod, set: instanceMethod)` referencing `@MainActor` methods** crashes `swift-frontend` on Swift 6.3.x (`report_fatal_error` in `SyncCallEmission::setArgs`). Lint passes; only `xcodebuild` shows it. Fix: closure literals `Binding(get: { … }, set: { newValue in … })`.

### 7. Cross-platform SwiftUI guards

- iOS-only view modifiers on a file that also compiles for macOS must be wrapped in `#if os(iOS)` at the smallest scope: `.keyboardType`, `.textInputAutocapitalization`, `.navigationBarTitleDisplayMode`, `.tabViewBottomAccessory`. (`.textContentType`, `.autocorrectionDisabled`, `.scrollDismissesKeyboard` are cross-platform - do not over-guard.)
- `.windowResizability(.contentMinSize)` does nothing without a paired `.frame(minWidth:minHeight:)`, both under `#if os(macOS)`.
- `import UIKit` on a cross-platform file belongs inside `#if os(iOS)`.

### 8. SwiftUI architecture

- Views importing from sibling views; views doing I/O or orchestrating other views (views should be leaves consuming injected state and emitting intents).
- Hardcoded colors/hex in views instead of theme tokens via `@Environment`.
- `@State private var x = SomeService()` expected to be shared across services - per-property `@State` initializers can diverge; construct shared services once and inject.

## Output

```
Swift 6 / SwiftUI Review — 4 files

App/Services/AuthService.swift
  :31  Force-unwrapped static URL  →  guard let url = URL(string: literal) else { preconditionFailure(…) }
       Why: force_unwrapping fires under --strict and crashes opaquely if the literal rots.
  :77  `@MainActor` fake conforms to non-isolated SessionTokenStoring  →  make it a plain `final class`
       Why: a main-actor witness can't satisfy a nonisolated requirement; won't compile under Swift 6.

App/Views/ReaderView.swift
  :120 `.keyboardType(.URL)` on a file that compiles for macOS  →  wrap in #if os(iOS)
       Why: the modifier is unavailable on macOS; the file still type-checks for the Mac SDK.

Clean: App/Models/Article.swift, App/App.swift
Summary: 3 findings across 2 files. Run /swift-verify to confirm against the compiler.
```

This is a report-only review. Do not edit files. Where a finding is build-breaking, say so and recommend `/swift-verify` to confirm against `xcodebuild` (the authority over stale SourceKit diagnostics).
