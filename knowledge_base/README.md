# Knowledge Base — Maintainer Notes

`gen_academy_seed.json` is loaded whole and passed to the LLM on every content question
(see `docs/requirements-spec.md` Section 7.1). Do not add disclaimers like
`[Placeholder — ...]` inside a document's `content` field — the LLM reads that as "this
information is unconfirmed" and will refuse to answer with it, even inconsistently
depending on question phrasing. Keep placeholder/TODO notes here instead.

## Entries still using placeholder values

- `recording-week-2`, `recording-week-3` — `url` fields point at `example.com`, not real
  recording links.
- `guest-speaker-week-4` — guest name/affiliation ("Example Guest Name (Example Company)")
  is a placeholder.
- `course-schedule` — has no real 2026 session dates.

Replace these with confirmed values before a live demo (Vidhya's responsibility per the
requirements spec, Section 10).
