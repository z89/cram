# cram — Canvas → Notion Sync

Syncs Canvas LMS course content into a Notion workspace, mirroring the user's existing university page structure.

---

## Project Goal

Pull structured course data from Canvas (via personal access token) and populate a Notion workspace that mirrors the user's existing layout:

```
university (Notion page)
  └─ classes DB
       └─ [Course page]  e.g. CAB401: High Performance and Parallel Computing
            ├─ content DB  (one entry per week)
            │    └─ [Week page]  e.g. Week 2 - Different Forms of Parallel Computing
            │         ├─ Properties: Class, Lec (checkbox), Tutorial (checkbox), Start Date
            │         ├─ activities DB (Kanban: todo / doing / finished)
            │         │    └─ [Activity page]  e.g. Activity 2.1 — Lecture slides
            │         └─ learning materials section (Canvas page HTML converted to Notion blocks)
            └─ assessment DB (one entry per assignment)
                 └─ [Assignment page]  due date, description, submission details
```

---

## Canvas Data to Scrape

| Canvas resource     | Maps to Notion                                      |
|---------------------|-----------------------------------------------------|
| Course              | Course page in `classes` DB                        |
| Modules             | Weeks in `content` DB (module name → week title)   |
| Module items        | Activities in `activities` kanban per week          |
| Page content (HTML) | `learning materials` section inside week page      |
| Assignments         | Entries in `assessment` DB                         |
| Files               | Linked in relevant week or assessment page         |
| Announcements       | (future) pinned callout on course page             |

---

## Notion Structure Details

### Course page properties
- Name (title): `{CODE}: {Course Name}`
- Icon: laptop emoji (default)
- Sub-databases: `content`, `assessment`

### Week page properties
- Name (title): `Week {N} - {Module Name}`
- `Class` (select): course code e.g. `CAB401`
- `Lec` (checkbox): false by default
- `Tutorial` (checkbox): false by default
- `Start Date` (date): week start date from Canvas module unlock date
- `cram_id` (rich text, hidden): Canvas module ID — used for sync targeting

### Activity page properties
- Name (title): activity name from Canvas module item
- `Status` (select): `todo` | `doing` | `finished`  — **never overwritten on re-sync**
- `cram_id` (rich text, hidden): Canvas module item ID

### Assignment page properties
- Name (title): assignment name
- `Due Date` (date)
- `Points` (number)
- `Status` (select): `todo` | `doing` | `finished`
- `cram_id` (rich text, hidden): Canvas assignment ID

---

## Sync Strategy

### What cram owns
Cram tracks all content it creates via the `cram_id` property on every page it manages. On re-sync:
- Pages are matched by `cram_id`, not name
- New Canvas items → new Notion pages created
- Removed Canvas items → Notion pages archived (not deleted)
- Changed Canvas items → content updated (see below)

### What is preserved (never overwritten)
- `Status` property on activities and assignments (user's todo/doing/finished progress)
- Any Notion blocks the user added **outside** of cram-managed sections
- User-added pages in any database that lack a `cram_id` property

### How block-level content is tracked
Canvas-sourced content inside a week page is wrapped in a **toggle block** with title `🔄 Canvas Content`. On re-sync, cram replaces everything inside this toggle but leaves all blocks outside it untouched.

Format inside week page:
```
[toggle: 🔄 Canvas Content]          ← cram replaces internals on sync
  [converted HTML blocks from Canvas page]

[user's own notes below — untouched]
```

### Content hash tracking
A local `state.json` stores `{ cram_id: content_hash }` per synced item. Content is only pushed to Notion if the hash changed, avoiding redundant API calls.

---

## Project Structure

```
cram/
├── CLAUDE.md
├── pyproject.toml
├── .env.example
├── state.json               # local sync state (gitignored)
├── cram/
│   ├── __init__.py
│   ├── cli.py               # CLI entry point (typer)
│   ├── config.py            # loads .env / config
│   ├── canvas/
│   │   ├── client.py        # Canvas API wrapper (canvasapi)
│   │   └── models.py        # Course, Module, Item, Assignment dataclasses
│   ├── notion/
│   │   ├── client.py        # Notion API wrapper (notion-client)
│   │   ├── builder.py       # Creates/updates pages and databases
│   │   └── converter.py     # HTML → Notion blocks (via markdownify + custom parser)
│   └── sync/
│       ├── engine.py        # Orchestrates full sync flow
│       └── state.py         # Hash tracking and state.json management
└── tests/
    └── ...
```

---

## CLI Interface

```bash
# Sync a specific course (by course code or Canvas course ID)
cram sync --course CAB401

# List all available courses from Canvas
cram courses

# Run in daemon mode (checks for changes every N minutes)
cram daemon --interval 30

# Use a debug Notion page instead of real university page
cram sync --course CAB401 --debug
```

The `--debug` flag routes all Notion writes to a separate `notion-university-debug` page to avoid touching the real university workspace during development.

---

## Environment Variables

```env
CANVAS_API_URL=https://<your-uni>.instructure.com
CANVAS_ACCESS_TOKEN=...

NOTION_TOKEN=...
NOTION_UNIVERSITY_PAGE_ID=...        # real university page
NOTION_DEBUG_PAGE_ID=...             # debug page for testing
```

---

## Tech Stack

- Python 3.12+
- `canvasapi` — Canvas REST API wrapper
- `notion-client` — official Notion SDK
- `markdownify` — HTML to Markdown for content conversion
- `typer` — CLI framework
- `python-dotenv` — env config
- `apscheduler` — daemon/scheduled sync mode
- `rich` — terminal output

---

## Implementation Phases

### Phase 1 — Scaffold & Canvas fetch
- [ ] Project setup (pyproject.toml, deps, .env.example)
- [ ] Canvas client: fetch courses, modules, module items, assignments, pages
- [ ] CLI: `cram courses` and dry-run output

### Phase 2 — Notion debug setup
- [ ] Create debug university page manually in Notion, add page ID to .env
- [ ] Notion builder: create course page, content DB, assessment DB
- [ ] Notion builder: create week pages with all properties

### Phase 3 — Activities + content
- [ ] Activities kanban per week page (todo/doing/finished)
- [ ] HTML → Notion blocks converter
- [ ] `🔄 Canvas Content` toggle section per week

### Phase 4 — Sync engine
- [ ] Hash-based change detection (state.json)
- [ ] Re-sync: update Canvas content blocks, preserve Status and user blocks
- [ ] Archive removed Canvas items

### Phase 5 — CLI + daemon
- [ ] Full `cram sync` flow with `--debug` flag
- [ ] Daemon mode with apscheduler

---

## Notes

- Always test against `--debug` page. Never write to the real university page during development.
- Canvas module "unlock dates" map to week `Start Date`. If unavailable, fall back to course start date + (week_index * 7 days).
- The `cram_id` property should be hidden in Notion (move to end of property list) so it doesn't clutter the UI.
- File attachments: link to Canvas file URL (no re-hosting). Files require the Canvas token in the URL, so embed as a bookmark block with the direct download URL.
