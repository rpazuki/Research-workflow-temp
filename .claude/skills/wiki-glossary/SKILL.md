---
name: wiki-glossary
description: Add or update a glossary entry and its entity page in the Research Wiki. Trigger when the user asks to define a term, add something to the glossary, look up and document a concept, or create an entity page — phrases like "add X to the glossary", "what is X — add it", "create a glossary entry for", "document this entity", or when a new term surfaces during INGEST or TALK NOTES that lacks a wiki page.
---

# Wiki GLOSSARY Workflow

The glossary is a two-tier system:
- **`wiki/glossary.md`** — lightweight alphabetical index with 1–2 sentence definitions and links to entity pages.
- **`wiki/entities/<term>.md`** — comprehensive pages with research detail, structural properties, domain role, and cross-references.

> **Page conventions:** Frontmatter schemas and log/index formats are in `CLAUDE.md`.

## Steps

### 1. Research the term

- Search `wiki/index.md` and any relevant existing pages to see if the term is already documented.
- Run one or more `WebSearch` queries to find: authoritative definitions, key structural properties, role in the research domain, and notable examples or instances.
- Summarise your findings (with sources) and share them with the user before writing anything. Ask for approval to proceed.

### 2. Create or update the entity page

Check whether `wiki/entities/<slugified-term>.md` exists. If it does, read it before making changes.

Entity page structure:

```markdown
---
title: "<Term>"
type: entity
tags: [...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: 0
---

## Description
<Comprehensive definition — 2–3 paragraphs>

## Key properties / characteristics
<Bulleted or sectioned details from research>

## Role in [domain]
<How this term relates to the user's research domain>

## Examples / instances
<Specific organisms, tools, databases, or models — if applicable>

## Related concepts
<[[wikilinks]] to related concept and entity pages>

## Sources
<Web references and/or wiki source pages that informed this entry>
```

Update `updated:` if modifying an existing page.

### 3. Write the glossary entry

Find the correct alphabetical position in `wiki/glossary.md` (sort case-insensitively; ignore leading articles "a", "an", "the"). Insert:

```
**Term** — concise 1–2 sentence definition; see [[entity-page]] for details.
```

Keep the glossary entry brief — all elaboration lives in the entity page.

### 4. Cross-reference

- In the entity page's **Related concepts** section, add `[[wikilinks]]` to other pages that discuss this term.
- In any existing wiki pages that mention this term for the first time, add a wikilink to the glossary: `[[glossary#Term|term]]`.
- If the entity page is new, add a backlink from closely related entity or concept pages.

### 5. Update metadata

- Add the new entry to `wiki/index.md` under `## Entities`: `- [[entity-slug]] — one-line description`.
- Append to `wiki/log.md`:
  ```
  ## [YYYY-MM-DD] glossary | <term>
  Entity page: wiki/entities/<slug>.md (created | updated)
  Glossary entry: wiki/glossary.md
  Cross-references: <list of pages updated>
  Notes: <one sentence on key findings>
  ```
