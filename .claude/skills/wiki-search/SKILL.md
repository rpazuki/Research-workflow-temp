---
name: wiki-search
description: >
  Unified 3-source literature search — WebSearch · Web of Science MCP · bioRxiv MCP.
  Trigger on: "search for papers on…", "find literature about…", "what papers exist on…",
  "do a literature search for…", or any request to discover new sources.
---

# Wiki SEARCH Workflow (Unified 3-Source)

This is a single, sequential workflow. Run all three sources, then produce one wiki page.

---

## ⚠️ Pre-flight check — MCP availability

This workflow uses **two MCPs** with different activation mechanisms in the Claudian Obsidian plugin:

| MCP | Type | How activated in Claudian |
|-----|------|--------------------------|
| `web-of-science` | **Local** server (`MCPs/wos-mcp/server.py`) | Requires `@web-of-science` in the message |
| `bioRxiv` | **Cloud** MCP (claude.ai) | Always available — no `@` needed, but always run it |

**Recommended search command template** (tell the user to use this every time):
> `search for <topic> @web-of-science MCP`
>
> bioRxiv is always active and will be searched automatically — no extra mention needed.

**Pre-flight checks:**

1. **Web of Science** — check whether `search_wos` is available:
   - **Available** → proceed.
   - **Not available** → tell the user:
     > "The Web of Science MCP is not active. Please include `@web-of-science` in your message — for example: *'search for protein language models @web-of-science MCP'* — then resend."
     Stop and wait. Do not proceed without WoS.

2. **bioRxiv** — check whether `mcp__claude_ai_bioRxiv__search_preprints` is available:
   - **Available** → it will be used in Phase 3. No action needed.
   - **Not available** → note in the search page: `_bioRxiv MCP not available in this session — skipped._` Proceed with Web + WoS only.

**Never skip bioRxiv silently.** If it is available, always run Phase 3 — it is mandatory for biological science topics, not optional.

---

## Phase 1 — Web Search

1. Run **3–5 `WebSearch` queries** covering different angles: broad terms, method names, key authors, recent years (include current year: 2026).

2. Compile results. Create the wiki search page at:
   `wiki/searches/search-<slugified-query>-<YYYYMMDD>.md`

   Use the frontmatter block:
   ```yaml
   ---
   title: "Search: <topic>"
   type: search
   tags: [search, <topic-tags>]
   query: "<exact WoS query used>"
   query_web: "<web search terms>"
   date: YYYY-MM-DD
   updated: YYYY-MM-DD
   total_results: 0
   returned_results: 0
   web_results: 0
   biorxiv_results: 0
   search_sources: [web]
   ---
   ```

3. Add section `## Results — Web Search` with numbered entries (`### WN. Short title`):
   authors · year · journal · DOI · citation count (`~` prefix for estimates) · abstract snippet.

4. Build the **Summary & Evaluation table** right after `## Query`:
   Columns: `#` · `Source` (Web / WoS / bioRxiv / Both) · `Title` (Obsidian wikilink `[[#WN. Exact heading]]`) · `Year` · `Citations` · `Relevance`.
   Sort descending by citations. Leave WoS and bioRxiv rows as placeholders for now.

---

## Phase 2 — Web of Science MCP

5. Construct a well-formed WoS advanced query using field tags:
   - `TS=` topic (title + abstract + keywords)
   - `TI=` title only
   - `AU=` author
   - `SO=` journal
   - Combine with `AND` / `OR` / `NOT`

6. Call `search_wos` with the query. Use `sort_field="TC"` (times cited) for high-impact results. Request `max_results=15`.

7. Add results to the page under `## Results — Web of Science` with entries numbered `### SN. Short title`. Mark any paper already in Web Search with `(also in Web Search #WN)`.

8. Update frontmatter: `total_results`, `returned_results`, add `"wos"` to `search_sources`.

---

## Phase 3 — bioRxiv MCP (conditional)

9. Decide: is this topic relevant to biological sciences (biochemistry, genomics, systems biology, metabolism, etc.)?

   - **Yes** → proceed.
   - **No** (e.g. pure maths, ML theory, engineering only) → skip Phase 3, note in the page: `_bioRxiv not searched — topic outside biological sciences scope._`

10. If applicable, call `mcp__claude_ai_bioRxiv__search_preprints` with:
    - `category`: the closest matching bioRxiv category
    - `date_from`: two years ago (YYYY-01-01)
    - `date_to`: today
    - `limit`: 10

    If the category is uncertain, run two narrower category searches and merge.

11. Add results under `## Results — bioRxiv` with entries numbered `### BN. Short title`. Mark duplicates with `(also in Web Search #WN)` or `(also in WoS #SN)`.

12. Update frontmatter: `biorxiv_results`, add `"biorxiv"` to `search_sources`.

---

## Phase 4 — Entity extraction

Before compiling the final page, scan all search results for **new entities** that lack a wiki page.

13. **Identify new entities** — for every result, ask: does this paper introduce or prominently feature a named model, tool, database, organism, or method that:
    - does not yet have a page in `wiki/entities/` or `wiki/concepts/`, **AND**
    - is referenced by two or more papers (or is a foundational/canonical work)?

    Typical signals: a named model (ESM-2, ProtBERT, GECKO…), a software tool (COBRApy, COMETS…), a database (BFD, UniRef…), an organism (*E. coli*, *S. cerevisiae*…), or a method with its own name (FSEOF, OptForce, dFBA…).

14. **Create entity pages** for every identified new entity — one `wiki/entities/<slug>.md` or `wiki/concepts/<slug>.md` per entity. Use the standard template:
    - **Entity pages:** Description · Key Properties · Mathematical Formulation (if applicable) · Role in research · Comparison with related entities · Related Concepts · Sources
    - **Concept pages:** Definition · Mathematical formulation · Variants / extensions · Key papers · See also

    Each entity page must:
    - Cross-link back to the search page: `[[searches/search-<slug>-<YYYYMMDD>]]` in its Sources or Related sections
    - Cross-link to any other existing wiki pages it relates to
    - Be added to `wiki/index.md` under `## Entities` or `## Concepts`

15. **Update existing entity/concept pages** — if a search result adds new information (a new citation, a benchmark result, a variant) to an *existing* entity page, add it there too. Update the `updated:` frontmatter date.

---

## Phase 5 — Compile, Wiki update, and follow-up

16. **Rebuild the Summary & Evaluation table** with all results merged:
    - Re-sort by citations descending.
    - Mark `Both` or `All` for papers appearing in multiple sources.
    - Prefix result numbers by source: `W` = Web, `S` = WoS, `B` = bioRxiv.

17. **Present a unified summary** to the user:
    - Total unique papers found
    - Key themes, methods, recurring authors
    - Papers appearing in multiple sources (highest confidence)
    - Any obvious gaps in the literature
    - Entity pages created or updated as part of this search

18. **Update `wiki/index.md`** — add under `## Searches`:
    `- [[search-<slug>-<YYYYMMDD>]] — <topic> (web · WoS · bioRxiv, YYYY-MM-DD)`
    Also add any new entity/concept pages under `## Entities` or `## Concepts`.

19. **Append to `wiki/log.md`**:
    ```
    ## [YYYY-MM-DD] search | <topic>
    Search page: wiki/searches/<filename>.md
    Sources: web · WoS · bioRxiv
    Entities created: <list of new entity/concept pages>
    Notes: <one sentence on coverage and key findings>
    ```

20. **Ask the user:**
    > "Would you like to download any of these papers to the raw folder?"

    If yes → call `download_paper` (from `@web-of-science` MCP) with the DOI and the appropriate `destination_folder="raw/<topic>/<subfolder>"`. After each successful download, update the `## Downloaded` section of the search page.

21. **Ask:**
    > "Should I add any downloaded papers to the INGEST queue?"

    If yes → note them in the `## Connections` section with `[INGEST candidate]` tag.

---

## Page section order

Required sections in this order:
**Query** · **Summary & Evaluation** (table) · **Results — Web Search** · **Results — Web of Science** · **Results — bioRxiv** · **Downloaded** · **Connections**

The **Summary & Evaluation table** must include these columns:
`#` · `Source` · `Title` (Obsidian in-page wikilink `[[#Exact heading]]`) · `Year` · `Relevance` (Foundational / High / Medium / Low) · `Download` (direct DOI or PMC link)

Each full detail section must include: **authors · year · journal · DOI/UID · keywords · abstract · key points**.

Entity pages created during this search are *separate files* (`wiki/entities/*.md`); they are not embedded in the search page — only linked from it via `[[entities/slug]]`.

## Wikilink rule for Summary table

Always use Obsidian in-page wikilink syntax `[[#WN. Exact heading text]]`.
Never use Markdown anchor links `[text](#anchor)` — they do not resolve in Obsidian.
When a heading contains markdown emphasis (e.g. `*confirmed*`), use the plain rendered text in the link.

## Merge rules (if adding sources to an existing search page)

1. Update frontmatter counts and `search_sources`.
2. Append the new results section below the existing ones.
3. Mark duplicates with `(also in <other source> #N)`.
4. Rebuild the Summary & Evaluation table (re-sort, update Source column, mark `Both`/`All`).
5. Set `updated:` to today in frontmatter.
