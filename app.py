from flask import Flask, render_template, request, redirect, url_for, flash
from providers import generate_with_provider
from dotenv import load_dotenv
import os, datetime, re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

POSTS_DIR = os.path.join(os.getcwd(), "_posts")
os.makedirs(POSTS_DIR, exist_ok=True)


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def _extract_title_and_body(generated: str):
    lines = generated.splitlines()
    # Skip leading empty lines
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return "Untitled", ""

    first = lines[0].strip()
    if first.startswith("# "):
        title = first.lstrip("# ").strip()
        body = "\n".join(lines[1:]).lstrip()
    elif first.lower().startswith("title:"):
        title = first.split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).lstrip()
    else:
        # Use first non-empty line as title
        title = first
        body = "\n".join(lines[1:]).lstrip()

    return title, body


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    provider = request.form.get("provider", "cohere")
    if not topic:
        flash("Please enter a topic", "error")
        return redirect(url_for("index"))

    try:
        generated = generate_with_provider(provider, topic)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("index"))

    title, body = _extract_title_and_body(generated)
    return render_template("result.html", title=title, content=body, provider=provider)


@app.route("/save", methods=["POST"])
def save():
    title = request.form.get("title", "Untitled").strip()
    content = request.form.get("content", "").strip()
    if not content:
        flash("No content to save", "error")
        return redirect(url_for("index"))

    date = datetime.date.today().isoformat()
    slug = _slugify(title)
    filename = f"{date}-{slug}.md"
    path = os.path.join(POSTS_DIR, filename)

    cleaned_title = title.replace('"', "'")
    front_matter = f"---\nlayout: post\ntitle: \"{cleaned_title}\"\ndate: {date}\n---\n\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(front_matter + content)

    flash(f"Saved post: {filename}", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
