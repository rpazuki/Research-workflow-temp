---
name: wiki-ingest
description: Ingest a new research paper, PDF, or HTML source into the Research Wiki. Trigger when the user asks to add, process, or ingest a paper/PDF/article — phrases like "add this paper", "process this PDF", "ingest this source", "read and summarise for the wiki", or when a raw/ file path is mentioned alongside a request to document it.
---

# Wiki INGEST Workflow

You are ingesting a new source document into the research wiki at `Research_vault/wiki/`.

> **Page conventions:** All frontmatter schemas, required page sections, cross-referencing style, and log/index formats are defined in `CLAUDE.md`. Read it if you need a reminder — do not duplicate those details here.

## Steps

1. **Read the source document.** Use the `Read` tool on the provided file path. For PDFs with embedded images, note image filenames and view them separately where needed.

2. **Discuss key takeaways before writing anything.** Summarise the paper's core contribution in 3–5 bullets and confirm with the user. Only proceed once satisfied.

3. **Write the source page** at `wiki/sources/<slugified-title>.md`.
   Required sections: Citation · Raw path · Summary · Key claims · Methods · Limitations · Connections · Quotes

4. **Update concept pages** (`wiki/concepts/`) for every significant concept, method, or algorithm the paper introduces or meaningfully addresses.
   - Check `wiki/index.md` first; extend an existing page or create a new one.
   - Required sections: Definition · Mathematical formulation (if applicable) · Variants / extensions · Key papers · See also
   - Use LaTeX inline (`$...$`) for all equations.

5. **Update entity pages** (`wiki/entities/`) for every organism, software tool, database, or model the paper centres on.
   - Required sections: Description · Role in research · Key papers · See also

6. **Update `wiki/overview.md`** if the source meaningfully shifts the big picture. Skip for incremental contributions.

7. **Update `wiki/index.md`** — add the new source page and any new/updated concept or entity pages under `## Sources`, `## Concepts`, `## Entities`. Format: `- [[slug]] — one-line description`.

8. **Append to `wiki/log.md`:**
   ```
   ## [YYYY-MM-DD] ingest | <paper short title>
   Source page: wiki/sources/<slug>.md
   Pages touched: <comma-separated list>
   Notes: <one sentence on the paper's key contribution>
   ```

## Quality checks

- Every concept/entity mentioned in the source page must link to an existing wiki page or have a new page created.
- Use `[[page-name]]` wikilinks on first mention; see CLAUDE.md for the **Contested** callout format.
- Never modify files in `raw/` — they are immutable.
