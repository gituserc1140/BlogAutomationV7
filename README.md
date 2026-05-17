# Local Blog Generator

Simple local app to generate blog posts using either Cohere or Google Gemini. The repository now includes both a Flask UI and a Streamlit UI.

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

3. Run the Flask app:

```bash
python app.py
```

Open http://localhost:5000 and pick a provider, enter a topic, generate and save to `_posts`.

4. Or run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Streamlit will print a local URL, usually http://localhost:8501.
