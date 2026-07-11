# Docs Knowledge Base Sync

![Tests](https://github.com/konnn04/docsift/actions/workflows/tests.yml/badge.svg)
![Daily scrape](https://github.com/konnn04/docsift/actions/workflows/daily-scrape.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)


A small pipeline that scrapes a Zendesk help center, converts each article to Markdown, and keeps a Gemini File Search Store in sync with it. Only new or changed articles are re-uploaded on every run (delta sync), and a support chatbot (**OptiBot**) answers questions grounded in that store, with citations back to the source articles.

## Features

- **Two scrape paths**: the Zendesk Help Center API, with an HTML sitemap scraper as a fallback if the API is unreachable.
- **Delta sync**: a local manifest (`data/manifest.json`) tracks each article's hash and `updated_at`, so unchanged articles are skipped instantly and only real changes are re-uploaded.
- **Parallel uploads/deletes**: independent per-article API calls run concurrently instead of one at a time.
- **CLI flags** to force a scrape source, run scrape-only (no AI provider needed), cap the batch size, or dry-run.
- **Streamlit test UI** with streaming answers and citations.
- **CI/CD**: automated tests, a one-article smoke test, and a daily scheduled scrape — all via GitHub Actions.

## Setup

1. **Clone the repo and enter it**, then create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt   # or requirements.txt for a runtime-only install
   ```

2. **Copy the env file and fill in your own values:**
   ```bash
   cp .env.sample .env
   ```
   At minimum you need a `GEMINI_API_KEY` (from [Google AI Studio](https://aistudio.google.com)). See `.env.sample` for every other setting (locale, chunk-size estimate, concurrency, etc.) and what it does.

## How to run locally

Run the full pipeline (scrape -> diff -> upload):
```bash
python main.py
```

Useful flags:
```bash
python main.py --source html          # force the HTML fallback scraper (skip the Zendesk API)
python main.py --source api           # force the API only, no fallback if it fails
python main.py --only-scraper --limit 5   # just scrape + write Markdown, no Gemini calls needed
python main.py --dry-run --limit 1    # scrape + diff, but skip real uploads/deletes
```

Run the test suite:
```bash
pytest -q
```

Run with Docker (matches what CI runs):
```bash
docker build -t docsift-scraper .
docker run --rm --env-file .env \
  -v "$(pwd)/data:/app/data" \
  docsift-scraper
```

Try the assistant in a browser (streaming answers + citations):
```bash
pip install streamlit   # already in requirements-dev.txt
streamlit run scripts/streamlit_app.py
```

## Chunking strategy

Gemini File Search Stores chunk documents **server-side** — there is no API parameter to set chunk size or overlap, so the actual chunking is entirely managed by Gemini and isn't something this pipeline controls.

To still give a meaningful "chunks embedded" number in the logs, `src/utils.py` estimates it locally: `tokens ≈ len(text) / 4` (a common rough chars-per-token ratio), then `chunks = ceil(tokens / (chunk_size - overlap))` using `GEMINI_CHUNK_SIZE_ESTIMATE_TOKENS=800` and `GEMINI_CHUNK_OVERLAP_ESTIMATE_TOKENS=100` (both configurable in `.env`). Treat this number as an approximation for observability, not Gemini's real internal chunk count.

## CI/CD

Three GitHub Actions workflows live in `.github/workflows/`:

| Workflow | Trigger | What it does |
|---|---|---|
| `tests.yml` | every push / PR | runs `pytest` |
| `smoke-test.yml` | manual (`workflow_dispatch`) | scrapes + uploads exactly **one** real article, to sanity-check the whole path without touching the rest of the store |
| `daily-scrape.yml` | manual (`workflow_dispatch`) only — cron disabled, scraping now runs on Railway | runs the full pipeline in Docker; state (`data/articles/`, `data/manifest.json`) is not persisted between runs here |

**Job logs:** open the repo's **Actions** tab -> *Daily scrape & upload* -> pick a run. Each run also writes a short summary (added/updated/skipped/deleted counts) to that run's Job Summary page, and uploads the full log as a downloadable artifact.

`> Daily scrape logs: https://github.com/OWNER/REPO/actions/workflows/daily-scrape.yml`

**Required repo setup before the workflows will run:**
- Add secret `GEMINI_API_KEY` (Settings -> Secrets and variables -> Actions -> *Secrets*).
- Optionally add variables `GEMINI_MODEL` / `GEMINI_STORE_NAME` (same page -> *Variables*) if you don't want the `.env.sample` defaults.
- Enable **Read and write permissions** for the workflow token (Settings -> Actions -> General -> Workflow permissions), so `daily-scrape.yml` can commit the updated manifest back.

## Assistant answering a sample question

![OptiBot answering a sample question](docs/images/screenshot-sample-question.png)


