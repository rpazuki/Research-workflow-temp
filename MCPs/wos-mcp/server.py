#!/usr/bin/env python3
"""
Web of Science MCP Server — Browser Automation Edition
=======================================================
Accesses Web of Science Smart Search via Playwright browser automation,
using your institutional SSO session. No Clarivate developer API key needed.

Quick start
-----------
1.  pip install -r requirements.txt
2.  playwright install chromium
3.  Register this server in claude_desktop_config.json (see README.md)
4.  In Claude, call the `authenticate_wos` tool and log in via your university SSO.
5.  After that, `search_wos` runs headlessly using the saved session.

Author: Generated for Roozbeh Pazuki, Imperial College London
"""

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Paths & configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config.json"
CURATED_DIR  = Path(__file__).parent / "curated"
SESSION_DIR  = Path(__file__).parent / "browser-session"
VAULT_ROOT   = Path(__file__).parent.parent.parent          # Research_vault/
SEARCHES_DIR = VAULT_ROOT / "wiki" / "searches"

for d in (CURATED_DIR, SESSION_DIR, SEARCHES_DIR):
    d.mkdir(parents=True, exist_ok=True)

WOS_ADVANCED = "https://www.webofscience.com/wos/woscc/advanced-search"
WOS_BASIC    = "https://www.webofscience.com/wos/woscc/basic-search"


def load_config() -> dict:
    """Load config from config.json, falling back to environment variables."""
    config = {
        "unpaywall_email": os.environ.get("UNPAYWALL_EMAIL", ""),
        "curated_folder":  str(CURATED_DIR),
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                file_config = json.load(f)
            config.update({
                k: v for k, v in file_config.items()
                if v and not k.startswith("_")
            })
        except (json.JSONDecodeError, OSError):
            pass
    return config


CONFIG = load_config()

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Web of Science",
    instructions=(
        "Accesses Web of Science Core Collection via Playwright browser automation "
        "(institutional SSO — no API key required). "
        "Run authenticate_wos once to save your session. "
        "Then use: search_wos · get_record · download_paper · "
        "save_search_to_wiki · list_curated."
    ),
)

# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

LOGIN_INDICATORS = [
    "login", "shibboleth", "idp.", "signin", "sign-in",
    "auth", "cas/login", "wayf", "federation", "saml",
]


def _is_login_page(url: str) -> bool:
    """Return True if the URL looks like an SSO / login redirect."""
    low = url.lower()
    if "webofscience.com/wos" not in low:
        return True
    return any(ind in low for ind in LOGIN_INDICATORS)


async def _launch(headless: bool = True):
    """
    Start Playwright and open a persistent Chromium context.

    The persistent context stores cookies/local-storage in SESSION_DIR so the
    user's WoS session survives across MCP tool calls.

    Returns (playwright_instance, context).
    Remember to call context.close() and pw.stop() when done.
    """
    from playwright.async_api import async_playwright
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 900},
        locale="en-GB",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    return pw, ctx


async def _get_page(ctx):
    """Return the first open page in a context, or open a new one."""
    return ctx.pages[0] if ctx.pages else await ctx.new_page()


async def _dismiss_consent_overlay(page) -> None:
    """
    Dismiss the OneTrust / cookie-consent modal that WoS sometimes shows.

    The overlay sets pointer-events on a dark filter div that intercepts all
    clicks.  We try three strategies in order:
      1. Click an "Accept All" / "Reject All" / "Close" button.
      2. Remove the overlay elements from the DOM via JavaScript.
      3. Force pointer-events: none on the filter div so clicks pass through.
    """
    try:
        # Strategy 1 — click the consent button if visible
        consent_btn = (
            "#onetrust-accept-btn-handler, "
            "#onetrust-reject-all-handler, "
            ".onetrust-close-btn-handler, "
            "button.ot-pc-refuse-all-handler, "
            "button:has-text('Accept All'), "
            "button:has-text('Reject All'), "
            "button:has-text('Accept Cookies')"
        )
        btn = await page.query_selector(consent_btn)
        if btn:
            await btn.click(timeout=5_000)
            await page.wait_for_timeout(800)
            return
    except Exception:
        pass

    try:
        # Strategy 2 — remove the SDK container from the DOM
        await page.evaluate(
            """() => {
                const sdk = document.getElementById('onetrust-consent-sdk');
                if (sdk) sdk.remove();
                const filter = document.querySelector('.onetrust-pc-dark-filter');
                if (filter) filter.remove();
            }"""
        )
        await page.wait_for_timeout(300)
    except Exception:
        pass

    try:
        # Strategy 3 — neutralise pointer-event interception in-place
        await page.evaluate(
            """() => {
                document.querySelectorAll(
                    '#onetrust-consent-sdk, .onetrust-pc-dark-filter, '
                    + '[class*="onetrust"], [id*="onetrust"]'
                ).forEach(el => {
                    el.style.pointerEvents = 'none';
                    el.style.display = 'none';
                });
            }"""
        )
        await page.wait_for_timeout(300)
    except Exception:
        pass


async def _goto_wos(page) -> bool:
    """
    Navigate to the WoS Advanced Search page.
    Return True if we land on WoS (advanced-search), False if we hit a login screen.

    The WoS Angular SPA sometimes redirects from /advanced-search to
    /search-history immediately after load. We detect this and recover by
    clicking the "Advanced Search" nav link or re-navigating.
    """
    await page.goto(WOS_ADVANCED, wait_until="domcontentloaded", timeout=40_000)
    # Give the Angular router time to settle (it often fires an internal redirect)
    await page.wait_for_timeout(4_000)
    await _dismiss_consent_overlay(page)

    if _is_login_page(page.url):
        return False

    # If the SPA redirected us away from advanced-search, recover
    for _attempt in range(2):
        if "advanced-search" in page.url:
            break
        # Try clicking the "Advanced Search" link in the top navigation
        adv_link = await page.query_selector(
            "a[href*='advanced-search'], "
            "a:has-text('Advanced Search'), "
            "span:has-text('Advanced Search')"
        )
        if adv_link:
            await adv_link.click()
            await page.wait_for_timeout(3_500)
        else:
            # Fall back to direct navigation
            await page.goto(WOS_ADVANCED, wait_until="domcontentloaded", timeout=40_000)
            await page.wait_for_timeout(4_000)
        await _dismiss_consent_overlay(page)

    return not _is_login_page(page.url)


# ---------------------------------------------------------------------------
# Tool 0: authenticate_wos
# ---------------------------------------------------------------------------

@mcp.tool()
async def authenticate_wos() -> str:
    """
    Open a visible browser so you can log in to Web of Science via your
    institutional SSO (e.g. Imperial College London single sign-on).

    Run this tool ONCE before using search_wos for the first time,
    or any time your session has expired.

    What happens:
        1. A Chromium window opens and navigates to Web of Science.
        2. Complete your university SSO / Shibboleth login.
        3. Once you see the WoS search page, wait — the tool detects the
           successful login automatically (up to 3 minutes).
        4. The browser closes and saves your session to disk.

    After this you can use search_wos in headless mode indefinitely
    (sessions typically last several days to weeks).
    """
    try:
        pw, ctx = await _launch(headless=False)
        page = await _get_page(ctx)
        await page.goto(WOS_ADVANCED, wait_until="domcontentloaded", timeout=40_000)

        # Poll until we land on a genuine WoS page (max 3 min)
        max_wait_s = 180
        poll_ms    = 2_000
        elapsed    = 0
        success    = False

        while elapsed < max_wait_s * 1000:
            await page.wait_for_timeout(poll_ms)
            elapsed += poll_ms
            if not _is_login_page(page.url):
                success = True
                break

        await ctx.close()
        await pw.stop()

        if success:
            return (
                "✅ **Authentication successful!**\n\n"
                f"Session saved to: `{SESSION_DIR}`\n\n"
                "You can now use `search_wos` without logging in again. "
                "Run `authenticate_wos` again if you ever see a 'session expired' error."
            )
        return (
            "⚠️ **Timed out waiting for login** (3 minutes elapsed).\n\n"
            "Please run `authenticate_wos` again and complete the SSO login "
            "within the 3-minute window."
        )

    except Exception as exc:
        return f"❌ **Browser error during authentication:** {exc}"


# ---------------------------------------------------------------------------
# Tool 1: search_wos  (Playwright edition)
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_wos(
    query: str,
    max_results: int = 10,
    sort_field: str = "RS",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    doc_type: Optional[str] = None,
) -> str:
    """
    Search the Web of Science Core Collection using Smart Search / Advanced Search
    syntax, driven by your saved browser session.

    Run authenticate_wos once before the first search.

    Args:
        query: Search query. Supports WoS field tags:
               TS=topic  TI=title  AU=author  SO=journal  DO=DOI
               Plain text is wrapped as a TS= topic search automatically.
               Boolean operators: AND  OR  NOT
               Example: "TS=flux balance analysis AND TS=machine learning"
        max_results: Number of results to retrieve (1–50, default 10).
        sort_field:  "RS" = relevance (default) | "TC" = times cited | "PY" = pub year.
        year_from:   Earliest publication year filter.
        year_to:     Latest publication year filter.
        doc_type:    Optional document type filter ("Article", "Review", etc.).

    Returns:
        Formatted list of matching papers with titles, authors, journals,
        DOIs, abstracts, and citation counts.
    """
    # --- Normalise query ---
    if not re.search(r'\b[A-Z]{2,3}=', query):
        query = f"TS={query}"
    if year_from or year_to:
        y0 = year_from or 1900
        y1 = year_to   or 2099
        query = f"({query}) AND PY={y0}-{y1}"
    if doc_type:
        query = f"({query}) AND DT={doc_type}"

    max_results = min(max(1, max_results), 50)

    try:
        pw, ctx = await _launch(headless=True)
        page = await _get_page(ctx)

        # Check session
        if not await _goto_wos(page):
            await ctx.close()
            await pw.stop()
            return (
                "🔐 **Not logged in to Web of Science.**\n\n"
                "Run `authenticate_wos` to log in via your institutional SSO, "
                "then retry your search."
            )

        # ---- Verify we landed on the Advanced Search page ----
        # WoS SPA may have redirected; if so, bail with a clear message.
        if "advanced-search" not in page.url:
            current = page.url
            await ctx.close()
            await pw.stop()
            return (
                "❌ Could not navigate to the WoS Advanced Search page.\n"
                f"Current URL: {current}\n"
                "Run `authenticate_wos` to refresh your session, then retry."
            )

        # ---- Fill in the Advanced Search textarea ----
        # Try specific selectors first; avoid bare 'textarea' which can match
        # unrelated fields on other WoS pages (e.g. search-history).
        textarea_sel = (
            "#advancedSearchInputArea, "
            "textarea[class*='advanced-search'], "
            "textarea[aria-label*='query' i], "
            "textarea[placeholder*='enter' i], "
            "textarea[placeholder*='search' i], "
            "app-advanced-search textarea, "
            "[class*='advanced-search'] textarea"
        )
        try:
            await page.wait_for_selector(textarea_sel, timeout=15_000)
        except Exception:
            await ctx.close()
            await pw.stop()
            return (
                "❌ Could not find the WoS Advanced Search input.\n"
                "The WoS page layout may have changed, or your session may have expired.\n"
                "Run `authenticate_wos` to refresh, then retry."
            )

        textarea = await page.query_selector(textarea_sel)
        if not textarea:
            await ctx.close()
            await pw.stop()
            return "❌ Search textarea not found. Run `authenticate_wos` to refresh your session."

        await textarea.fill(query)
        await page.wait_for_timeout(500)

        # Dismiss any consent overlay that may have appeared after page load
        await _dismiss_consent_overlay(page)

        # ---- Submit the search ----
        # The WoS post-2024 Angular redesign uses data-ta="run-search" on the
        # submit button.  "button:has-text('Search')" must NOT be used as the
        # first selector because "View your search history" appears earlier in
        # the DOM and its text contains "search" (Playwright has-text is
        # case-insensitive), causing navigation to the history page instead.
        btn_sel = (
            "button[data-ta='run-search'], "
            "button[data-ta='advanced-search-button'], "
            "button[data-ta='search-button'], "
            "app-advanced-search button[type='submit'], "
            "app-advanced-search button.mat-flat-button"
        )
        search_btn = await page.query_selector(btn_sel)
        if search_btn:
            # Use JS .click() to bypass CSS pointer-events interception from overlays
            await page.evaluate("btn => btn.click()", search_btn)
        else:
            # Fall back: press Enter in the textarea to submit
            await textarea.press("Enter")

        # ---- Wait for the SPA to navigate away from advanced-search ----
        # After submission WoS routes to /search-results, /basic-search, or
        # similar — anything that is NOT the advanced-search form page.
        # We wait up to 15 s for the URL to change, then wait for results.
        try:
            await page.wait_for_function(
                "() => !window.location.href.includes('advanced-search')",
                timeout=15_000,
            )
        except Exception:
            pass  # URL may not change on some WoS layouts; proceed to results wait

        # If we ended up on search-history (WoS SPA quirk), click the first
        # search-history entry to navigate to the actual results page.
        if "search-history" in page.url:
            history_link = await page.query_selector(
                "a[href*='search-results'], "
                "[data-ta='search-history-query-link'], "
                ".search-history-query a, "
                "app-search-history a"
            )
            if history_link:
                await history_link.click()
                await page.wait_for_timeout(3_000)

        # ---- Wait for results ----
        results_sel = (
            "app-full-record-cover, "
            "app-record, "
            "[data-ta='record'], "
            ".summary-record, "
            ".record-set-list-item, "
            # Additional modern WoS selectors (post-2024 redesign)
            "app-summary-record, "
            "app-records-list, "
            "[class*='summary-record'], "
            "[class*='record-component'], "
            "[data-record-id], "
            "[id*='recordId'], "
            ".record"
        )
        try:
            await page.wait_for_selector(results_sel, timeout=60_000)
        except Exception:
            # Could be zero results or page change — dump body for debugging
            body = await page.text_content("body") or ""
            body_low = body.lower()
            if "no results" in body_low or "0 results" in body_low or "found 0" in body_low:
                await ctx.close()
                await pw.stop()
                return (
                    f"## Web of Science Search Results\n"
                    f"**Query:** `{query}`\n\n"
                    "No records found. Try broadening your query or removing filters."
                )
            # Return a snippet of the page body to help diagnose selector issues
            snippet = body[:1500].replace("\n", " ").strip()
            current_url = page.url
            await ctx.close()
            await pw.stop()
            return (
                "⚠️ Results did not load within 60 seconds.\n"
                "WoS may be slow, your session may have expired, or the page layout changed.\n"
                f"**Current URL:** {current_url}\n"
                f"**Page body snippet (first 1500 chars):** {snippet}\n\n"
                "Run `authenticate_wos` to refresh your session and try again."
            )

        await page.wait_for_timeout(2_000)  # let Angular finish rendering

        # ---- Extract total result count ----
        total = 0
        for cnt_sel in [
            "[data-ta='results-count']",
            ".results-count",
            "span.brand-blue",
            "app-page-controls",
        ]:
            el = await page.query_selector(cnt_sel)
            if el:
                txt = (await el.text_content() or "").replace(",", "")
                m = re.search(r'(\d+)', txt)
                if m:
                    total = int(m.group(1))
                    break

        # ---- Extract records via JavaScript ----
        records = await page.evaluate(
            """(maxN) => {
                const pick = (el, ...sels) => {
                    for (const s of sels) {
                        const found = el.querySelector(s);
                        if (found) return found;
                    }
                    return null;
                };
                const pickAll = (el, ...sels) => {
                    for (const s of sels) {
                        const found = el.querySelectorAll(s);
                        if (found.length) return Array.from(found);
                    }
                    return [];
                };
                const txt = el => el ? el.textContent.trim() : '';

                const containers = document.querySelectorAll(
                    'app-full-record-cover, app-record, app-summary-record, ' +
                    '[data-ta="record"], .summary-record, .record-set-list-item, ' +
                    '[class*="summary-record"], [data-record-id], [id*="recordId"], ' +
                    'app-records-list > *, [class*="record-component"]'
                );

                const items = [];
                for (let i = 0; i < Math.min(containers.length, maxN); i++) {
                    const c = containers[i];

                    // Title + WoS URL
                    const titleEl = pick(c,
                        '[data-ta="summary-record-title-link"]',
                        '[data-ta="record-title-link"]',
                        'a.title', 'h3 a', '.record-title a',
                        'a[href*="full-record"]'
                    );
                    const title  = txt(titleEl);
                    const wosUrl = titleEl ? (titleEl.href || '') : '';

                    // WoS UID from link
                    const uidM = wosUrl.match(/WOS:[A-Z0-9]+/);
                    const uid  = uidM ? uidM[0] : '';

                    // Authors
                    const authorEls = pickAll(c,
                        '[data-ta="author-name"]', '.author-link',
                        '.name-link', '.authors a', 'a[class*="author"]'
                    );
                    const authors = authorEls.map(a => txt(a)).filter(Boolean);

                    // Journal / source
                    const srcEl = pick(c,
                        '[data-ta="source-title-link"]', '[data-ta="source-title"]',
                        '.source-title a', '.journal-title', '.source a'
                    );
                    const journal = txt(srcEl);

                    // Year
                    const yrEl = pick(c, '.pub-year', '[data-ta="pub-year"]', '.pubyear');
                    let year = txt(yrEl);
                    if (!year) {
                        const srcTxt = txt(pick(c, '.source', '.pub-info', '.metadata'));
                        const yrM = srcTxt.match(/\\b(19|20)\\d{2}\\b/);
                        if (yrM) year = yrM[0];
                    }

                    // DOI
                    let doi = '';
                    const doiEl = pick(c,
                        '[data-ta="doi"]', 'a[href*="doi.org"]',
                        '[class*="doi"]', 'a[href*="dx.doi"]'
                    );
                    if (doiEl) {
                        const raw = (doiEl.href || '') + ' ' + txt(doiEl);
                        const dm = raw.match(/10\\.\\d{4,}[/\\\\][^\\s"<>]+/);
                        if (dm) doi = dm[0].replace(/[.,;]+$/, '');
                    }

                    // Citation count
                    const citeEl = pick(c,
                        '[data-ta="citing-articles-count"]',
                        '[data-ta="times-cited"]',
                        '.times-cited-count', '[class*="times-cited"]',
                        '[class*="cite-count"]'
                    );
                    const citationCount = citeEl
                        ? (parseInt(txt(citeEl).replace(/[^0-9]/g, '')) || 0)
                        : 0;

                    // Abstract (often hidden in list view)
                    const absEl = pick(c,
                        '.abstract-text', '[data-ta="abstract"]',
                        '[class*="abstract"]', 'p.abstract'
                    );
                    const abstract = txt(absEl).slice(0, 600);

                    items.push({
                        title, authors, journal, year,
                        doi, citationCount, abstract,
                        uid, wosUrl
                    });
                }
                return items;
            }""",
            max_results,
        )

        await ctx.close()
        await pw.stop()

        if not records:
            return (
                f"## Web of Science Search Results\n"
                f"**Query:** `{query}`\n\n"
                "No records were extracted. The page may have loaded but the selectors "
                "did not match the current WoS layout. Try running `authenticate_wos` to "
                "open the browser visibly and check the page."
            )

        # ---- Format output ----
        lines = [
            "## Web of Science Search Results",
            f"**Query:** `{query}`",
            f"**Showing:** {len(records)} of {total or '?'} total results",
            "",
        ]
        for i, r in enumerate(records, 1):
            authors = r.get("authors", [])
            auth_str = "; ".join(authors[:5])
            if len(authors) > 5:
                auth_str += f" et al. (+{len(authors)-5} more)"
            doi  = r.get("doi", "")
            uid  = r.get("uid", "")
            cite = r.get("citationCount", 0)

            lines += [
                f"### {i}. {r.get('title') or '(no title)'}",
                f"**Authors:** {auth_str or 'N/A'}",
                f"**Source:** {r.get('journal', 'N/A')} ({r.get('year', '?')})",
                f"**UID:** `{uid}`"
                + (f" | **DOI:** `{doi}`" if doi else "")
                + (f" | **Cited:** {cite}"  if cite else ""),
            ]
            if r.get("abstract"):
                ab = r["abstract"]
                if len(ab) > 500:
                    ab = ab[:500] + "…"
                lines.append(f"**Abstract:** {ab}")
            if r.get("wosUrl"):
                lines.append(f"**WoS Link:** {r['wosUrl']}")
            lines.append("")

        return "\n".join(lines)

    except Exception as exc:
        return (
            f"❌ **Browser automation error in search_wos:** {exc}\n\n"
            "Run `authenticate_wos` to refresh your session and try again."
        )


# ---------------------------------------------------------------------------
# Tool 2: get_record  (Playwright edition)
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_record(record_id: str) -> str:
    """
    Fetch full metadata for a specific Web of Science record.

    Args:
        record_id: The WoS UID from search_wos results (e.g. "WOS:000123456789012"),
                   or a DOI (e.g. "10.1038/s41586-021-03819-2").

    Returns:
        Full record: title, all authors, journal, year, DOI, abstract,
        keywords, citation count, and direct WoS link.
    """
    if record_id.startswith("10."):
        return await search_wos(query=f"DO={record_id}", max_results=1)

    url = f"https://www.webofscience.com/wos/woscc/full-record/{record_id}"

    try:
        pw, ctx = await _launch(headless=True)
        page = await _get_page(ctx)

        if not await _goto_wos(page):
            await ctx.close()
            await pw.stop()
            return "🔐 Not logged in. Run `authenticate_wos` first."

        await page.goto(url, wait_until="domcontentloaded", timeout=40_000)
        await page.wait_for_timeout(2_500)

        if _is_login_page(page.url):
            await ctx.close()
            await pw.stop()
            return "🔐 Session expired. Run `authenticate_wos` to log in again."

        data = await page.evaluate("""
            () => {
                const q  = s => document.querySelector(s)?.textContent.trim() || '';
                const qa = s => Array.from(document.querySelectorAll(s))
                                     .map(e => e.textContent.trim())
                                     .filter(Boolean);

                // Title
                const title = q('[data-ta="record-title"], h2.title, .title-card h2, h1.title');

                // Authors
                const authors = qa(
                    '[data-ta="author-name"], .author-link, .name-link, ' +
                    'a[href*="author"], .author span'
                );

                // Journal
                const journal = q(
                    '[data-ta="source-title"], .journal-title, .source-title, ' +
                    '[class*="source"] a'
                );

                // Year
                let year = q('.pub-year, [data-ta="pub-year"]');
                if (!year) {
                    const m = document.body.textContent.match(/Published[^:]*:\\s*(\\d{4})/);
                    if (m) year = m[1];
                }

                // Abstract
                const abstract = q(
                    '.abstract-text, [data-ta="abstract"] p, .abstract, ' +
                    '[class*="abstract"] p'
                );

                // Keywords
                const keywords = qa(
                    '[data-ta="keyword"], .keyword-link, .author-keyword, ' +
                    '[class*="keyword"] a'
                );

                // DOI
                const doiEl = document.querySelector(
                    '[data-ta="doi"] a, a[href*="doi.org"], [class*="doi"] a'
                );
                let doi = '';
                if (doiEl) {
                    const raw = (doiEl.href || '') + ' ' + (doiEl.textContent || '');
                    const m = raw.match(/10\\.\\d{4,}[/\\\\][^\\s"<>]+/);
                    if (m) doi = m[0].replace(/[.,;]+$/, '');
                }

                // Citation count
                const citations = q(
                    '[data-ta="citing-articles-count"], [data-ta="times-cited"], ' +
                    '.times-cited-count, [class*="times-cited"]'
                ) || '0';

                // UID from URL
                const uid = window.location.href.match(/WOS:[A-Z0-9]+/)?.[0] || '';

                return { title, authors, journal, year, abstract, keywords, doi, citations, uid };
            }
        """)

        await ctx.close()
        await pw.stop()

        lines = [
            f"# {data.get('title') or '(no title)'}",
            "",
            f"**Authors:** {'; '.join(data.get('authors', [])) or 'N/A'}",
            f"**Journal:** {data.get('journal', 'N/A')}",
            f"**Year:** {data.get('year', 'N/A')}",
            (f"**DOI:** `{data['doi']}`" if data.get('doi') else "**DOI:** N/A"),
            f"**Times Cited:** {data.get('citations', '0')}",
            f"**WoS UID:** `{data.get('uid') or record_id}`",
            f"**WoS Link:** {url}",
            "",
            "## Abstract",
            data.get("abstract") or "No abstract available.",
            "",
            "## Keywords",
            ", ".join(data.get("keywords", [])) or "None listed.",
        ]
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ **Error fetching record {record_id}:** {exc}"


# ---------------------------------------------------------------------------
# Tool 3: download_paper
# ---------------------------------------------------------------------------

@mcp.tool()
async def download_paper(
    doi: Optional[str] = None,
    url: Optional[str] = None,
    filename: Optional[str] = None,
    destination_folder: Optional[str] = None,
) -> str:
    """
    Download a paper PDF to a local folder.

    Uses Unpaywall to locate a legal open-access PDF. If the paper is
    paywalled, returns the publisher URL and instructions for manual download
    via your institutional access.

    Args:
        doi: DOI of the paper (e.g. "10.1038/s41586-021-03819-2").
             Preferred over url when available.
        url: Direct URL to a PDF. Used if no DOI given, or as fallback.
        filename: Optional custom filename (without .pdf extension).
                  Defaults to a sanitised form of the DOI.
        destination_folder: Where to save the PDF.
            • Omit → saves to the curated/ folder next to this server.
            • Relative path → resolved from vault root
              (e.g. "raw/FBA/FBA and AI" saves to Research_vault/raw/FBA/FBA and AI/).
            • Absolute path → used as-is.

    Returns:
        Success: local file path and paper metadata.
        Not open-access: publisher URL for manual download.
        Error: description of what went wrong.
    """
    if not doi and not url:
        return "❌ Please provide at least a DOI or a direct URL."

    email   = CONFIG.get("unpaywall_email", "")
    pdf_url: Optional[str] = None
    paper_title: str = ""
    paper_doi:   str = doi or ""

    # ---- Resolve destination folder ----
    if destination_folder:
        dest_path = Path(destination_folder)
        if not dest_path.is_absolute():
            dest_path = VAULT_ROOT / dest_path
        save_dir = dest_path
    else:
        save_dir = Path(CONFIG.get("curated_folder", str(CURATED_DIR)))
    save_dir.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: Check Unpaywall for open-access PDF ----
    if doi:
        clean_doi = doi.strip().lstrip("https://doi.org/").lstrip("doi:")
        paper_doi = clean_doi
        oa_email  = email or "anonymous@example.com"
        unpaywall = f"https://api.unpaywall.org/v2/{clean_doi}?email={oa_email}"

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                resp = await client.get(unpaywall)
                if resp.status_code == 200:
                    oa = resp.json()
                    paper_title = oa.get("title", "")
                    if oa.get("is_oa") and oa.get("best_oa_location"):
                        best = oa["best_oa_location"]
                        pdf_url = best.get("url_for_pdf") or best.get("url")
                    elif not oa.get("is_oa"):
                        pub_url = oa.get("doi_url", f"https://doi.org/{clean_doi}")
                        return (
                            "## Paper Not Openly Available\n\n"
                            f"**Title:** {paper_title or '(unknown)'}\n"
                            f"**DOI:** `{clean_doi}`\n\n"
                            "This paper is **not open access** and cannot be downloaded "
                            "automatically.\n\n"
                            "**Download manually** through your institutional access:\n"
                            f"{pub_url}\n\n"
                            "If you are off-campus, use the "
                            "[Imperial College VPN / Library Off-Campus Access]"
                            "(https://www.imperial.ac.uk/admin-services/library/learning-support/"
                            "reference-management/library-access-using-a-vpn/)."
                        )
        except httpx.RequestError:
            pass  # Fall through to direct URL

    # ---- Step 2: Use provided URL if no OA PDF found ----
    if not pdf_url and url:
        pdf_url = url

    if not pdf_url:
        return (
            f"❌ Could not locate a downloadable PDF for DOI `{paper_doi}`. "
            "The paper may not be open access. Provide a direct URL as a fallback."
        )

    # ---- Step 3: Build filename ----
    if not filename:
        if paper_doi:
            filename = re.sub(r'[^\w\-.]', '_', paper_doi)
        else:
            filename = "paper_" + re.sub(r'[^\w]', '_', pdf_url.split("/")[-1])[:40]
    dest = save_dir / f"{filename}.pdf"

    if dest.exists():
        return (
            f"✅ **Already downloaded:** `{dest.name}`\n"
            f"**Location:** `{dest}`\n"
            f"**Title:** {paper_title or '(unknown)'}"
        )

    # ---- Step 4: Download ----
    try:
        async with httpx.AsyncClient(
            timeout=120,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (academic research; "
                    f"mailto:{email or 'r.pazuki@imperial.ac.uk'})"
                )
            },
        ) as client:
            resp = await client.get(pdf_url)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            if "pdf" not in ct and "octet-stream" not in ct:
                return (
                    f"⚠️ **Could not download PDF directly** — server returned `{ct}`.\n\n"
                    "This may be a paywall redirect. Download manually:\n"
                    f"{pdf_url}\n\n"
                    f"**DOI:** `{paper_doi}`"
                )
            dest.write_bytes(resp.content)
    except httpx.HTTPStatusError as exc:
        return f"❌ Download failed (HTTP {exc.response.status_code}): {pdf_url}"
    except httpx.RequestError as exc:
        return f"❌ Network error during download: {exc}"

    size_kb = dest.stat().st_size // 1024
    return (
        "✅ **Downloaded successfully!**\n\n"
        f"**Title:** {paper_title or '(see file)'}\n"
        f"**DOI:** `{paper_doi}`\n"
        f"**File:** `{dest.name}` ({size_kb} KB)\n"
        f"**Saved to:** `{dest}`\n"
        f"**Source:** {pdf_url}"
    )


# ---------------------------------------------------------------------------
# Helper: slugify
# ---------------------------------------------------------------------------

def _slugify(text: str, max_len: int = 60) -> str:
    """Convert a string to a lowercase hyphenated slug."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s\-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:max_len].rstrip('-')


# ---------------------------------------------------------------------------
# Tool 4: save_search_to_wiki
# ---------------------------------------------------------------------------

@mcp.tool()
async def save_search_to_wiki(
    query: str,
    results_json: str,
    total_results: int = 0,
    notes: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Persist a Web of Science search session as a structured Markdown page in
    wiki/searches/.

    Call this immediately after search_wos to save the results to the wiki.
    The file is written to:
        <vault_root>/wiki/searches/search-<slug>-<YYYYMMDD>.md

    Args:
        query: The original query string passed to search_wos.
        results_json: JSON string — a list of record dicts from search_wos.
                      If you only have the formatted text output, pass that;
                      it will be stored verbatim under Results.
        total_results: Total records found in WoS (from the "N of M" line).
        notes: Optional observations or context to include on the page.
        tags: Optional comma-separated lowercase tags for frontmatter
              (e.g. "enzyme-constrained, ecgem, yeast"). Spaces around commas
              are stripped automatically.

    Returns:
        Path to the created wiki search page, plus next-step reminders.
    """
    today         = date.today().isoformat()
    today_compact = today.replace("-", "")
    slug          = _slugify(query)
    filename      = f"search-{slug}-{today_compact}.md"
    dest          = SEARCHES_DIR / filename

    # Parse results
    records: list[dict] = []
    raw_text = ""
    try:
        parsed = json.loads(results_json)
        if isinstance(parsed, list):
            records = parsed
    except (json.JSONDecodeError, TypeError):
        raw_text = str(results_json)

    returned = len(records)

    # Build tag list
    tag_list = ["search", "wos"]
    if tags:
        for t in tags.split(","):
            t = t.strip().lower()
            if t and t not in tag_list:
                tag_list.append(t)
    tags_yaml = "[" + ", ".join(tag_list) + "]"

    # ---- Frontmatter ----
    lines = [
        "---",
        f'title: "Search: {query}"',
        "type: search",
        f"tags: {tags_yaml}",
        f'query: "{query}"',
        f"date: {today}",
        f"total_results: {total_results}",
        f"returned_results: {returned}",
        "---",
        "",
        f"# Search: {query}",
        "",
        "## Query",
        "",
        f"- **Query:** `{query}`",
        f"- **Date:** {today}",
        f"- **Database:** Web of Science Core Collection",
        f"- **Total records in WoS:** {total_results}",
        f"- **Records saved here:** {returned}",
        "",
    ]

    # ---- Results ----
    lines.append("## Results")
    lines.append("")
    if records:
        for i, r in enumerate(records, 1):
            authors = r.get("authors", [])
            auth_str = "; ".join(authors[:5]) + (" et al." if len(authors) > 5 else "")
            doi  = r.get("doi", "")
            uid  = r.get("uid", "")
            cite = r.get("citationCount", r.get("citation_count", ""))
            wos_url = r.get("wosUrl", r.get("wos_url", ""))
            lines += [
                f"### {i}. {r.get('title', '(no title)')}",
                "",
                f"- **Authors:** {auth_str or 'N/A'}",
                f"- **Journal:** {r.get('journal', 'N/A')} ({r.get('year', '?')})",
            ]
            if doi:
                lines.append(f"- **DOI:** `{doi}` — [https://doi.org/{doi}](https://doi.org/{doi})")
            if uid:
                wlink = wos_url or f"https://www.webofscience.com/wos/woscc/full-record/{uid}"
                lines.append(f"- **WoS UID:** `{uid}` — [{wlink}]({wlink})")
            if cite:
                lines.append(f"- **Times cited:** {cite}")
            if r.get("abstract"):
                lines.append(f"- **Abstract:** {r['abstract']}")
            lines.append("")
    elif raw_text:
        lines.append(raw_text)
        lines.append("")
    else:
        lines.append("_No results recorded._")
        lines.append("")

    # ---- Downloaded ----
    lines += [
        "## Downloaded",
        "",
        "_No papers downloaded from this search yet._",
        "",
        "<!-- Add entries here as papers are downloaded, e.g.:            -->",
        "<!-- - `author-year-title.pdf` — saved to `raw/FBA/FBA and AI/` on YYYY-MM-DD -->",
        "",
    ]

    # ---- Connections ----
    lines += [
        "## Connections",
        "",
        "_Link to existing wiki pages relevant to these results. "
        "Mark papers as INGEST candidates._",
        "",
    ]

    # ---- Notes ----
    lines += [
        "## Notes",
        "",
        notes if notes else "_None._",
        "",
    ]

    dest.write_text("\n".join(lines), encoding="utf-8")
    rel = dest.relative_to(VAULT_ROOT)

    return (
        "✅ **Search saved to wiki.**\n\n"
        f"**File:** `{rel}`\n"
        f"**Query:** {query}\n"
        f"**Papers recorded:** {returned}\n\n"
        "Next steps:\n"
        f"1. Update `wiki/index.md` — add "
        f"`- [[{filename[:-3]}]] — {query} ({today})` under `## Searches`.\n"
        "2. Append a `search` entry to `wiki/log.md`.\n"
        "3. Use `download_paper` with `destination_folder='raw/<topic>/<subfolder>'` "
        "to save any papers to the raw folder."
    )


# ---------------------------------------------------------------------------
# Tool 5: list_curated
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_curated() -> str:
    """
    List all papers saved in the local curated folder.

    Returns a formatted list of downloaded PDF files with filenames and sizes.
    """
    curated = Path(CONFIG.get("curated_folder", str(CURATED_DIR)))
    pdfs    = sorted(curated.glob("*.pdf"))

    if not pdfs:
        return (
            "📂 The curated folder is empty.\n\n"
            "Use `download_paper` with a DOI or URL to save papers here.\n"
            f"**Folder:** `{curated}`"
        )

    total_kb = sum(p.stat().st_size for p in pdfs) // 1024
    lines = [
        f"## Curated Papers ({len(pdfs)} files, {total_kb} KB total)",
        f"**Folder:** `{curated}`",
        "",
    ]
    for i, p in enumerate(pdfs, 1):
        lines.append(f"{i}. `{p.name}` — {p.stat().st_size // 1024} KB")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
