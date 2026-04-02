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

- If there are already files with conflict markers (`U` status or `<<<<<<<` in files), proceed to Step 2.
- If no merge is in progress, ask the user which branch to merge, then run `git merge <branch>`. Never rebase.

If the merge completes without conflicts, report success and stop.

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

- Generated: lock files, compiled output, auto-generated code
- Binary: images, compiled assets
- Source: everything else

For generated files, prefer regeneration over manual resolution.

For binary files, flag them for a user decision immediately.

## Step 3: Plan

For each conflicted source file, gather context:

1. Read the conflict regions in the file.
2. Read both versions with `git show :2:<file>` and `git show :3:<file>`.
3. Read recent git history on that file from both sides to understand intent:

```bash
git log --oneline -5 HEAD -- <file>
git log --oneline -5 MERGE_HEAD -- <file>
```

For each conflict region, decide whether it is auto-resolvable or needs human input.

### Auto-resolvable

- Both sides add to different, non-overlapping parts of the file
- Import or dependency additions where both are needed
- One side only changes formatting or whitespace
- Tests where both sides add different cases
- The surrounding code and git history make the correct merged state obvious

### Needs Human Input

- Both sides modify the same logic in incompatible ways
- Delete/modify conflicts
- Config, CI, or migration files with competing values
- The intent behind one or both changes is still unclear after reading the code and git history
- Merging both sides could introduce a semantic bug

Present a short plan to the user before editing files:

```text
File                        | Conflicts | Strategy
----------------------------|-----------|------------------
src/auth.py                 | 2         | Auto-resolve
src/config.yaml             | 1         | Ask user
package-lock.json           | 1         | Regenerate
```

Wait for approval before proceeding.

## Step 4: Resolve

Work through files in this order: auto-resolvable first, then ambiguous files one by one.

### Auto-resolvable files

- Edit to the correct merged state
- Remove all conflict markers
- Stage with `git add <file>`

### Generated files

- Delete the conflicted file
- Run the appropriate regeneration command
- Stage the regenerated result

### Files that need human input

For each one:

1. Show both sides clearly
2. Explain the intent behind each side
3. Propose a resolution
4. Ask the user to confirm or redirect
5. Apply the chosen resolution and stage it

Resolve these one at a time rather than batching all ambiguity together.

## Step 5: Verify

After all files are resolved:

```bash
git grep -l '<<<<<<< ' | cat
git diff --check
git status
```

If markers or diff issues remain, fix them before proceeding.

## Step 6: Test

Try to run the most relevant project tests to catch semantic conflicts.

- Look for test commands in repo tooling such as `Makefile`, `package.json`, `pyproject.toml`, `Cargo.toml`, or CI config.
- If tests fail, investigate whether the failure is merge-related and attempt to fix it.
- If no clear test command exists, say so plainly.

## Step 7: Commit

Complete the merge with:

```bash
git commit --no-edit
```

Use git's generated merge commit message unless the user asks otherwise.

## Important Rules

- Never rebase when handling this workflow.
- Never blindly pick one side without understanding intent.
- Never leave conflict markers behind.
- Ask the user when the conflict is genuinely ambiguous.
- Do not dump all ambiguous conflicts on the user at once.
