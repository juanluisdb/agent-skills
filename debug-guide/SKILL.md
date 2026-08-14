---
name: debug-guide
description: Thinking guide for debugging and investigation. Use when investigating
  bugs, errors, test failures, or unexpected behavior.
---

# Debug Guide

Not a process or a checklist to fill. These are thinking prompts — consider whichever
are relevant, skip what doesn't apply, and bring your own judgment beyond what's listed
here.

## Investigate before concluding

- **Understand fully before proposing.** Don't stop at the surface. What is the error
  actually saying? What are the conditions that produce it? Don't propose a fix until
  you can explain the cause.
- **Complete the dataset.** If there are N instances of the problem, investigate all of
  them — or at least a representative of each distinct variant — before forming patterns.
  Conclusions from a subset are guesses. The instance you skipped might be the one that
  disproves your theory.
- **Explore deeply.** Cast a wide net before narrowing down. Consider using subagents
  to investigate multiple areas of the codebase in parallel.

## Separate what you see from what you think it means

- **Observation vs inference.** State what the evidence proves. Then separately state
  what you infer. Mark the boundary. "The generator was closed" is an observation.
  "The client disconnected" is an inference — it requires proof of its own.
- **Trace the full causal chain, and verify each link.** If your explanation is
  "A causes B causes C," verify A→B and B→C independently. An unverified link is a
  guess dressed as a conclusion.

## Generate and eliminate hypotheses

- **Enumerate competing explanations before settling on one.** What else could produce
  the same evidence? If you can only think of one explanation, you haven't thought hard
  enough.
- **Form hypotheses, then verify them.** Don't guess — build a theory of what's wrong
  and look for evidence that confirms or disproves it. When the search space is wide,
  explore multiple hypotheses in parallel. Discard what doesn't hold, double down on
  what does.
- **Actively try to disprove your leading theory.** What evidence would contradict it?
  Go look for that evidence. A theory that survives disconfirmation is stronger than
  one that was never challenged.

## Find the root cause

- **Find the root cause, not the symptom.** The error location is often not the origin.
  Trace upstream until you find where things actually went wrong.
- **Look beyond the code.** Infrastructure (load balancers, proxies, DNS, timeouts),
  deployment state, network path, and configuration all participate in the causal chain.
  If the code looks correct, the answer may not be in the code.
- **Question your assumptions.** If your hypotheses aren't panning out, your mental
  model is wrong. Step back, challenge what you think the code is doing.

## Prove it

- **Back it with evidence.** Show proof for your conclusion — whatever makes it
  verifiable. "I think X is the cause" isn't enough. "X is the cause because Y" is.
- **Name what you don't know.** Explicitly state what remains unproven, what evidence
  is missing, and what would be needed to close the gap. Unknown unknowns are dangerous;
  known unknowns are just next steps.
