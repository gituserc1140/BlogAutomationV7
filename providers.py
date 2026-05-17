import os
import re
from dotenv import load_dotenv

load_dotenv()


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


def _get_env_var(name: str) -> str:
    load_dotenv()
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} not set in environment")
    return value


def _extract_cohere_text(response) -> str:
    message = getattr(response, "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, list):
        text_parts = [part.text for part in content if hasattr(part, "text") and part.text]
        if text_parts:
            return "".join(text_parts)

    if hasattr(response, "response") and isinstance(response.response, dict):
        out = response.response.get("content") or response.response.get("generations")
        if isinstance(out, list):
            return "".join([part.get("text", str(part)) for part in out])
        if out:
            return str(out)

    return str(response)


def generate_with_cohere(topic: str) -> str:
    try:
        import cohere
    except Exception:
        raise RuntimeError("Cohere client not installed")

    cohere_api_key = _get_env_var("COHERE_API_KEY")

    # Prefer the new ClientV2 chat API. Fall back if unavailable.
    prompt = _make_prompt(topic)
    try:
        # Cohere v5+ exposes ClientV2 for chat-style API
        client = cohere.ClientV2(api_key=cohere_api_key)
        messages = [{"role": "user", "content": prompt}]
        # model choice may vary by account; adjust if needed
        resp = client.chat(model="command-a-03-2025", messages=messages)
        return _extract_cohere_text(resp)
    except AttributeError:
        # Older cohere packages may not have ClientV2; try legacy client if present
        client = cohere.Client(cohere_api_key)
        resp = client.generate(model="command-xlarge-nightly", prompt=prompt, max_tokens=800)
        return resp.generations[0].text
    except Exception as e:
        # Surface useful error message to caller
        raise RuntimeError(f"Cohere generation error: {e}")


def generate_with_gemini(topic: str) -> str:
    gemini_api_key = _get_env_var("GEMINI_API_KEY")
    prompt = _make_prompt(topic)

    try:
        from google import genai
    except Exception:
        genai = None

    if genai is not None:
        try:
            client = genai.Client(api_key=gemini_api_key)
            out = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            text = getattr(out, "text", "")
            if text:
                return text
            return str(out)
        except Exception as exc:
            raise RuntimeError(f"Gemini generation error: {exc}")

    try:
        import google.generativeai as legacy_genai
    except Exception:
        raise RuntimeError("google-genai not installed")

    legacy_genai.configure(api_key=gemini_api_key)
    model = legacy_genai.GenerativeModel("gemini-flash-latest")
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

