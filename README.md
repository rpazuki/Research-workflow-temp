# Research Wiki Template

A personal research wiki maintained by an AI agent (Claude). Drop papers into `raw/`, ask Claude to ingest them, and the wiki grows automatically — source pages, concept pages, entity pages, cross-references, and a searchable glossary, all in plain Markdown.

Designed to open in [Obsidian](https://obsidian.md) — backlinks, graph view, and LaTeX rendering work out of the box.

---

## Quick start

### 1. Set up a new project from this template

Follow **[SETUP.md](SETUP.md)**. The short version:

1. Rename the root folder to your topic
2. Create `raw/<YourTopic>/` and drop PDFs in
3. Replace `<topic>` tags in `wiki/index.md`, `wiki/overview.md`, `wiki/glossary.md`
4. `cp MCPs/wos-mcp/config.json.example MCPs/wos-mcp/config.json` and add your email

### 2. Install the WoS MCP server (one-time)

```bash
cd MCPs/wos-mcp
pip install -r requirements.txt
playwright install chromium
```

Register with Claude (from the project root):

```bash
claude mcp add web-of-science -- python MCPs/wos-mcp/server.py
```

See **[MCPs/wos-mcp/README.md](MCPs/wos-mcp/README.md)** for full installation and Claude Desktop instructions.

### 3. Authenticate Web of Science (one-time)

In a Claude session, say:
```
Use the authenticate_wos tool
```
A browser window opens for your institutional SSO login. The session is cached for future searches.

---

## Workflows

The agent reads a skill file before executing each workflow. All skill files live in `.claude/skills/`.

| Workflow | When to use | Trigger phrase |
|----------|-------------|----------------|
| **INGEST** | Add a paper or PDF to the wiki | "Ingest `raw/<topic>/paper.pdf`" |
| **SEARCH** | Search the literature (WebSearch + WoS + bioRxiv) | "Search for papers on X @web-of-science" |
| **CONCEPT SEARCH** | You can describe an idea but don't know its field term | "Find papers about methods that do X" |
| **QUERY** | Answer a question from existing wiki pages | "What does the wiki say about X?" |
| **GLOSSARY** | Add or update a glossary entry and entity page | "Add X to the glossary" |
| **TALK NOTES** | Process seminar or lecture notes into the wiki | "Process these talk notes" |
| **SPARSE TALK NOTES** | Enrich brief bullet notes with online research | "Enrich these sparse notes" |
| **LINT** | Health-check the wiki for broken links and gaps | "Lint the wiki" |

---

## Directory layout

```
<project>/
├── raw/                    ← immutable source documents (never modified by agent)
│   └── <Topic>/            ← one subfolder per research topic
├── wiki/                   ← agent-maintained knowledge base
│   ├── index.md            ← master catalog (updated on every change)
│   ├── log.md              ← append-only operation log
│   ├── overview.md         ← evolving field synthesis
│   ├── glossary.md         ← alphabetical term definitions
│   ├── concepts/           ← methods, algorithms, mathematical ideas
│   ├── entities/           ← organisms, tools, databases, models
│   ├── sources/            ← one page per ingested document
│   ├── analyses/           ← comparisons, deep dives, query answers
│   └── searches/           ← saved literature search results
├── MCPs/
│   └── wos-mcp/            ← Web of Science MCP server
├── .claude/
│   ├── CLAUDE.md           ← agent schema and conventions
│   ├── skills/             ← workflow skill files
│   └── mcp.json            ← MCP server registration
├── .gitignore
├── SETUP.md                ← new-project onboarding checklist
└── README.md               ← this file
```

---

## Wiki page conventions

All pages use YAML frontmatter:

```yaml
---
title: "Page title"
type: concept | entity | source | analysis | overview
tags: [<topic>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: 0
---
```

Cross-references use Obsidian wikilink syntax: `[[page-name]]`. See `.claude/CLAUDE.md` for full page-type schemas (required sections, citation rules, cross-referencing style, and log/index formats).

---

## Privacy & version control

- `MCPs/wos-mcp/browser-session/` — browser cookies; gitignored, keep private
- `MCPs/wos-mcp/config.json` — your email address; gitignored. Commit `config.json.example` instead
- `raw/` — source PDFs may be large; consider adding to `.gitignore` or using Git LFS
