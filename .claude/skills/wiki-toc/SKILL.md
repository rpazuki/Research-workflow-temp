# SKILL: TOC — Regenerate the Wiki Table of Contents

## Trigger

User asks to "update the TOC", "regenerate the table of contents", "refresh the TOC", "rebuild the ToC", or "update index.md".

---

## Purpose

`index.md` is a **scientifically organised, human-browsable** table of contents for the wiki. It groups pages by research theme and concept hierarchy — not by folder structure or file type. It is separate from `wiki/index.md`, which is a flat machine-readable catalogue for LLM queries.

---

## Steps

### 1 · Read the current state of the wiki

```
Read wiki/index.md          ← full list of all pages and their descriptions
Read index.md            ← existing ToC to understand current structure
```

Also read `wiki/log.md` (last 50 lines) to understand what has changed since the last ToC update.

### 2 · Identify what is new or changed

Compare `wiki/index.md` against the current `index.md`:
- Pages present in `index.md` but missing from `toc.md` → must be added
- Pages in `toc.md` that no longer exist → remove or mark
- New research domains (new top-level topic areas) → may require a new Part

### 3 · Determine correct scientific placement

For each new page, decide which section it belongs to based on **scientific meaning**, not folder:

| Scientific theme → | Section |
|--------------------|---------|
| FBA core LP, solution space, underdeterminacy | §1 Mathematical Foundations |
| pFBA, dFBA, ecFBA | §2 Core FBA Variants |
| FVA, flux sampling, Pareto | §3 Solution Analysis & Uncertainty |
| Thermodynamics, enzyme capacity, NED genes, Braess | §4 Constraints Beyond Stoichiometry |
| GIMME, iMAT, LBFBA, transcriptomics | §5 Omics Data Integration |
| AMN, MINN, FCL, dAMN, hybrid ML | §6 AI/ML-Enhanced FBA |
| MICOM, COMETS, syntrophic, community | §7 Community & Multi-Organism Modelling |
| MOMA, OptKnock, ALE, strain engineering | §8 Evolutionary Dynamics & Strain Engineering |
| COBRA, CHRR, BayFlux (software) | §9 Software & Computational Tools |
| E. coli, S. cerevisiae, Y. lipolytica (organisms) | §10 Model Organisms |
| Taste prediction, umami, food ML | §11 Taste Prediction & ML |
| ESM, ProtBERT, ProtT5, Ankh | §12 Protein Language Models |
| Undergraduate topic introductions | Part III Introductory Resources |
| Seminar/talk notes | Part IV Talks & Personal Notes |
| Analyses | Part V Analyses |
| Search records | Part V Searches |

**New research domains** (pages that don't fit any existing section): create a new Part or section and note it in the log.

### 4 · Write the updated `index.md`

- Keep the existing structure; insert new rows in the correct table
- Each row uses **standard Markdown links**, not Obsidian wikilinks:
  `| [Human-Readable Title](wiki/path/to/file.md) | type | one-line description |`
- Path pattern: always `wiki/<subfolder>/<slug>.md` (relative from the repo root)
- Use a human-readable title as link text (e.g. `Flux Balance Analysis`, `Orth et al. 2010`), not the raw slug
- Use the description from `wiki/index.md` as the basis for the one-liner
- If a new section is needed, add it with a brief italicised scope note
- Update the `updated:` frontmatter field to today's date
- Update the "Last updated" footer line

### 5 · Update `wiki/log.md`

Append one entry:

```markdown
## [YYYY-MM-DD] toc | Table of contents regenerated

- Added N pages: [[slug1]], [[slug2]], ...
- New sections (if any): ...
- Removed N stale entries (if any)
```

---

## What NOT to do

- Do **not** include pages outside `wiki/` — the ToC scope is strictly `wiki/**/*.md`. Excluded:
  - `Notes/Talks/` seminar notes (they live outside the wiki folder)
  - `raw/` inventory listings from `index.md`
  - Any other vault files not under `wiki/`
- Do **not** mirror the folder structure (`sources/`, `concepts/`, `entities/` — these are file-type groups, not scientific themes)
- Do **not** modify `wiki/index.md` — that is maintained by INGEST/SEARCH/etc.
- Do **not** delete sections that are temporarily empty; leave them with the scope note only

---

## Output

Confirm to the user:
- How many new pages were added to the ToC
- Which sections were affected
- Whether any new sections/parts were created
