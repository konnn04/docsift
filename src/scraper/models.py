from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Article:
    id: str          
    title: str
    url: str          
    section: str       
    updated_at: str 
    html: str          
    source: str = "api"  # "api" | "html_fallback"

    @property
    def slug(self) -> str:
        import re

        base = self.title.strip().lower()
        base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
        return f"{self.id}-{base}"[:120] or self.id