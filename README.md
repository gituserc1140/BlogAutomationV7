# Local Blog Generator

Simple local Flask app to generate blog posts using either Cohere or Google Gemini.

Setup

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (recommended in a `.env` file):

- `COHERE_API_KEY` (for Cohere)
- `GEMINI_API_KEY` (for Gemini)
- `FLASK_SECRET` (optional)

3. Run the app:

```bash
python app.py
```

Open http://localhost:5000 and pick a provider, enter a topic, generate and save to `_posts`.
