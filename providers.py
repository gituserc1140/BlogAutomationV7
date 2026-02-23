import os
import re
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug


def _make_prompt(topic: str) -> str:
    # Ask the model to produce Markdown where the first line is an H1 title
    return (
        f"Write a clear, well-structured blog post in Markdown.\n"
        f"Start with an H1 title line (for example: '# My Title') on its own first line,\n"
        f"then include headings, subheadings, short paragraphs, and a brief conclusion.\n"
        f"Write for a general audience and keep the tone friendly and informative.\n\n"
        f"Topic: {topic}\n\n"
    )


def generate_with_cohere(topic: str) -> str:
    try:
        import cohere
    except Exception:
        raise RuntimeError("Cohere client not installed")

    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY not set in environment")

    # Prefer the new ClientV2 chat API. Fall back if unavailable.
    prompt = _make_prompt(topic)
    try:
        # Cohere v5+ exposes ClientV2 for chat-style API
        client = cohere.ClientV2(api_key=COHERE_API_KEY)
        messages = [{"role": "user", "content": prompt}]
        # model choice may vary by account; adjust if needed
        resp = client.chat(model="command-a-03-2025", messages=messages)
        # The API returns a list of content parts; join them if needed
        if hasattr(resp, "response") and isinstance(resp.response, dict):
            # Try common shapes
            out = resp.response.get("content") or resp.response.get("generations")
            if isinstance(out, list):
                return "".join([p.get("text", str(p)) for p in out])
            return str(out)
        # Fallback to string conversion
        return str(resp)
    except AttributeError:
        # Older cohere packages may not have ClientV2; try legacy client if present
        client = cohere.Client(COHERE_API_KEY)
        resp = client.generate(model="command-xlarge-nightly", prompt=prompt, max_tokens=800)
        return resp.generations[0].text
    except Exception as e:
        # Surface useful error message to caller
        raise RuntimeError(f"Cohere generation error: {e}")


def generate_with_gemini(topic: str) -> str:
    try:
        import google.generativeai as genai
    except Exception:
        raise RuntimeError("google-generativeai not installed")

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-flash-latest")
    prompt = _make_prompt(topic)
    out = model.generate_content(prompt)
    return getattr(out, "text", str(out))


def generate_with_provider(provider: str, topic: str) -> str:
    provider = provider.lower()
    if provider == "cohere":
        return generate_with_cohere(topic)
    elif provider in ("gemini", "google", "gpt", "gemini-flash"):
        return generate_with_gemini(topic)
    else:
        raise ValueError(f"Unknown provider: {provider}")

