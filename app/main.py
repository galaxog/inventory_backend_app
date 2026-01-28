from __future__ import annotations

import os

from app import create_app

# Uvicorn entrypoint: `uvicorn app.main:app --reload`
app = create_app(os.getenv("ENVIRONMENT"))
