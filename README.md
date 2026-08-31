# Prospect Intelligence

Company-level B2B prospect intelligence using Firecrawl, Seltz, Gemini, and Streamlit.

## Run

```powershell
copy .env.example .env
uv sync
uv run pytest -v
uv run streamlit run app.py
```

Add real API keys to `.env` before starting Streamlit.
