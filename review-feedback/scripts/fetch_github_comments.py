#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any

QUERY = """
query(
  $owner: String!,
  $repo: String!,
  $number: Int!,
  $commentsCursor: String,
  $reviewsCursor: String,
  $threadsCursor: String
) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      url
      title
      state
      comments(first: 100, after: $commentsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          body
          createdAt
          updatedAt
          url
          author { login }
        }
      }
      reviews(first: 100, after: $reviewsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          state
          body
          submittedAt
          url
          author { login }
        }
      }
      reviewThreads(first: 100, after: $threadsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          originalLine
          originalStartLine
          diffSide
          startDiffSide
          resolvedBy { login }
          comments(first: 100) {
            nodes {
              id
              body
              createdAt
              updatedAt
              url
              author { login }
            }
          }
        }
      }
    }
  }
}
"""


def run(cmd: list[str], stdin: str | None = None) -> str:
    proc = subprocess.run(cmd, input=stdin, text=True, capture_output=True)
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{stderr}")
    return proc.stdout


def run_json(cmd: list[str], stdin: str | None = None) -> dict[str, Any]:
    output = run(cmd, stdin=stdin)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON output: {exc}") from exc


def ensure_gh_auth() -> None:
    try:
        run(["gh", "auth", "status"])
    except RuntimeError as exc:
        raise RuntimeError(
            "GitHub CLI is not ready. Run `gh auth login`, or rerun outside the sandbox if the host has working GitHub auth."
        ) from exc


def parse_pr_url(url: str) -> tuple[str, str, int]:
    match = re.match(r"^https://github\\.com/([^/]+)/([^/]+)/pull/(\\d+)(?:/.*)?$", url)
    if not match:
        raise ValueError(f"Unsupported GitHub PR URL: {url}")
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def get_current_branch_pr() -> tuple[str, str, int]:
    pr = run_json(["gh", "pr", "view", "--json", "number,headRepositoryOwner,headRepository"])
    owner = pr["headRepositoryOwner"]["login"]
    repo = pr["headRepository"]["name"]
    number = int(pr["number"])
    return owner, repo, number


def get_repo_from_context() -> tuple[str, str]:
    repo = run_json(["gh", "repo", "view", "--json", "owner,name"])
    owner = repo["owner"]["login"]
    name = repo["name"]
    return owner, name


def fetch_page(
    owner: str,
    repo: str,
    number: int,
    comments_cursor: str | None,
    reviews_cursor: str | None,
    threads_cursor: str | None,
) -> dict[str, Any]:
    cmd = [
        "gh",
        "api",
        "graphql",
        "-F",
        "query=@-",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"number={number}",
    ]
    if comments_cursor:
        cmd += ["-F", f"commentsCursor={comments_cursor}"]
    if reviews_cursor:
        cmd += ["-F", f"reviewsCursor={reviews_cursor}"]
    if threads_cursor:
        cmd += ["-F", f"threadsCursor={threads_cursor}"]
    payload = run_json(cmd, stdin=QUERY)
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], indent=2))
    return payload


def fetch_all(owner: str, repo: str, number: int, include_resolved: bool) -> dict[str, Any]:
    comments: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    threads: list[dict[str, Any]] = []
    comments_cursor: str | None = None
    reviews_cursor: str | None = None
    threads_cursor: str | None = None
    pr_meta: dict[str, Any] | None = None

    while True:
        payload = fetch_page(owner, repo, number, comments_cursor, reviews_cursor, threads_cursor)
        pr = payload["data"]["repository"]["pullRequest"]
        if pr_meta is None:
            pr_meta = {
                "number": pr["number"],
                "url": pr["url"],
                "title": pr["title"],
                "state": pr["state"],
                "owner": owner,
                "repo": repo,
            }

        page_comments = pr["comments"]
        page_reviews = pr["reviews"]
        page_threads = pr["reviewThreads"]

        comments.extend(page_comments.get("nodes") or [])
        reviews.extend(page_reviews.get("nodes") or [])

        for thread in page_threads.get("nodes") or []:
            if include_resolved or not thread.get("isResolved"):
                threads.append(thread)

        comments_cursor = page_comments["pageInfo"]["endCursor"] if page_comments["pageInfo"]["hasNextPage"] else None
        reviews_cursor = page_reviews["pageInfo"]["endCursor"] if page_reviews["pageInfo"]["hasNextPage"] else None
        threads_cursor = page_threads["pageInfo"]["endCursor"] if page_threads["pageInfo"]["hasNextPage"] else None

        if not (comments_cursor or reviews_cursor or threads_cursor):
            break

    if pr_meta is None:
        raise RuntimeError("Failed to resolve PR metadata.")

    return {
        "pull_request": pr_meta,
        "conversation_comments": comments,
        "reviews": reviews,
        "review_threads": threads,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub PR comments, reviews, and review threads for review-feedback workflows."
    )
    parser.add_argument("--pr-url", help="GitHub PR URL, e.g. https://github.com/owner/repo/pull/123")
    parser.add_argument("--pr-number", type=int, help="PR number when owner and repo can be inferred or provided")
    parser.add_argument("--owner", help="GitHub owner or org")
    parser.add_argument("--repo", help="GitHub repository name")
    parser.add_argument(
        "--include-resolved",
        action="store_true",
        help="Include resolved review threads. Unresolved threads are returned by default.",
    )
    return parser


def resolve_target(args: argparse.Namespace) -> tuple[str, str, int]:
    if args.pr_url:
        return parse_pr_url(args.pr_url)

    if args.pr_number is not None:
        owner = args.owner
        repo = args.repo
        if not owner or not repo:
            owner, repo = get_repo_from_context()
        return owner, repo, args.pr_number

    return get_current_branch_pr()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        ensure_gh_auth()
        owner, repo, number = resolve_target(args)
        result = fetch_all(owner, repo, number, include_resolved=args.include_resolved)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
