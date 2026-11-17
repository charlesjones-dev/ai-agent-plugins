# Test rules

The checklist for `/slop-tests`. Project rules (CLAUDE.md, AGENTS.md, Cursor rules, the KB, CONTRIBUTING.md) override anything here. The examples are illustrative and mix stacks.

**The test:** would this test fail if the behavior it names broke, and pass after any change that keeps that behavior? A test that fails for other reasons is a change detector. A test that can't fail is noise. Either one goes, unless a keep rule applies.

**The exception:** never delete the only test of real behavior. Fix it or rewrite it instead.

**What counts as one test:** one `it` or `test`, one `def test_*`, one `func TestX` or `t.Run` case, one XCTest method, or one `@Test`. Rows of a `test.each`, `parametrize` or Go table count as one test unless their cases check different behavior.

## Confidence

| Level | Meaning | `--fix` acts on it |
|---|---|---|
| High | A mechanical signal that reading the test and the code confirms, such as no assertion, a tautology or a `.only`. Or a medium finding that `--verify` confirmed | Yes |
| Medium | A pattern plus supporting evidence, such as git history, a mock that echoes its stub, or a co-change count | No |
| Low | A judgment call, such as a test that may mirror the implementation | No |

## A. Change detectors: tests that change whenever the code does

| Signal | What it looks like |
|---|---|
| Large structural snapshots | Jest/Vitest `toMatchSnapshot()` or `toMatchInlineSnapshot()` of a whole render tree or a large object; `-u` in a package script; pytest syrupy or snapshottest of large dicts; Swift `assertSnapshot(of: view, as: .dump)`; Go golden files that an `-update` flag rewrites in most commits; Playwright `toMatchAriaSnapshot` of a whole page (low) |
| Interaction-only assertions | The only assertions are `toHaveBeenCalledWith`, `toHaveBeenCalledTimes` or call order; Python `assert_called_once_with` or `call_args_list == [...]`; a Swift spy array compared with `XCTAssertEqual(spy.calls, [...])`; gomock `EXPECT()` inside `gomock.InOrder` |
| Private internals | TS `(obj as any)._state`, `obj['_cache']`, `vi.spyOn(obj, 'privateHelper')`, rewire; Python `obj._attr`, `patch('module._helper')`, imports of `_private` names; Swift members widened from `private` only so `@testable import` can reach them; Go tests that read unexported struct fields |
| Brittle selectors | Playwright or Testing Library locators on generated class names, `nth-child`, deep CSS paths or test IDs added only for one assertion, when a role, label or text locator exists |
| Mocks everything | Every collaborator of the subject is mocked, including pure functions and value types; `vi.mock` or `jest.mock` of the subject's sibling modules; four or more stacked `@patch` decorators; an interface created only so a test can mock it; more lines of mock setup than of assertions |
| Mirrors the code | The expected value is computed with the same expression the implementation uses, or the test's steps map one-to-one to the source lines |

**Starting confidence:** low, or medium when a signal in the table matches, such as a read of a private field or an interaction-only test. A change detector is never high from reading alone, because only breaking it under a refactor proves it.

**Git evidence:** the co-change count, per test. List the commits that changed the source file after the test was added. Count those that also changed this test's lines: `git log -L '/<test name>/,+<n>:<file>'`, or `git log -L :<function>:<file>` for Go and Python. If the count is 80% or more, and those changes only update expected values or snapshots rather than add cases, raise a low finding to medium. Co-change never makes an A finding high. Only `--verify` does.

**Mutation for `--verify`:** a refactor that keeps the behavior. Rename a private member, inline or extract a helper, reorder independent statements, change markup that has no role or text, or swap a mocked collaborator's call order where order doesn't matter. If the test fails, it's a change detector.

For "Mirrors the code", a refactor proves nothing, because the test copies the behavior too. Change the constant or expression the test copies or imports instead. If the test still passes while a behavior test of the same function fails, it can't catch that bug: raise the confidence to high.

**Keep:**

- approval, golden or contract tests the project documents, such as an API schema snapshot that clients depend on;
- visual regression tests: Playwright `toHaveScreenshot`, image snapshots;
- interaction tests where the call is the behavior: the email was sent, the card was charged, the event was published, the cache was invalidated;
- small inline snapshots of a value a person reads, such as an error message.

**Fix direction:** delete the test when another test covers the behavior. Otherwise rewrite it to call the public interface and assert the result a user or caller sees.

## B. Tests that check a removed feature is gone

| Signal | What it looks like |
|---|---|
| Absence with no cause | `expect(mod.oldFn).toBeUndefined()`; `expect(Object.keys(mod)).not.toContain('old')`; `queryByText('Old banner')` with `not.toBeInTheDocument()` and no action before it; `expect(res.status).toBe(404)` for a deleted route; `assert not hasattr(module, 'old_fn')`; `pytest.raises(ImportError)` around an old import; `assert 'old_flag' not in config`; `XCTAssertNil` on a removed key; Go reflection that checks a method doesn't exist |
| Source scanning | The test reads source files (`fs.readFileSync('src/…')`, `Path('src/…').read_text()`, `os.ReadFile`) and asserts a string isn't in them |
| Names | "no longer", "removed", "should not exist", "is gone", "was deleted", "does not render" |

**Git evidence:** run `git log -S'<symbol>' --oneline` for the name the test checks. If the commit that removed the symbol also added the test, or both landed in the same PR, and no keep rule below applies, the confidence is high. If a comment, issue link or doc ties the absence to clients, security or a contract, make it a question, never a high-confidence delete. If the feature was removed long before the test was added, look for an issue that says it came back.

**Mutation for `--verify`:** put the feature back in its simplest form, such as re-adding the export or the route. If the test still passes, it checks nothing. If it fails, it does check absence: judge it by the keep rules below.

**Keep:**

- a negative assertion with a cause in the test: a viewer role sees no delete button, a disabled flag hides the panel, an expired token gets a 401;
- an absence that is a security or privacy contract: a secret or personal field must stay out of a response, a debug route must stay off in production;
- a removed public endpoint or API that must return 404 or 410 to existing clients, when the project documents that contract in its docs, an API spec, a linked issue, or a comment at the test that names the clients. If you can't read the linked issue, ask;
- a regression test that links an issue where the removed thing came back.

**Fix direction:** delete.

## C. Tests that can never fail

| Signal | What it looks like |
|---|---|
| No assertion | Jest/Vitest body with no `expect` and no `expect.assertions(n)`; pytest or unittest with no `assert`, `self.assert*`, `pytest.raises` or `self.assertRaises`; Go with no `t.Error`, `t.Fatal`, `require` or `assert`; XCTest with no `XCTAssert*` or `XCTFail`; Swift Testing with no `#expect` or `#require`. A Playwright test with only actions is a smoke test, because actions auto-wait and can fail: medium at most |
| Tautology | `expect(true).toBe(true)`; `expect(x).toBe(x)`; `XCTAssertTrue(true)`; `expect(list.length).toBeGreaterThanOrEqual(0)`; `toBeDefined()` on an import or a literal; `typeof fn === 'function'`; `not.toThrow()` around code that can't throw; Python `assert (cond, "message")`, a tuple that is always true; a bare `expect(x)` with no matcher |
| Mock echo | A stub returns X and the test asserts the result is X, when the subject only passes the value through or the test calls the mock itself |
| Swallowed error | `try { … expect … } catch {}`; `.catch(() => {})` on the promise under test; `except Exception: pass`; Swift `try?` around the call under test; Go `if err != nil { return }` with no `t.Fatal` |
| Unreached or unawaited assertion | `expect` inside `.then` with no `return` or `await`; a `done` callback that's never called or not declared; assertions in a `setTimeout` or an event handler that never fires; assertions in a loop over a collection that is empty; `if (x) expect(…)`; Go assertions in a goroutine that outlives the test; an `XCTestExpectation` with no `wait(for:)` or `fulfillment(of:)`; assertions in an unawaited `Task {}`. Node's built-in runner shows such a test as passed and reports the late assertion as a failure of the file. That is still an unawaited assertion |
| Empty table | `test.each([])`, `@pytest.mark.parametrize("x", [])`, an empty Go test table |
| Skip | `.skip`, `xit`, `xdescribe`, `it.todo`, `test.fixme`, `@pytest.mark.skip` with no condition, unconditional `t.Skip()` or `XCTSkip`, Swift Testing `.disabled` |
| Focus | `.only`, `fit`, `fdescribe`, `test.only`. Focus doesn't make this test useless. In most runners it silently turns off every other test in the file or run. Node's built-in runner ignores it unless `--test-only` is set, so check the test script for that flag |

**Mutation for `--verify`:** break the behavior the test claims to cover. Negate the condition, return the zero value or an empty collection, throw, or delete the call the assertion depends on. If the test passes under every mutation, it can never fail.

**Keep:**

- a skip with a condition (platform, environment variable) or a linked issue;
- a smoke test that is the only check that a page or command runs at all, when the project has no better one. Mark it medium and say so.

**Fix direction:**

- no assertion, tautology, mock echo, empty table: delete, unless it's the only test near real behavior, then rewrite;
- Python `assert (cond, "message")`: fix so it can fail by removing the parentheses;
- swallowed error, unreached or unawaited assertion: fix so it can fail. Add the `await` or `return`, remove the catch, wait for the expectation, or assert that the collection isn't empty;
- focus: remove the focus marker. Offer `forbidOnly` or `allowOnly: false` in step 9;
- skip with no condition or issue: count it under Delete, mark it "waits on question N", and ask whether to delete it or file an issue.

## Duplicates

Two tests that call the same code with the same inputs and assert the same result: merge them into one, keeping the clearer name. Snapshot cases that differ only by a prop that doesn't change the output: merge them into one case.
