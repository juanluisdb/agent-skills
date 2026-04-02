# GitHub Feedback

Load this reference when the review surface is a GitHub pull request and you need to inspect existing review comments efficiently.

## When To Use

- the user gives a GitHub PR URL
- the current branch is associated with a GitHub PR
- review comments or unresolved threads need to be collected from GitHub rather than pasted manually

## Preferred Approach

Use `scripts/fetch_github_comments.py` when `gh` is available.

The script can:

- resolve the PR from the current branch
- accept an explicit PR URL
- accept an explicit PR number when owner and repo are known
- fetch top-level comments, review submissions, and inline review threads
- include resolved and outdated state so stale comments can be identified

## Environment Notes

- `gh auth status` must succeed before the script can fetch anything useful.
- In sandboxed environments, `gh` may fail even when it works on the host machine.
- If GitHub access is important and the failure looks environmental, consider rerunning outside the sandbox with approval rather than assuming there are no comments.

## What To Do With The Output

- prioritize unresolved and actionable threads first
- separate stale or already-addressed comments from still-relevant concerns
- validate each concern against the current code, not just the original comment text
- consolidate multiple comments that point at the same root issue
