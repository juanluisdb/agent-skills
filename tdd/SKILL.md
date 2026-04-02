---
name: tdd
description: Test-driven development with a red-green-refactor loop. Use when the user wants test-first implementation, mentions TDD or red-green-refactor, or wants a bug fixed by first capturing behavior in a test.
---

# Test-Driven Development

Use this skill when the work should proceed through small, test-first vertical slices.

## Core Loop

1. RED: Write one test for the next behavior and run it. It must fail for the expected reason.
2. GREEN: Write the minimum code to make that test pass.
3. REFACTOR: Improve the code only while the suite is green.
4. Repeat for the next behavior.

## Working Rules

- Use vertical slices. Do not write a full batch of tests before implementation.
- Each test should describe behavior, not implementation details.
- Prefer public interfaces over reaching into internals.
- Keep each cycle small enough that the next move is obvious.
- When fixing a bug, start by capturing the failing behavior in a test if the codebase makes that practical.

## In Existing Codebases

- If the code is hard to test, begin with a characterization test around current behavior, then create safer seams from there.
- If there is no clean seam yet, make the smallest refactor that improves testability while staying green.
- If the full suite is slow, use the smallest trustworthy test subset during the loop, then run the broader relevant suite before finishing.
- If the suite is flaky, do not treat random red as meaningful signal. Isolate a stable repro or note that the suite itself needs attention.
- If a failing test is caused by bad setup rather than the intended behavior, fix the test so RED means something real.

## Per-Cycle Check

- The test fails for the reason you expect.
- The implementation is the smallest change that could pass the test.
- All relevant tests pass after the change.
- Any refactor keeps behavior covered.

## Avoid

- Writing tests in bulk from an imagined end state.
- Adding large abstractions before a test demands them.
- Declaring victory on a focused test run without running the broader relevant checks.
- Using TDD as a ritual when the task is still too ambiguous to express as behavior.
