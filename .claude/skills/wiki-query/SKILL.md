---
name: wiki-query
description: Answer a research question using the wiki knowledge base. Trigger when the user asks a question about FBA, metabolic modelling, or any topic covered in the wiki — phrases like "what is...", "how does...", "compare X and Y", "explain...", "which papers cover...", or any direct question that should be answered from existing wiki pages rather than new literature.
---

# Wiki QUERY Workflow

You are synthesising an answer from the existing wiki knowledge base.

> **Page conventions:** Cross-referencing style and log/index formats are in `CLAUDE.md`.

## Steps

1. **Read `wiki/index.md`** to identify which source, concept, entity, and analysis pages are relevant to the user's question.

2. **Read those pages** and synthesise a coherent answer. Use inline `[[page-name]]` wikilinks to cite every claim.

3. **Present the answer to the user.** Be concise — lead with the direct answer, then supporting detail.

4. **Ask the user:** "Should I save this as a new analysis page?"

5. **If yes:** Write to `wiki/analyses/<slug>.md` with the required sections:
   - **Question** — the exact question asked
   - **Answer** — your synthesised response
   - **Evidence** — wikilinks to every source/concept/entity page cited
   - **Confidence** — high / medium / low, with brief justification
   - **Gaps** — what the wiki does not currently cover that would sharpen the answer

   Then update `wiki/index.md` (add entry under `## Analyses`) and append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] query | <short question title>
   Analysis page: wiki/analyses/<slug>.md
   Pages cited: <comma-separated list>
   Notes: <one sentence>
   ```

## When the wiki is insufficient

If the question cannot be adequately answered from existing wiki pages, tell the user what is missing and suggest either a SEARCH (to find new literature) or an INGEST (if they already have the relevant paper).
