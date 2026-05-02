---
name: wiki-sparse-notes
description: Enrich sparse talk or seminar notes with online research. Trigger when the user has brief bullet-point notes from a talk and wants each point researched and expanded — phrases like "enrich my talk notes", "research each topic in my notes", "expand my sparse notes", "look up each bullet point", or when notes are described as minimal/brief and the goal is personal learning rather than formal wiki ingestion.
---

# Wiki SPARSE TALK NOTES WITH RESEARCH Workflow

This workflow is for *brief* bullet-point notes (single phrases or short sentences) captured during a talk. It enriches each note entry with online research so the file becomes a useful personal reference — the goal is understanding and retention, not formal wiki ingestion.

**When to use instead of TALK NOTES:** Choose this workflow when the original notes are minimal bullets and the user wants each one researched and expanded inline, rather than producing a structured wiki source page. If the notes are substantial prose already, use the TALK NOTES workflow instead.

> **Page conventions:** Frontmatter schemas, log/index formats are in `CLAUDE.md`. Read it if you need a reminder.

## Frontmatter fields

Same fields as TALK NOTES: `title`, `speaker`, `venue`, `event_type`, `date`, `type: "source"`, `tags`, `created`, `updated`.

## Steps

1. **Read the sparse note file** at the path specified by the user.

2. **Extract metadata** (title, speaker, venue, date, event_type). Ask the user if any are missing.

3. **Add YAML frontmatter** to the top of the file.

4. **For each bullet point / note entry**, produce the following block and append it to the file (or replace the original bullet):

   ```markdown
   ### N. <Original note text>

   **Talk note:** <verbatim original bullet>

   **Online research:**
   <2–4 sentence summary of key findings from WebSearch>

   **Key finding:** <single-line takeaway>
   ```

   - Preserve the user's exact wording as the heading and in "Talk note".
   - Run one or more `WebSearch` queries per topic to gather authoritative context.
   - Keep the research concise — clarity over comprehensiveness.
   - If a topic connects to a concept already in the wiki, add a brief note: `*See also: [[concept-page]]*`.

5. **(Optional) Add a "Summary of Interconnections" section** at the end if several topics share a unifying theme — helpful for seeing the big picture of the talk.

6. **Update `wiki/index.md`** to add the note as a source entry.

7. **Append to `wiki/log.md`:**
   ```
   ## [YYYY-MM-DD] sparse-talk-notes | <talk title> by <speaker>
   File: Notes/Talks/<path>/<filename>.md
   Topics enriched: <N sections — list topic names>
   Notes: <one sentence on the domain or unifying theme>
   ```
