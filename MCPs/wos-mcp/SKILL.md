# Web of Science Search & Download Skill

## Purpose
This skill enables Claude to search the **Web of Science Core Collection** (Smart Search) via the Clarivate API — the same premium database available through your university library — and to download papers to a local curated folder using DOIs or direct URLs.

It operates **in parallel with Claude's built-in web search**: for any scientific query, Claude will search both its internal capabilities and Web of Science, then synthesise and rank the results.

---

## When to use this skill
Trigger this skill whenever the user asks Claude to:
- Search for scientific papers, articles, or reviews (e.g. "find papers on X", "search for recent work on Y")
- Look up citations, authors, or journals in Web of Science
- Retrieve metadata (abstracts, authors, DOIs, citation counts) for a paper
- Download a paper from a DOI or a URL into the curated folder
- List papers already saved in the curated folder

---

## How to invoke each tool

### 1. `search_wos` — Search Web of Science
Use this for any scientific literature query.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The search phrase (topic, title keyword, author, etc.) |
| `max_results` | int | 10 | Number of results to return (max 100) |
| `database` | string | `"WOS"` | Database ID — use `"WOS"` for Core Collection |
| `sort_field` | string | `"RS"` | Sort order: `RS`=relevance, `TC`=times cited, `PY`=pub year |
| `year_from` | int | None | Filter: earliest publication year |
| `year_to` | int | None | Filter: latest publication year |
| `doc_type` | string | None | Filter: e.g. `"Article"`, `"Review"`, `"Proceedings"` |

**Query syntax tips (Web of Science field tags):**
- `TS=quantum computing` — topic (title + abstract + keywords)
- `TI=machine learning` — title only
- `AU=Smith J` — author
- `SO=Nature` — journal/source title
- `DO=10.1038/...` — DOI
- Combine with `AND`, `OR`, `NOT`

**Example Claude usage:**
> "Search for papers on CRISPR gene editing published after 2020, sorted by citation count"
→ Call `search_wos(query="TS=CRISPR gene editing", year_from=2021, sort_field="TC")`

---

### 2. `get_record` — Get full record details
Use to retrieve the complete metadata for a specific Web of Science record.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `record_id` | string | The WOS record UID (e.g. `WOS:000123456789012`) |

Returns: full abstract, all authors, all keywords, journal, volume, issue, pages, DOI, citation count, references.

---

### 3. `download_paper` — Download a paper to the curated folder
Use whenever a user wants to save a paper locally.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `doi` | string | None | DOI of the paper (e.g. `10.1038/s41586-021-03819-2`) |
| `url` | string | None | Direct URL to the paper PDF |
| `filename` | string | None | Optional custom filename (without extension) |

**Behaviour:**
1. If a DOI is provided, first checks **Unpaywall** for a legal open-access PDF
2. If no open-access version found, attempts direct publisher URL resolution
3. Downloads the PDF to the `curated/` subfolder next to this skill
4. Returns the local file path and metadata

**Note:** This tool only downloads legally accessible (open access) PDFs. For paywalled papers, it returns the best available metadata and the publisher URL so the user can download manually through their institutional access.

---

### 4. `list_curated` — List downloaded papers
Use to show the user what papers have been saved locally.

Returns a formatted list of all PDFs in the `curated/` folder with filenames and sizes.

---

## Parallel search strategy
When the user asks for a literature search, Claude should:
1. Run `search_wos` with a well-constructed WoS query
2. Simultaneously use Claude's built-in web search for the same topic
3. Merge and deduplicate results, preferring WoS records (which include citation counts and verified metadata)
4. Present a unified ranked list to the user

---

## Configuration
The MCP server reads its configuration from `wos-mcp/config.json` (or environment variables). Required settings:

```json
{
  "wos_api_key": "YOUR_CLARIVATE_API_KEY",
  "unpaywall_email": "your@email.com",
  "curated_folder": "./curated"
}
```

**Getting a WoS API key:**
Your university library's Web of Science access includes API access via Clarivate's Developer Portal. Contact your library's digital resources team and request an API key for the Web of Science Expanded API, referencing your institutional subscription.

---

## Setup instructions
See `README.md` in the `wos-mcp/` folder for full installation and Claude Desktop integration steps.
