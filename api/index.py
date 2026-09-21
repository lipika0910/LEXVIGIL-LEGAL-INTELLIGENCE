"""Vercel ASGI entry. Intentionally never imports the local SQLite application."""
from backend.showcase_bootstrap import build_showcase_app

app = build_showcase_app()
