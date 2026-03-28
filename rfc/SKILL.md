---
name: rfc
description: Create or work on an RFC (Request for Comments). Use when the user wants to start a new RFC, discuss a feature/architecture proposal, or work on an existing RFC.
---

# RFC - Request for Comments

Lightweight decision records for features, architecture, and technical discussions. RFCs live in the repo so decisions are searchable, reviewable, and permanent - even rejected or postponed ones.

## Workflow

1. **Branch:** Create a branch named `rfc/<short-slug>` using lowercase letters, numbers, and hyphens (e.g., `rfc/api-rate-limiting`). Do not use underscores.
2. **Folder:** Add a subfolder under `rfcs/` named `YYYY-MM-short-slug` (e.g., `2026-03-api-rate-limiting`). Use the creation date, not the merge date.
3. **README.md:** Every RFC must have one - it's the entry point (see structure below).
4. **Supporting docs:** Add whichever files make sense for the discussion. Nothing beyond the README is mandatory.
5. **PR:** Open a Pull Request with `[RFC]` prefix in the title and an `rfc` label. This is where discussion happens.
6. **Merge:** All RFCs get merged regardless of outcome. The final `status` in README.md records the decision.

## README.md structure

Every RFC README starts with a YAML frontmatter header:

```yaml
---
status: under_discussion
date: 2026-03-27
---
```

Below the frontmatter, include at minimum:
- **Title** as an H1
- **Summary:** one or two sentences - what is this about and why now
- **Links:** pointers to relevant tickets, PRs, issue threads, related RFCs - whatever applies

Keep it minimal. The README is an index card, not the full discussion - details go in supporting docs.

## Status lifecycle

| Status             | Meaning                                                |
|--------------------|--------------------------------------------------------|
| `under_discussion` | Being written or under discussion                      |
| `in_progress`      | Accepted and actively being implemented                |
| `done`             | Implementation complete                                |
| `rejected`         | Decided against - rationale should be in the PR/README |
| `postponed`        | Valid idea, not now - revisit later                    |

## Common supporting files

Pick what fits. These are suggestions, not requirements:

| File                     | Use case                                                       |
|--------------------------|----------------------------------------------------------------|
| `prd.md`                 | Product-facing: problem, users, success metrics, scope         |
| `technical_design.md`    | Architecture/system design: approach, alternatives, trade-offs |
| `implementation_plan.md` | Phased rollout, task breakdown, dependencies                   |
| `customer_success.md`    | CS input: pain points, customer quotes, support patterns       |
| `qa_plan.md`             | Testing strategy for non-trivial QA needs                      |

You can add any other file that makes sense (diagrams, benchmarks, spikes...).
