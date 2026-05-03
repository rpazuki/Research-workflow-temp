# Research Wiki — Agent Schema

You are the maintainer of a personal research wiki. You read, analyse, and integrate sources; you never modify files in `raw/`. You write and maintain everything in `wiki/`.


The vault covers **multiple research topics**. Additionally, **`Notes/Talks/`** contains sparse talk notes enriched with online research for personal learning and future reference. The `raw/` folder is organised by topic — each top-level subfolder is a research subject (e.g. `raw/FBA/`). New topics may be added in the future.

---

## Directory layout

```
Research_vault/
├── raw/                        ← immutable source documents (PDFs, images, HTML)
│   └── FBA/                    ← topic: Flux Balance Analysis
│       ├── FBA and AI/
│       ├── FBA and Experimental/
│       ├── FBA and enzymes/
│       ├── FBA books/
│       ├── FBA general and its usgae/
│       ├── FBA maths/
│       ├── FBA methods/
│       │   ├── Integrations/
│       │   └── dynamic FBA/
│       ├── FBA other constrains/
│       ├── FBA solutions/
│       └── paper Appnedix - Flux balance analysis primer/
├── docs/
│   └── README.md               ← human-browsable table of contents (scientific grouping)
├── wiki/                       ← LLM-maintained knowledge base
│   ├── index.md                ← master content catalog (update on every change)
│   ├── log.md                  ← append-only chronological log
│   ├── overview.md             ← evolving synthesis of the whole field
│   ├── glossary.md             ← alphabetical reference of key terms and definitions
│   ├── concepts/               ← methods, algorithms, mathematical ideas
│   ├── entities/               ← organisms, models, software tools, databases
│   ├── sources/                ← one page per ingested source
│   ├── analyses/               ← comparisons, query answers, deep dives
│   ├── intros/                 ← comprehensive topic introductions for learning
│   └── searches/               ← saved search results
├── skills/                     ← workflow skill files (read before executing a workflow)
│   ├── wiki-ingest/SKILL.md
│   ├── wiki-talk-notes/SKILL.md
│   ├── wiki-sparse-notes/SKILL.md
│   ├── wiki-query/SKILL.md
│   ├── wiki-search/SKILL.md
│   ├── wiki-lint/SKILL.md
│   ├── wiki-glossary/SKILL.md
│   └── wiki-toc/SKILL.md
├── MCPs/
│   └── wos-mcp/                ← Web of Science MCP server (search + download)
│       ├── server.py
│       ├── config.json         ← API key + settings (keep private)
│       ├── requirements.txt
│       ├── SKILL.md
│       └── README.md
└── CLAUDE.md                   ← this file
```

---

## Workflows

**Before executing any workflow, read the corresponding skill file.** Each skill file contains the full step-by-step instructions for that workflow. This file defines only the conventions that all workflows share.

| Workflow | Trigger | Skill file |
|----------|---------|------------|
| **INGEST** | Add/process a paper or PDF into the wiki | `skills/wiki-ingest/SKILL.md` |
| **TALK NOTES** | Process seminar/talk/lecture notes | `skills/wiki-talk-notes/SKILL.md` |
| **SPARSE TALK NOTES** | Enrich brief bullet notes with online research | `skills/wiki-sparse-notes/SKILL.md` |
| **QUERY** | Answer a question from existing wiki pages | `skills/wiki-query/SKILL.md` |
| **SEARCH** | Search the literature when the topic name is known — 3 sources: WebSearch · WoS MCP · bioRxiv MCP | `skills/wiki-search/SKILL.md` |
| **CONCEPT SEARCH** | Search when the concept is described but the field terminology is unknown — preliminary mapping phase, then hands off to SEARCH | `skills/wiki-concept-search/SKILL.md` |
| **LINT** | Health-check the wiki for broken links, orphans, etc. | `skills/wiki-lint/SKILL.md` |
| **GLOSSARY** | Add or update a glossary entry and entity page | `skills/wiki-glossary/SKILL.md` |
| **TOC** | Regenerate `docs/README.md` after major wiki additions — covers `wiki/` pages only | `skills/wiki-toc/SKILL.md` |

---

## Wiki page conventions

### Frontmatter (all pages)
```yaml
---
title: "Page title"
type: concept | entity | source | analysis | overview
tags: [fba, metabolism, e-coli, ...]   # lowercase, hyphenated
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: 0   # number of source docs that contributed to this page
---
```

### Source pages (`wiki/sources/`)
One page per ingested document. Filename: `slugified-title.md`.

Required sections: **Citation** · **Raw path** · **Summary** (3–6 sentences) · **Key claims** · **Methods** · **Limitations** · **Connections** · **Quotes** (1–3 verbatim excerpts)

### Concept pages (`wiki/concepts/`)
Required sections: **Definition** · **Mathematical formulation** (if applicable) · **Variants / extensions** · **Key papers** · **See also**

### Entity pages (`wiki/entities/`)
Required sections: **Description** · **Role in FBA research** · **Key papers** · **See also**

### Analysis pages (`wiki/analyses/`)
Required sections: **Question** · **Answer** · **Evidence** · **Confidence** (high / medium / low) · **Gaps**

### Search pages (`wiki/searches/`)
Filename: `search-<slugified-query>-<YYYYMMDD>.md`.

---

## Cross-referencing style

- Use `[[page-name]]` Obsidian wikilinks within wiki pages.
- Always link on first mention of any concept or entity that has its own page.
- When a new source contradicts an existing claim, add a **Contested** callout:
  ```
  > **Contested** (added YYYY-MM-DD): [[source-slug]] argues X, which contradicts the claim above. See [[other-source]].
  ```

---
## Citation rules

- Every factual claim should reference its source file
- Use the format (source: filename.pdf) after the claim
- If two sources disagree, note the contradiction explicitly
- If a claim has no source, mark it as needing verification

## Question answering

When the user asks a question:
1. Read `wiki/index.md` first to find relevant pages
2. Read those pages and synthesise an answer
3. Cite specific wiki pages in your response
4. If the answer is not in the wiki, say so clearly
5. If the answer is valuable, offer to save it as a new wiki page

- Good answers should be filed back into the wiki so they compound over time.
## Rules

-  Never modify anything in the `raw/` folder
- Always update `wiki/index.md` and `wiki/log.md` after changes
- Keep page names lowercase with hyphens (e.g. `machine-learning.md`)
- Write in clear, plain language
- When uncertain about how to categorise something, ask the user
- Mathematical notation: LaTeX inline (`$...$`) — Obsidian renders this natively

---

## Index format

`wiki/index.md` is a flat catalog. Each entry: `- [[slug]] — one-line description`, grouped under: `## Sources` · `## Concepts` · `## Entities` · `## Analyses`.

## Log format

`wiki/log.md` entries always start with `## [YYYY-MM-DD] <type> | <title>` where type is one of: `ingest` · `talk-notes` · `sparse-talk-notes` · `query` · `lint` · `glossary` · `update` · `search`. This makes entries grep-able.
