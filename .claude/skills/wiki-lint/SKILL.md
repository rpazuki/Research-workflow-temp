---
name: wiki-lint
description: Run a health check on the Research Wiki to find and fix structural problems. Trigger when the user asks to check the wiki's health, fix broken links, find orphan pages, or audit consistency — phrases like "lint the wiki", "check for broken links", "find orphan pages", "audit the wiki", "health check", or "are there any inconsistencies in the wiki".
---

# Wiki LINT Workflow

A structural health check that finds and reports problems across all wiki pages, then fixes the ones the user approves.

> **Page conventions:** Cross-referencing style, index and log formats are in `CLAUDE.md`.

## What to scan for

Work through each category in order. Number every finding consecutively so the user can reference them by number.

| # | Category | What to look for |
|---|----------|-----------------|
| 1 | **Broken wikilinks** | `[[page-name]]` references that point to a page that does not exist in `wiki/` |
| 2 | **Missing concept/entity pages** | Concepts or entities mentioned in source pages but without their own `wiki/concepts/` or `wiki/entities/` page |
| 3 | **Orphan pages** | Pages in `wiki/` with no inbound wikilinks from any other page (not referenced anywhere) |
| 4 | **Index gaps** | Pages that exist in `wiki/` but are missing from `wiki/index.md` |
| 5 | **Stale or contradicted claims** | Claims in older pages that are superseded or contradicted by newer sources; flag where a **Contested** callout should be added |
| 6 | **Frontmatter issues** | Missing required fields (`title`, `type`, `created`, `updated`, `tags`) in any wiki page |

## Steps

1. **Read `wiki/index.md`** to get the complete list of known pages.

2. **Scan all files** in `wiki/` (sources, concepts, entities, analyses, searches). Extract all `[[wikilinks]]` and cross-reference them against the index and actual files on disk.

3. **Compile a numbered findings list** grouped by category. Present it to the user.

4. **Ask the user which items to fix.** The user may say "fix all", approve individual numbers, or say "just report — don't fix."

5. **Fix approved items.** Common fixes:
   - Broken link → correct the slug or create the missing stub page.
   - Missing page → create a minimal stub with correct frontmatter and a "stub" tag.
   - Orphan → add a link from the most relevant related page.
   - Index gap → add the entry to `wiki/index.md`.
   - Stale claim → add a **Contested** callout (format in `CLAUDE.md`).
   - Frontmatter → add the missing field.

6. **Append to `wiki/log.md`:**
   ```
   ## [YYYY-MM-DD] lint | health check
   Findings: <N total — breakdown by category>
   Fixed: <list of items fixed, or "none">
   Deferred: <list of items the user did not approve>
   ```
