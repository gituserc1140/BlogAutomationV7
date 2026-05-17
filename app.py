from flask import Flask, render_template, request, redirect, url_for, flash
from providers import generate_with_provider
from blog_utils import extract_title_and_body, save_post
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")


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

    title, body = extract_title_and_body(generated)
    return render_template("result.html", title=title, content=body, provider=provider)


@app.route("/save", methods=["POST"])
def save():
    title = request.form.get("title", "Untitled").strip()
    content = request.form.get("content", "").strip()
    if not content:
        flash("No content to save", "error")
        return redirect(url_for("index"))

    filename = save_post(title, content)

    flash(f"Saved post: {filename}", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
