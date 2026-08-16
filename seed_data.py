"""
seed_data.py
------------
Reads news-data/index.json + news-data/articles/*.json + glossary.json
and loads them into the database defined in models.py.

Usage:
    python seed_data.py            # seed (skips if articles already exist)
    python seed_data.py --reset    # wipe tables and reseed from scratch
"""

import json
import os
import sys
from datetime import datetime

from app import create_app
from models import db, Article, GlossaryTerm

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "news-data")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if "--reset" in sys.argv:
            print("Resetting tables...")
            Article.query.delete()
            GlossaryTerm.query.delete()
            db.session.commit()

        if Article.query.first() is not None:
            print("Articles already exist -- skipping. Use --reset to reseed.")
        else:
            index = load_json(os.path.join(DATA_DIR, "index.json"))
            count = 0
            for entry in index["articles"]:
                article_path = os.path.join(DATA_DIR, entry["file"])
                data = load_json(article_path)

                article = Article(
                    id=data["id"],
                    headline=data["headline"],
                    date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
                    category=data["category"],
                    intro=data["intro"],
                    what_happened=data["what_happened"],
                    key_facts=data["key_facts"],
                    why_important=data["why_important"],
                    economic_impact=data["economic_impact"],
                    impact_on_people=data["impact_on_people"],
                    simple_explanation=data["simple_explanation"],
                    source=data.get("source"),
                    source_url=data.get("source_url"),
                )
                db.session.add(article)
                count += 1

            db.session.commit()
            print(f"Seeded {count} articles.")

        if GlossaryTerm.query.first() is not None:
            print("Glossary already exists -- skipping.")
        else:
            glossary = load_json(os.path.join(DATA_DIR, "glossary.json"))
            for entry in glossary:
                term = GlossaryTerm(
                    term=entry["term"],
                    definition=entry["definition"],
                    related_article_ids=entry.get("related_article_ids", []),
                )
                db.session.add(term)
            db.session.commit()
            print(f"Seeded {len(glossary)} glossary terms.")

        print("Done.")


if __name__ == "__main__":
    seed()
