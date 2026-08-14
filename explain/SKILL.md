---
name: explain
description: Explain something again, more clearly, or in more depth — the last message, a decision, a concept, or how some code works. Use when the user says they don't follow, asks what something means, wants more detail, or is losing the thread.
---

# Explain

Something didn't land. The job is to make it land, not to say it again.

## What to explain

No argument means the last message. An argument names the target: a term, a step, a decision, a file, a concept. Answer what was asked; opening with a diagnostic question costs more than a wrong guess would.

Plain doesn't mean elementary. The person asking is an engineer who lost one thread, not a beginner who needs the field explained. Drop the jargon, keep the level.

## Change something

Repeating the same explanation in different words fails the same way it failed the first time. Pick what to change:

- **Register** — same content, plainer words. For "what?", "that didn't land", a sentence carrying three unexplained terms.
- **Depth** — more of it, not less. "I want to know more about X" is a request for detail, and simplifying is the wrong direction. Answering a depth request with a summary is the most common way to miss twice.
- **Medium** — for shape problems: several moving parts, an order of operations, who calls what, what changed. Prose is the worst medium for these and the default one.

If a second attempt also fails, the model was wrong rather than the wording. Switch medium instead of reaching for plainer words again.

## Ways to show it

Some claims can't be carried by prose, because checking them means holding two things at once: a comparison of two options, an ordering over time, a before and after, a state that branches, a quantity spread across cases. There the notation isn't a nicer presentation of the argument, it *is* the argument — prose only asks the reader to rebuild it.

- **Pseudocode** for logic or an algorithm.
- **Call tree** for control flow, annotated with what goes in and what comes back. A bare call tree shows the order and hides the thing that actually moves.
- **Component tree** for UI structure, with the state and module boundaries that matter and nothing else.
- **Shallow file tree**, one line of responsibility per entry, for "where does this live".
- **Sequence or state diagram** for interaction between parts over time.
- **Diff** when the surrounding shape already exists and the point is what changes.
- **A worked example with real values**, traced end to end. One concrete trip through the thing often beats every diagram.

The notation belongs to the claim, not to the explanation. Every claim with a shape gets its own, next to the short text it supports. Across a long explanation the density holds or rises, never falls — the opening is usually setup, and the claims that come last (the comparisons, the edge cases, the part you're least sure of) are the ones a reader can least rebuild from paragraphs. One diagram at the top and prose from there has shown the easy part.

Keep only the calls, files, states, and boundaries that answer the question — a complete picture is a second wall to read.

## Plain language

- Short sentences, everyday words, one idea per sentence.
- Lead with the answer, then the reason.
- Name a thing before describing it. Nobody can hold an attribute of something they haven't been introduced to.
- Cut hedges, cut restatements of the previous sentence, cut the "it's not just X, it's Y" shape.
- Keep every fact, name, number, and path. Simpler wording, not less content.

## Explaining code

Read it before explaining it. An explanation reconstructed from memory of what the code probably does is confidently wrong and unfalsifiable by the person asking, who came here precisely because they can't check it themselves. Quote the lines that carry the answer, with their paths.

## Landing

End on the thing itself, not a summary of what you just said. Say plainly what you're unsure landed, and let the next question come.
