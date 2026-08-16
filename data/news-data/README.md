# NEWS LETTER — News Data

This folder holds the raw economics news content for your **NEWS LETTER** Flask
project. It's plain JSON, not HTML, so it can be loaded straight into your
SQLAlchemy database instead of being rewritten as templates.

## Structure

```
news-data/
├── index.json          # list of all articles with id, file path, headline, category, date
├── categories.json      # the fixed list of categories for filtering/nav
├── glossary.json         # "Economics Explained" terms, linked to article ids
├── README.md
└── articles/
    ├── article-01.json
    ├── article-02.json
    ├── ...
    └── article-11.json  # 11 articles (spec asked for 10+)
```

Each `article-XX.json` has this shape:

```json
{
  "id": 1,
  "headline": "...",
  "date": "2026-08-05",
  "category": "Banking & Finance",
  "intro": "...",
  "what_happened": "...",
  "key_facts": ["...", "..."],
  "why_important": "...",
  "economic_impact": "...",
  "impact_on_people": "...",
  "simple_explanation": "...",
  "source": "Publication name(s)",
  "source_url": "https://..."
}
```

This maps directly onto an `Article` model — one row per file, `key_facts`
stored as a JSON/Text column or a related `ArticleFact` table if you want it
normalized.

## Using this in your Flask project

1. Put this whole `news-data/` folder somewhere outside `static/` and
   `templates/` (e.g. project root, or a `/data` folder) — it's seed data,
   not something served directly to the browser.
2. Write a `seed_data.py` that reads `index.json`, opens each linked article
   file, and inserts a row per article into your `Article` table via
   SQLAlchemy. `glossary.json` seeds an `EconTerm` table the same way.
3. Your routes (`/`, `/article/<id>`, `/category/<name>`) then query the
   database instead of rendering static HTML files — one `article.html`
   Jinja template handles every article.
4. `categories.json` gives you the fixed category list for your nav bar and
   filter dropdown, so it doesn't need to be hardcoded in every template.

## Sourcing note

Every article was researched from real, dated reporting (Reuters, Business
Standard, PIB, NPCI, Forbes India, etc. — see each `source`/`source_url`
field) and written in original wording, not copied from the source. Figures
and dates should still be spot-checked against the linked source before
submission, since some are provisional/revised figures that get updated.
