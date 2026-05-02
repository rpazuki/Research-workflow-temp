# Web of Science MCP Server — Browser Automation Edition

Gives Claude access to **Web of Science Core Collection** (Smart Search) via
Playwright browser automation, using your Imperial College London
institutional SSO session — **no Clarivate developer API key required**.

---

## What it does

| Tool | Description |
|------|-------------|
| `authenticate_wos` | Opens a visible browser for one-time SSO login; saves session to disk |
| `search_wos` | Search WoS Core Collection headlessly using your saved session |
| `get_record` | Fetch full metadata for a specific WoS UID or DOI |
| `download_paper` | Download open-access PDFs via Unpaywall; returns publisher URL for paywalled papers |
| `save_search_to_wiki` | Persist search results as a structured Markdown page in `wiki/searches/` |
| `list_curated` | List all PDFs saved in the `curated/` folder |

---

## Prerequisites

- **Python 3.11+** — check with `python --version`
- **Imperial College London** (or equivalent) subscription to Web of Science
- **Claude Desktop** (or any MCP-compatible host)

---

## Installation

### Step 1 — Install Python dependencies

Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 2 — Install the Chromium browser for Playwright

This is a **separate step** that downloads a bundled Chromium (~180 MB):

```bash
playwright install chromium
```

> **Tip:** If you prefer a virtual environment (recommended):
> ```bash
> python -m venv .venv
> .venv\Scripts\activate          # Windows
> # source .venv/bin/activate    # macOS/Linux
> pip install -r requirements.txt
> playwright install chromium
> ```

### Step 3 — Configure the server (optional)

Edit `config.json` to set your email for the Unpaywall open-access API
(used when downloading papers):

```json
{
  "unpaywall_email": "r.pazuki@imperial.ac.uk",
  "curated_folder": "./curated"
}
```

The `wos_api_key` field is no longer required and can be left blank or removed.

### Step 4 — Register the MCP server

Registration differs depending on whether you use **Claude Desktop** (the
standalone app) or **Claude Code** (the CLI / VS Code agent). Follow the
section that matches your setup.

---

#### Option A — Claude Desktop

Open your Claude Desktop configuration file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the following inside the `"mcpServers"` object:

```json
{
  "mcpServers": {
    "web-of-science": {
      "command": "python",
      "args": [
        "C:/Users/rh2310/OneDrive - Imperial College London/Documents/Claude/Research_vault/MCPs/wos-mcp/server.py"
      ]
    }
  }
}
```

> **If using a virtual environment**, replace `"python"` with the full path to
> the venv interpreter, e.g.:
> `"C:/Users/rh2310/.../wos-mcp/.venv/Scripts/python.exe"`

Restart Claude Desktop after saving. You should see **"web-of-science"** in the
MCP tools list.

---

#### Option B — Claude Code (CLI / VS Code extension)

Claude Code manages MCP servers via its own config, **not**
`claude_desktop_config.json`. Use the `claude mcp add` command from a terminal
**inside the vault directory**:

```bash
cd C:\Users\rh2310\Research_vault

claude mcp add web-of-science -- python MCPs/wos-mcp/server.py
```

This writes the server definition into `.claude/settings.local.json` (project
scope). You can verify it was registered:

```bash
claude mcp list
```

You should see `web-of-science` in the output. Then **restart your Claude Code
session** (`/exit` and relaunch, or reload the VS Code window). The WoS tools
(`authenticate_wos`, `search_wos`, etc.) will appear in the tools list.

> **Tip — scoping:** `claude mcp add` defaults to project scope (this vault
> only). To make the server available in all projects, add the `-s user` flag:
> ```bash
> claude mcp add -s user web-of-science -- python MCPs/wos-mcp/server.py
> ```

> **If using a virtual environment**, replace `python` with the full path:
> ```bash
> claude mcp add web-of-science -- C:/Users/rh2310/.../wos-mcp/.venv/Scripts/python.exe MCPs/wos-mcp/server.py
> ```

> **Important — `authenticate_wos` in Claude Code:** The authentication tool
> opens a *visible* Chromium window for SSO login. This works normally — the
> browser window will appear on your desktop even though Claude Code runs in a
> terminal. Complete the login as usual.

### Step 5 — Authenticate (one-time)

In Claude, run:

```
Use the authenticate_wos tool
```

A Chromium window will open and navigate to Web of Science. Log in using your
Imperial College credentials (you may be redirected through Shibboleth/SSO).
Once you see the WoS search page, the tool detects success automatically and
closes the browser. **Your session is saved to `browser-session/`** and reused
for all future headless searches.

---

## Usage from the Claudian Obsidian plugin

This server is configured with **context-saving mode** (`contextSaving: true` in `.claude/mcp.json`), which means it is only activated when you explicitly mention it in your message. This keeps the WoS tools out of conversations where they are not needed, saving context tokens.

**To activate the WoS tools, include `@web-of-science` anywhere in your message:**

```
search for enzyme-constrained FBA papers @web-of-science
find recent literature on dynamic FBA @web-of-science
```

Claudian detects the `@web-of-science` mention and injects the WoS MCP tools for that message and the rest of the conversation. You do not need to mention it again in follow-up messages within the same chat.

If you forget the mention, Claude will remind you automatically (the search skill includes a pre-flight check).

---

## Usage examples

After authenticating, you can ask Claude things like:

> "Search Web of Science for papers on enzyme-constrained FBA published after 2018, sorted by citations. @web-of-science"

> "Find the full record for WOS:000612345678901 @web-of-science"

> "Download the paper with DOI 10.1038/s41586-021-03819-2 and save it to raw/FBA/FBA and enzymes/"

> "Save these search results to the wiki."

---

## Session management

| Situation | Action |
|-----------|--------|
| First-time use | Run `authenticate_wos` |
| `search_wos` returns "🔐 Not logged in" | Run `authenticate_wos` again |
| Session expires (typically days–weeks) | Run `authenticate_wos` again |
| Switch to a different university account | Delete `browser-session/` folder, then run `authenticate_wos` |

---

## Folder structure

```
wos-mcp/
├── server.py            ← MCP server (main code)
├── SKILL.md             ← Skill instructions for Claude
├── config.json          ← Optional: Unpaywall email + curated folder path
├── requirements.txt     ← Python dependencies (mcp, httpx, playwright)
├── README.md            ← This file
├── browser-session/     ← Saved Chromium session (auto-created; keep private)
└── curated/             ← Default folder for downloaded PDFs (auto-created)
```

---

## Privacy & security

- `browser-session/` contains your browser cookies — **do not commit it to
  version control**. Add it to `.gitignore`.
- The server only makes outbound connections to `www.webofscience.com` and
  `api.unpaywall.org`.
- No credentials are stored in plain text; authentication uses your browser's
  normal SSO cookie flow.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `"🔐 Not logged in"` | Run `authenticate_wos` |
| Browser opens but login times out | Log in faster (3-minute window) |
| `ModuleNotFoundError: playwright` | `pip install playwright && playwright install chromium` |
| `No records extracted` | WoS page layout may have changed; open `authenticate_wos` in visible mode to inspect |
| Server not appearing in **Claude Desktop** | Restart Claude Desktop; double-check the path in `claude_desktop_config.json` |
| Server not appearing in **Claude Code** | Run `claude mcp list` to check registration. If missing, run `claude mcp add web-of-science -- python MCPs/wos-mcp/server.py` from the vault root, then restart the session |
| `authenticate_wos` tool not found | The MCP server is not registered in your current Claude environment — see Step 4 above |
| Very slow search (>30 s) | WoS is loading slowly; the 35-second timeout should catch it |
