# New Project Setup Checklist

Follow these steps when starting a new research project from this template.

---

## 1. Rename the project folder

Rename the root folder from its current name to your project/topic name (e.g. `Thermodynamics`, `ProteinFolding`, `ClimateModelling`).

## 2. Create your raw folder

Create a subfolder under `raw/` named after your topic:

```
raw/<YourTopic>/
```

This is where all immutable source documents (PDFs, HTML, images) will live.

## 3. Update the wiki scaffold tags

In each of the following files, replace `<topic>` with your topic name (lowercase, hyphenated):

- `wiki/index.md` — `tags: [index, <topic>]`
- `wiki/overview.md` — `tags: [<topic>, overview]` and the page title/heading
- `wiki/glossary.md` — `tags: [glossary, <topic>]`

## 4. Configure the WoS MCP

```bash
cp MCPs/wos-mcp/config.json.example MCPs/wos-mcp/config.json
```

Then edit `config.json` and replace `your.email@institution.ac.uk` with your institutional email address. This is used by the Unpaywall API for open-access PDF downloads.

## 5. Authenticate Web of Science

Open a session and run the `authenticate_wos` tool (or include `@web-of-science` in your first search message). This opens a browser window for your institutional login — the session is cached in `MCPs/wos-mcp/browser-session/`.

## 6. Update the CLAUDE.md directory layout (optional)

The directory layout example in `.claude/CLAUDE.md` shows `raw/FBA/` as an example. You can update this to reflect your actual topic — it's illustrative only and does not affect agent behaviour.

## 7. Add a log entry

When you start ingesting your first paper, the agent will automatically append to `wiki/log.md`. You're ready to go.

---

## Quick-start commands

| What you want to do | Say to the agent |
|---------------------|-----------------|
| Add a paper to the wiki | "Ingest `raw/<topic>/paper.pdf`" |
| Search the literature | "Search for papers on `<topic>` @web-of-science MCP" |
| Answer a question from the wiki | "What does the wiki say about `<concept>`?" |
| Add a term to the glossary | "Add `<term>` to the glossary" |
| Health-check the wiki | "Lint the wiki" |
