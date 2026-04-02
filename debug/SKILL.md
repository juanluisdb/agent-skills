---
name: debug
description: Thinking guide for debugging and investigation. Use when investigating bugs, errors, flaky tests, regressions, or unexpected behavior. Not for broad architecture planning or feature design.
---

# Debug

Use this skill when the work is primarily about finding the cause of a problem, not just patching symptoms.

## Mindset

- Understand the failure before proposing a fix.
- Prefer evidence over intuition.
- Stay open to the possibility that the reported error is downstream from the real cause.
- Adjust the depth of investigation to the cost and risk of the problem.

## Investigation Prompts

- Reproduce the issue first when possible. If you cannot reproduce it, identify what is missing.
- Make the observed behavior concrete: what happened, what was expected, and under which conditions.
- Narrow the search space aggressively. Compare passing vs failing cases, recent changes, environments, inputs, and code paths.
- Form explicit hypotheses, then try to disprove them.
- Add instrumentation when it will shorten the search: logs, traces, assertions, temporary probes, smaller test cases.
- Reduce to a minimal repro when the problem surface is large or noisy.
- Trace upstream to the first bad state, not just the place where the system finally complains.
- Question hidden assumptions: data shape, timing, ordering, caching, config, state, permissions, environment, and stale artifacts.
- When a fix seems obvious, still verify the root cause. A plausible patch is not the same as an explained failure.

## Good Outcomes

- The cause is explained in a way another engineer could verify.
- The proposed fix addresses the cause, not only the symptom.
- The verification step is clear: repro now passes, regression test added, or evidence no longer appears.

## When Helpful

Summarize the investigation as repro, evidence, root cause, fix, and verification.

Do not force a rigid template if the user wants a lightweight or conversational debugging session.
