---
name: clean-comments
description: Must load before any commit, push, or MR; no change ships without it. Strips AI-slop comments the change introduced and keeps only those carrying a non-obvious why. One pass per checkpoint over the whole diff, never after each edit.
---

# Comments that earn their place

A comment costs the reader attention and costs the next author maintenance. It earns that cost only by carrying what the code cannot: a non-obvious **why** — a hidden constraint, an invariant, surprising external behaviour, the reason a workaround exists. Anything a reader would learn faster from the line below is not worth its cost. Default to no comment.

## The tell

AI-written comments fail in a recognisable way: they describe the *session*, not the code. The model captions each line as it writes it, narrates what it changed, and reassures the reviewer. None of that survives the merge — the reviewer sees the final state, and the next reader has no idea a session ever happened.

Remove:

- **Captions** — restating the line below. `# increment the counter`, `# loop over the results`, `# return the response`.
- **Change history** — `# now uses X instead of Y`, `# moved out of the old handler`, `# renamed from foo`. This belongs in the commit or the MR.
- **Reviewer talk** — `# as requested`, `# NEW`, `# this fixes the bug`. Addressed to someone who will never read it in that context.
- **Neighbour narration** — `# the helper below parses the payload`. The helper's name should do that.
- **Banners** — `# ---- Helpers ----`, `# === Setup ===`. Structure is the file's job.
- **Restating docstrings** — a docstring that re-says the signature, the parameter names, and the return type the annotations already declare. Keep the line that says what the function is *for*; drop the rest.
- **Empty hedges** — `# should be safe`, `# just in case`, `# defensive check`. If there is a real risk, name it. Otherwise it reads as a shrug.
- **Commented-out code** — dead by definition, and git remembers it.

## What stays

- The non-obvious why: a constraint, an invariant, a surprising API behaviour, a race being avoided.
- Workarounds, with the upstream issue or ticket that will let someone delete them later.
- `noqa`, `type: ignore`, `eslint-disable` and friends — a suppression is meaningless without its reason.
- `TODO` / `FIXME` tied to a ticket.
- Licence headers, generated-file markers, anything a tool reads.
- Public API documentation, where the audience is a caller who never opens the file.

When you genuinely can't tell whether a comment carries a why, keep it. Deleting the one line that explained a constraint costs far more than leaving a mediocre comment in place.

## Slop on top of subtle code

A caption above genuinely tricky code is a signal, not just litter — something there felt like it needed explaining. Deleting the caption loses that signal. Two better moves: write the actual why in its place, or rename the variable or function so nothing needs explaining. Prefer the rename.

## When: at the checkpoint

A **checkpoint** is the last moment before a change leaves your hands: a commit, a push, opening or updating an MR, or handing finished code back when no commit is coming. Every checkpoint gets a pass; a change that reaches one uncleaned is not ready to ship.

Mid-edit is the wrong moment. Files are still in flux, and a pass after each write re-reads lines you are about to touch again.

**One checkpoint, one pass.** A `commit → push → MR` run in a single stretch is one checkpoint, not three: clean once before the commit, then carry straight through. If nothing has been edited since your last pass, the checkpoint is already clean — skip it silently.

## What: the diff you are handing off

Clean the comments **your change introduced**, across the whole diff crossing the checkpoint:

- before a commit — `git diff HEAD` (staged and unstaged together)
- before a push — `git diff @{push}`, or `git diff <target>..HEAD` when there is no upstream yet
- before an MR — the branch diff, `git diff <target>...HEAD`

That is the set you are accountable for, and it keeps the diff about the change.

Preexisting comments elsewhere are not this skill's job. Sweeping a file's comments buries the change under noise a reviewer has to read past. If you notice slop right next to what you touched, say so in one line and leave it; the user decides whether it deserves its own MR.

## Voice for the ones that stay

One line. Present tense, about the code as it stands, never about the edit that produced it. No first person. If it needs a paragraph, the code is the problem — fix the code.

Then report in one line what came out. The diff shows the removals; a reviewer who disagrees with one can say so.
