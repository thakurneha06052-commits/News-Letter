"""
app.py
------
Main Flask application for NEWS LETTER — An Intelligent Economics
News Analysis Platform.

Run locally:
    python app.py

The app factory pattern (create_app) is used so the same codebase can be
imported by seed_data.py and by a WSGI server (e.g. gunicorn) at deploy
time without duplicating configuration.
"""

import os
from collections import OrderedDict

from flask import Flask, render_template, abort, request
from dotenv import load_dotenv

from models import db, Article, GlossaryTerm

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'newsletter.db')}")
    # Normalize hosted Postgres URLs so SQLAlchemy uses pg8000 explicitly.
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---------------------------------------------------------------
    # Template helpers (available in every Jinja template)
    # ---------------------------------------------------------------
    @app.context_processor
    def inject_categories():
        categories = [c[0] for c in db.session.query(Article.category).distinct().order_by(Article.category)]
        latest_date = db.session.query(db.func.max(Article.date)).scalar()
        return {"nav_categories": categories, "edition_date": latest_date}

    # ---------------------------------------------------------------
    # Routes
    # ---------------------------------------------------------------
    @app.route("/")
    def home():
        latest = Article.query.order_by(Article.date.desc()).limit(6).all()
        featured = latest[0] if latest else None
        rest = latest[1:] if latest else []

        # A handful of headline stats for the "ticker" strip on the homepage.
        # Pulled straight from the seeded articles rather than hardcoded,
        # so it stays accurate if the data changes.
        stats = build_stat_ticker()

        return render_template(
            "index.html",
            featured=featured,
            latest=rest,
            stats=stats,
        )

    @app.route("/article/<int:article_id>")
    def article_detail(article_id):
        article = Article.query.get_or_404(article_id)

        # Filtering in Python (rather than a JSON `contains` query) keeps
        # this portable across SQLite/PostgreSQL without relying on
        # driver-specific JSON operators.
        related_terms = [
            t for t in GlossaryTerm.query.all() if article.id in (t.related_article_ids or [])
        ]

        more = (
            Article.query.filter(Article.category == article.category, Article.id != article.id)
            .order_by(Article.date.desc())
            .limit(3)
            .all()
        )

        return render_template(
            "article.html",
            article=article,
            related_terms=related_terms,
            more_articles=more,
        )

    @app.route("/category/<path:category_name>")
    def category(category_name):
        articles = (
            Article.query.filter(Article.category == category_name)
            .order_by(Article.date.desc())
            .all()
        )
        if not articles:
            # Category might exist but have zero articles seeded yet --
            # still show the page instead of a hard 404.
            known = {c[0] for c in db.session.query(Article.category).distinct()}
            if category_name not in known:
                abort(404)

        return render_template("category.html", category_name=category_name, articles=articles)

    @app.route("/glossary")
    def glossary():
        terms = GlossaryTerm.query.order_by(GlossaryTerm.term).all()
        return render_template("glossary.html", terms=terms)

    @app.route("/search")
    def search():
        q = request.args.get("q", "").strip()
        results = []
        if q:
            like = f"%{q}%"
            results = (
                Article.query.filter(
                    db.or_(Article.headline.ilike(like), Article.intro.ilike(like))
                )
                .order_by(Article.date.desc())
                .all()
            )
        return render_template("search.html", query=q, results=results)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


def build_stat_ticker():
    """
    Pull one short, punchy stat per article for the homepage ticker strip.
    Keeps this logic in one place instead of duplicating it in a template.
    """
    articles = Article.query.order_by(Article.date.desc()).limit(8).all()
    ticker = []
    for a in articles:
        if a.key_facts:
            ticker.append({"label": a.category, "fact": a.key_facts[0], "article_id": a.id})
    return ticker


app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, port=int(os.environ.get("PORT", 5000)))
