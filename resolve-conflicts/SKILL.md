---
name: resolve-conflicts
description: Resolve git merge conflicts intelligently. Use when the user asks to resolve merge conflicts, merge a branch, or when conflict markers are detected in files.
---

# Resolve Merge Conflicts

Resolve git merge conflicts by understanding intent from both branches, auto-resolving clear cases, and asking the user only when genuinely ambiguous.

## Step 1: Detect State

Determine if a merge is already in progress or needs to be started.

```bash
git status --porcelain | cat
```

- If there are already files with conflict markers (`U` status or `<<<<<<<` in files): proceed to Step 2.
- If no merge or rebase in progress: identify the branch to integrate (from the user or the conversation; ask if unclear), choose merge or rebase (below), and run it.

If the integration completes without conflicts, report success and stop.

### Merge vs rebase

Default to `git merge`. Rebase instead when it's genuinely better:

- the branch is unpushed or single-author, so history can be rewritten freely
- the repo wants linear history (fast-forward-only or semi-linear merge method, or a stated convention)
- the branch is mid-review with a stale base — a rebase keeps the review diff clean (this is what a reviewer's "rebase onto target" ask means)

Prefer merge for long-lived shared branches, and for long branches where a rebase would replay the same conflict once per commit.

During a rebase, `ours`/`theirs` **invert** (ours = the base being replayed onto, theirs = your commit) and conflicts arrive one commit at a time — resolve each against that commit's intent. Where the steps below say `MERGE_HEAD`, read `REBASE_HEAD` during a rebase.

**Hard rule:** rebasing published history ends in a force-push. Never force-push without explicit user confirmation.

## Step 2: Collect Conflicted Files

List all conflicted files:

```bash
git status --porcelain | grep -E '^(U.|.U|AA|DD)' | cat
```

Also scan for any files with conflict markers that git might not flag:

```bash
git grep -l '<<<<<<< ' | cat
```

Classify each file loosely:
- **Generated** — lock files, compiled output, auto-generated code
- **Binary** — images, compiled assets
- **Source** — everything else

For **generated files**: note them for regeneration rather than manual resolution.
For **binary files**: flag for user decision immediately (cannot be merged textually).

## Step 3: Plan

For each conflicted source file, gather context:

1. Read the conflict regions in the file (look for `<<<<<<<` / `=======` / `>>>>>>>` markers)
2. Read both versions: `git show :2:<file>` (ours) and `git show :3:<file>` (theirs)
3. Understand the *intent* behind each side, not just its text:
   ```bash
   git log --oneline -5 HEAD -- <file>
   git log --oneline -5 MERGE_HEAD -- <file>
   ```
   For the commits that actually touch the conflict region, read their full diffs (`git show <sha> -- <file>`). When a commit came from an MR/PR, pull that MR's description for the *why* (for GitLab, `glab mr list --search "<sha or title>"` or the commit page's associated MR) — descriptions often state the invariant the change protects.
4. For each conflict, name what a wrong resolution would erase — *"taking ours drops the tenant filter added in !4980"* — and, where one exists, the test that pins that behavior. A resolution merges intents, not lines.

For each conflict region, decide if it is **auto-resolvable** or **needs human input**:

### Auto-resolvable (resolve without asking)
- Both sides add to different, non-overlapping parts of the file
- Import/dependency additions where both are needed (merge unique, deduplicate)
- One side only has whitespace or formatting changes
- Test files where both sides add different test cases
- The intent from git log makes the correct resolution obvious

### Needs human input (must ask the user)
- Both sides modify the same logic in incompatible ways
- Delete/modify conflicts — one side deleted code the other modified
- Config, CI, or migration files with competing values
- The intent behind one or both changes is unclear even after reading git log
- Semantic conflicts where merging both could introduce bugs

Build a summary table:

```
File                        | Conflicts | Strategy
----------------------------|-----------|------------------
src/auth.py                 | 2         | Auto-resolve (additive)
src/config.yaml             | 1         | Ask user (competing values)
package-lock.json           | 1         | Regenerate
```

Scale the gate to blast radius: if every conflict is auto-resolvable or regenerate-only, proceed and show the table with the result. If any file needs human input, present the table first and wait for approval before changing anything.

## Step 4: Resolve

Work through files in this order: auto-resolvable first, then human-input files one by one.

### Auto-resolvable files
- Edit the file to the correct merged state
- Remove ALL conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Stage with `git add <file>`

### Generated files
- Delete the conflicted file
- Run the appropriate regeneration command (e.g., `npm install`, `poetry lock`, etc.)
- Stage the regenerated file

### Human-input files (one at a time)
For each file that needs human input:
1. Show the conflicting code from both sides clearly
2. Explain what each side intended (based on git log)
3. Propose a resolution with reasoning
4. Ask the user to confirm or provide alternative direction
5. Apply the chosen resolution, remove markers, stage the file

Move to the next file only after the current one is resolved.

## Step 5: Verify

After all files are resolved, verify the merge is clean:

```bash
# No remaining conflict markers anywhere
git grep -l '<<<<<<< ' | cat

# Git agrees everything is resolved
git diff --check

# Check status
git status
```

If any conflict markers remain or `git diff --check` reports issues, go back and fix them.

Textual cleanliness isn't semantic cleanliness. Git only flags overlapping edits — also check for **semantic conflicts in files that never conflicted**: the other side renamed a function, changed a signature, or tightened an invariant that this side's changes still use in the old shape. Scan what the other branch changed (`git log MERGE_HEAD ^HEAD --stat`) for symbols this side touches, and grep for callers of anything renamed or re-signatured. Tests catch these only if a test happens to cover the collision; this sweep catches them directly.

## Step 6: Test

Attempt to run the project's test suite to catch semantic conflicts (code merges cleanly but breaks behavior):

- Look for test commands in `Makefile`, `package.json` (scripts.test), `pyproject.toml`, `Cargo.toml`, or CI config
- Run the test command and report results
- If tests fail, investigate whether the failure is merge-related and attempt to fix
- If the failure is unrelated to the merge, inform the user and proceed

If no test command can be determined, inform the user and suggest they verify manually.

## Step 7: Commit

Complete the integration:

```bash
git commit --no-edit       # merge — uses git's auto-generated merge message
git rebase --continue      # rebase — then repeat from Step 2 for the next commit's conflicts
```

Report the final status to the user. If the branch was rebased and needs a force-push, ask first (see the hard rule in Merge vs rebase).

## Important Rules

- **Never force-push without explicit user confirmation** — rewriting published history is the destructive edge of a rebase.
- **Never force-resolve by blindly picking one side.** A resolution merges intents, not lines.
- **Ask the user when genuinely uncertain** — but not for things the code, the git log, or the originating MR can settle.
- **One human-input file at a time.** Don't dump all ambiguous conflicts on the user at once.
