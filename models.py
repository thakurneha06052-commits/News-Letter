"""
models.py
---------
Database models for NEWS LETTER.

Two tables:
  Article       - one row per economics news article
  GlossaryTerm  - one row per "Economics Explained" term

We keep list-type fields (key_facts, related_article_ids) as JSON columns.
SQLite supports JSON via SQLAlchemy's JSON type transparently, so no need
for a separate normalized table -- simpler to explain in a viva.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(300), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)

    intro = db.Column(db.Text, nullable=False)
    what_happened = db.Column(db.Text, nullable=False)
    key_facts = db.Column(db.JSON, nullable=False, default=list)
    why_important = db.Column(db.Text, nullable=False)
    economic_impact = db.Column(db.Text, nullable=False)
    impact_on_people = db.Column(db.Text, nullable=False)
    simple_explanation = db.Column(db.Text, nullable=False)

    source = db.Column(db.String(300))
    source_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Article {self.id}: {self.headline[:40]}>"

    @property
    def slug_category(self):
        """URL-friendly version of the category name, e.g. 'Banking & Finance' -> 'banking-finance'."""
        return (
            self.category.lower()
            .replace(" & ", "-")
            .replace(" ", "-")
        )


class GlossaryTerm(db.Model):
    __tablename__ = "glossary_terms"

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(150), nullable=False, unique=True)
    definition = db.Column(db.Text, nullable=False)
    related_article_ids = db.Column(db.JSON, nullable=False, default=list)

    def __repr__(self):
        return f"<GlossaryTerm {self.term}>"
