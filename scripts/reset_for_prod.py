from __future__ import annotations
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.config import settings
from google import genai
from google.genai import types


def main() -> int:
    client = genai.Client(api_key=settings.gemini_api_key)

    deleted = False
    for store in client.file_search_stores.list():
        if store.display_name == settings.gemini_store_name:
            print(f"Deleting Gemini store {store.name!r} (display_name={settings.gemini_store_name!r})")
            client.file_search_stores.delete(
                name=store.name, config=types.DeleteFileSearchStoreConfig(force=True)
            )
            deleted = True
    if not deleted:
        print(f"No store named {settings.gemini_store_name!r} found (nothing to delete).")

    articles_dir = Path(settings.articles_dir)
    manifest_path = Path(settings.manifest_path)

    if articles_dir.exists():
        shutil.rmtree(articles_dir)
        print(f"Removed {articles_dir}")

    if manifest_path.exists():
        manifest_path.unlink()
        print(f"Removed {manifest_path}")

    print("Reset complete. Next pipeline run starts from a clean slate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
