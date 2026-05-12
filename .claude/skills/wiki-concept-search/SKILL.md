---
name: wiki-concept-search
description: >
  Exploratory concept search for vague or fuzzy research ideas where the exact
  field terminology is unknown. Runs a 2-phase workflow: first maps the
  conceptual landscape with preliminary web searches, then hands off to the
  full wiki-search skill with discovered terminology.
  Trigger on: "I'm not sure if anyone has done this", "something like X but
  also Y", "is there a method that...", "I don't know the exact term but...",
  "search for the idea of...", or any query where the user describes a concept
  without knowing its formal name.
---

# Wiki CONCEPT SEARCH Workflow (Exploratory 2-Phase)

Use this workflow when the **user's query is conceptually clear but terminologically fuzzy** — they describe what they want, but do not know what the field calls it, whether it exists as a named method, or how to phrase it for a database search.

**Worked example:** "flux balance variability that finds the probability of the flux ranges and/or pathway sampling that can find it by sampling — I'm not sure whether anyone has done it."
→ Preliminary phase discovers: the field is called *flux sampling*, two traditions exist (uniform MCMC and Bayesian), standard algorithms are CHRR / BaMFA / BayFlux.
→ Final phase runs [[wiki-search]] with those discovered terms.

---

## When to use this skill vs wiki-search

| Situation | Skill to use |
|-----------|-------------|
| User knows the topic name ("search for enzyme-constrained FBA") | [[wiki-search]] directly |
| User knows an author or paper ("find papers by Palsson on GEMs") | [[wiki-search]] directly |
| User describes a concept in their own words without a field name | **This skill** |
| User says "I'm not sure if this exists" | **This skill** |
| User uses hedging language: "something like", "maybe called" | **This skill** |
| Query spans multiple potential disciplines (concept might be named differently in each) | **This skill** |

---

## Phase 0 — Pre-flight: MCP availability

Same check as [[wiki-search]]:
- Confirm `search_wos` is available (requires `@web-of-science` in user message). If not, prompt the user to resend with `@web-of-science`.
- Note whether `mcp__claude_ai_bioRxiv__search_preprints` is available.

---

## Phase 1 — Concept Mapping (Preliminary Exploration)

**Goal:** Discover what the field calls this concept. Do NOT yet write a wiki page.

### Step 1 — Translate the user's description into search angles

Before searching, decompose the user's description into:
- **Core idea** — what is the computational/biological task being described?
- **Possible synonyms** — what else might this be called?
- **Adjacent methods** — what methods solve a related problem?
- **Disciplines** — could this be named differently in CS, biology, or mathematics?

Record this analysis explicitly (shown to user, not stored).

### Step 2 — Run 3–5 preliminary web searches

Use the user's own phrasing and paraphrases. Do NOT assume terminology. Examples:
- Query the concept with the user's exact words
- Query with each synonym hypothesis
- Query with "method for [the task described]"
- Query "probabilistic [thing]" or "stochastic [thing]"
- Query with the adjacent discipline's vocabulary

Run these searches **in parallel** when possible.

### Step 3 — Build a concept map

From the results, compile:

```
CONCEPT MAP
───────────────────────────────────────────────────────────
User description: "<exact user phrase>"

Formal name(s) discovered:     e.g. "flux sampling", "MCMC flux analysis"
Alternative names:              e.g. "uniform sampling", "Bayesian MFA"
Key methods/algorithms:         e.g. ACHR, CHRR, BaMFA, BayFlux
Foundational papers:            e.g. Price et al. 2004; Haraldsdottir et al. 2017
Active research groups:         e.g. Palsson lab, Vempala (CS theory)
Software tools:                 e.g. COBRA Toolbox, dingo, COBRApy
Time period of activity:        e.g. 2004–present (active)
Disciplines:                    e.g. systems biology, computational biology, convex geometry
───────────────────────────────────────────────────────────
```

### Step 4 — Show the concept map to the user

Present the map in a readable summary before proceeding. This serves two purposes:
1. **Confirmation**: the user can correct misidentifications before a full search is run
2. **Education**: the user learns the field vocabulary immediately

> **Concept map — confirm before proceeding?**
> I found that what you're describing is called *flux sampling* in the literature, ...
> Is this correct, or should I adjust the direction?

**Wait for confirmation if the concept seems non-obvious or if multiple very different fields emerged.** If the mapping is clear and unambiguous, proceed automatically (but note "proceeding automatically").

---

## Phase 2 — Targeted Search (Handoff to wiki-search)

Once the concept map is confirmed:

### Step 5 — Derive targeted search terms

From the concept map, derive:
- 2–4 WoS `TS=` queries using formal field names (not user paraphrase)
- The bioRxiv category best matching the field
- Key author names to watch for

Write these out explicitly so the search strategy is transparent.

### Step 6 — Execute full wiki-search

Invoke the complete [[wiki-search]] workflow (Phases 1–5) using the discovered terminology. The final search page should include:

**Additional section at the top of the search page** (before `## Query`):

```markdown
## Concept Discovery

**User description:** "<exact user phrase>"
**Preliminary searches run:** <N>
**Field name discovered:** <formal name(s)>
**Key terminology:** <comma-separated list of terms found in Phase 1>
**Concept map note:** <1–2 sentences summarising the Phase 1 finding>
```

This section documents the provenance of the search — making it clear the terminology was discovered, not assumed.

---

## Phase 3 — Concept page (if needed)

After the search is complete, assess: **does a concept page need to be created or updated?**

The concept mapping often reveals that the topic deserves its own `wiki/concepts/` page (especially if Phase 1 discovered the topic doesn't yet have one). Use the entity-extraction phase of [[wiki-search]] (Phase 4) for this — it is already part of that workflow.

---

## Summary: what this skill adds over wiki-search

| | wiki-search | wiki-concept-search |
|-|-------------|---------------------|
| Starting point | Known term | Fuzzy description |
| Phase 1 | Direct WoS/web queries | Exploratory web mapping |
| Concept map | Not produced | Produced + shown to user |
| User confirmation | Not needed | Asked before final search |
| Search plan | Implicit | Explicit + documented in search page |
| Final output | Same search page format | Same + `## Concept Discovery` section |

---

## Log format

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] search | <topic> (concept-search)
Search page: wiki/searches/<filename>.md
Sources: web · WoS · bioRxiv
Preliminary queries: <N>
Field discovered: <formal name(s)>
Entities created: <list>
Notes: <one sentence>
```
