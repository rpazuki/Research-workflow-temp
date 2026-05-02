# Wiki Log

Append-only chronological record of all wiki operations. Each entry starts with:
`## [YYYY-MM-DD] <type> | <title>`

Types: `ingest` · `talk-notes` · `sparse-talk-notes` · `query` · `lint` · `glossary` · `update` · `search`

---

## [2026-05-02] update | wiki scaffold initialised

Wiki directory structure created from scratch. Replace <topic> tags in index.md, overview.md, and glossary.md with your actual topic name. Files created:
- `wiki/index.md` — master content catalog
- `wiki/log.md` — this file
- `wiki/overview.md` — field synthesis placeholder
- `wiki/glossary.md` — glossary placeholder
- `wiki/concepts/` — directory for concept pages
- `wiki/entities/` — directory for entity pages
- `wiki/sources/` — directory for source pages
- `wiki/analyses/` — directory for analysis pages
- `wiki/searches/` — directory for search result pages

## [2026-05-02] lint | initial health check

Wiki is freshly initialised with no content pages. Scaffold files pass structural checks:
- No broken wikilinks (no wikilinks exist yet)
- No missing concept/entity pages
- No orphan pages
- No index gaps
- No stale claims
- Frontmatter present on all scaffold pages

Fixed: none (nothing to fix on an empty wiki)
Deferred: none
