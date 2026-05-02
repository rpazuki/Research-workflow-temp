---
name: wiki-talk-notes
description: Process seminar, talk, workshop, or lecture notes into the Research Wiki. Trigger when the user mentions a note file from a talk or seminar and wants it cleaned up, frontmatter added, or ingested — phrases like "process my talk notes", "add this seminar note", "ingest my lecture notes", "clean up and add to wiki", or when a file from Notes/Talks/ is referenced for wiki integration.
---

# Wiki TALK NOTES Workflow

This workflow processes notes from talks, seminars, workshops, or lectures. It cleans up the note file itself (frontmatter + grammar) then treats the note as a source document and follows the INGEST workflow.

> **Page conventions:** Frontmatter schemas, required page sections, cross-referencing style, and log/index formats are in `CLAUDE.md`. Read it if you need a reminder.

## Frontmatter fields to extract / add

| Field | Notes |
|-------|-------|
| `title` | Talk title or topic — extract from file, ask if missing |
| `speaker` | Presenter name(s), comma-separated for multiples |
| `venue` | Institution, location, or event name |
| `event_type` | One of: seminar, talk, workshop, lecture, personal-notes |
| `date` | Event date in YYYY-MM-DD — ask if only partial date is provided |
| `type` | Always `"source"` for consistency with INGEST |
| `tags` | Lowercase hyphenated domain tags, e.g. `[fba, metabolism, e-coli]` |
| `created` | Today's date |
| `updated` | Today's date |
| `sources` | Number of papers/sources cited in the notes |

## Steps

1. **Read the note file** at the path specified by the user.

2. **Extract metadata.** Pull title, speaker, venue, date, and event_type from the file content. If any are missing, ask the user before proceeding.

3. **Add or update YAML frontmatter** at the top of the note file with all fields above.

4. **Review and correct grammar, spelling, and sentence structure** throughout the note. If corrections are extensive (more than a handful of sentences), show the user a summary of what you intend to change and ask for approval before writing.

5. **INGEST the note as a source.** Once frontmatter and grammar are finalised, read `skills/wiki-ingest/SKILL.md` and follow all steps there — this note is now treated as a source document.
   - Key difference from a raw PDF: the note file *is* updated in place (frontmatter + grammar). Raw PDFs in `raw/` remain immutable.

6. **Identify new glossary terms.** Scan the note for key terms, concepts, or entities that warrant glossary entries and are not yet in `wiki/glossary.md`.

7. **Add glossary entries.** For each new term, read `skills/wiki-glossary/SKILL.md` and follow the GLOSSARY workflow.

8. **Append to `wiki/log.md`:**
   ```
   ## [YYYY-MM-DD] talk-notes | <talk title> by <speaker>
   Source page: wiki/sources/<slug>.md
   Glossary additions: <list of terms added, or "none">
   Pages touched: <comma-separated list>
   Notes: <one sentence on key insights>
   ```
