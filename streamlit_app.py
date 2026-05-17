import json

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from blog_utils import extract_title_and_body, save_post
from providers import generate_with_provider


load_dotenv()


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@400;500;600;700;800&display=swap');

            :root {
                --bg: #f6f0e8;
                --panel: rgba(255, 252, 247, 0.82);
                --panel-strong: #fffaf4;
                --ink: #201714;
                --muted: #6c5f58;
                --accent: #c9622f;
                --accent-deep: #8e3d1d;
                --line: rgba(32, 23, 20, 0.08);
                --shadow: 0 20px 60px rgba(88, 54, 35, 0.12);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(233, 161, 107, 0.26), transparent 28%),
                    radial-gradient(circle at top right, rgba(151, 190, 186, 0.22), transparent 24%),
                    linear-gradient(180deg, #fbf7f1 0%, var(--bg) 100%);
                color: var(--ink);
                font-family: 'Manrope', sans-serif;
            }

            .block-container {
                padding-top: 2.2rem;
                padding-bottom: 3rem;
                max-width: 1180px;
            }

            h1, h2, h3 {
                color: var(--ink);
                letter-spacing: -0.03em;
            }

            .hero-panel,
            .surface-card,
            .metric-card {
                background: var(--panel);
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                backdrop-filter: blur(16px);
            }

            .hero-panel {
                padding: 2rem 2rem 1.6rem;
                border-radius: 28px;
                margin-bottom: 1.25rem;
            }

            .hero-kicker {
                text-transform: uppercase;
                letter-spacing: 0.18em;
                font-size: 0.72rem;
                font-weight: 800;
                color: var(--accent-deep);
                margin-bottom: 0.8rem;
            }

            .hero-title {
                font-family: 'Instrument Serif', serif;
                font-size: clamp(2.8rem, 6vw, 4.8rem);
                line-height: 0.95;
                margin: 0;
                max-width: 11ch;
            }

            .hero-copy {
                color: var(--muted);
                font-size: 1.05rem;
                line-height: 1.7;
                max-width: 60ch;
                margin-top: 1rem;
                margin-bottom: 1.2rem;
            }

            .hero-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
            }

            .hero-badge {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.45rem 0.85rem;
                background: rgba(201, 98, 47, 0.1);
                color: var(--accent-deep);
                font-size: 0.85rem;
                font-weight: 700;
            }

            .surface-card {
                border-radius: 24px;
                padding: 1.2rem 1.2rem 0.6rem;
                margin-bottom: 1rem;
            }

            .surface-title {
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            }

            .surface-copy {
                color: var(--muted);
                margin-bottom: 0.8rem;
                line-height: 1.6;
            }

            .metric-card {
                border-radius: 22px;
                padding: 1rem 1.1rem;
                min-height: 130px;
            }

            .metric-label {
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-size: 0.72rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
            }

            .metric-value {
                font-size: 2rem;
                line-height: 1;
                font-weight: 800;
                color: var(--ink);
                margin-bottom: 0.35rem;
            }

            .metric-note {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.5;
            }

            .stTextInput label,
            .stSelectbox label,
            .stTextArea label {
                font-weight: 700;
                color: var(--ink);
            }

            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] > div {
                background: rgba(255, 250, 244, 0.92);
                border-radius: 16px;
                border: 1px solid rgba(32, 23, 20, 0.12);
            }

            .stButton > button,
            .stFormSubmitButton > button {
                background: linear-gradient(135deg, var(--accent) 0%, #dd8c50 100%);
                color: white;
                border: 0;
                border-radius: 999px;
                font-weight: 800;
                padding: 0.7rem 1.2rem;
                box-shadow: 0 10px 24px rgba(201, 98, 47, 0.22);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
            }

            .stTabs [data-baseweb="tab"] {
                background: rgba(255, 250, 244, 0.9);
                border-radius: 999px;
                padding: 0.4rem 1rem;
                border: 1px solid rgba(32, 23, 20, 0.08);
            }

            .stTabs [aria-selected="true"] {
                background: white;
                color: var(--accent-deep);
            }

            .stAlert {
                border-radius: 18px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_state() -> None:
    st.session_state.setdefault("generated_title", "")
    st.session_state.setdefault("generated_content", "")
    st.session_state.setdefault("last_provider", "cohere")
    st.session_state.setdefault("last_saved_filename", "")


def _render_hero() -> None:
    st.markdown(
        """
        <section class="hero-panel">
            <div class="hero-kicker">Editorial Studio</div>
            <h1 class="hero-title">Turn a rough topic into a publishable draft.</h1>
            <p class="hero-copy">
                Generate a markdown article, shape the headline and body in place, preview the final structure,
                then save a post directly into your local <code>_posts</code> directory.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">Cohere + Gemini</span>
                <span class="hero-badge">Markdown-first</span>
                <span class="hero-badge">Local file export</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <section class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _content_metrics(title: str, content: str) -> tuple[str, str, str]:
    word_count = len(content.split()) if content.strip() else 0
    heading_count = sum(1 for line in content.splitlines() if line.lstrip().startswith("#"))
    read_time = max(1, round(word_count / 200)) if word_count else 0
    return str(word_count), str(heading_count), f"{read_time} min" if read_time else "0 min"


def _render_copy_button(title: str, content: str) -> None:
        payload = title.strip()
        if content.strip():
                payload = f"# {title.strip() or 'Untitled'}\n\n{content}" if title.strip() else content

        components.html(
                f"""
                <div style="padding-top: 0.1rem;">
                    <button
                        id="copy-draft-button"
                        type="button"
                        style="
                            width: 100%;
                            border: 0;
                            border-radius: 999px;
                            padding: 0.78rem 1.2rem;
                            font-weight: 800;
                            cursor: pointer;
                            color: white;
                            background: linear-gradient(135deg, #5f7c6d 0%, #3f5f53 100%);
                            box-shadow: 0 10px 24px rgba(63, 95, 83, 0.2);
                        "
                    >
                        Copy draft
                    </button>
                    <div id="copy-draft-status" style="padding-top: 0.65rem; color: #6c5f58; font: 600 0.92rem Manrope, sans-serif;"></div>
                </div>
                <script>
                    const copyButton = document.getElementById("copy-draft-button");
                    const copyStatus = document.getElementById("copy-draft-status");
                    const copyPayload = {json.dumps(payload)};

                    copyButton.addEventListener("click", async () => {{
                        try {{
                            await navigator.clipboard.writeText(copyPayload);
                            copyStatus.textContent = "Draft copied to clipboard.";
                        }} catch (error) {{
                            copyStatus.textContent = "Clipboard access was blocked by the browser.";
                        }}
                    }});
                </script>
                """,
                height=76,
        )


def main() -> None:
    st.set_page_config(page_title="Local Blog Generator", layout="wide")
    _init_state()
    _apply_styles()

    _render_hero()

    form_col, info_col = st.columns([1.35, 0.9], gap="large")

    with form_col:
        st.markdown(
            """
            <section class="surface-card">
                <div class="surface-title">Start a draft</div>
                <div class="surface-copy">Pick a provider, give it a precise angle, and generate the first version.</div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        with st.form("generator_form"):
            topic = st.text_input(
                "Topic",
                placeholder="Example: Why small businesses should document repeatable workflows",
            )
            provider = st.selectbox("Provider", ["cohere", "gemini"])
            generate_clicked = st.form_submit_button("Generate Draft")

    with info_col:
        st.markdown(
            """
            <section class="surface-card">
                <div class="surface-title">What makes a better prompt</div>
                <div class="surface-copy">
                    Narrow topics usually produce cleaner structure. Ask for a point of view, audience, or practical outcome rather than a broad subject.
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.last_saved_filename:
            st.success(f"Last saved: {st.session_state.last_saved_filename}")

    if generate_clicked:
        if not topic.strip():
            st.error("Please enter a topic")
        else:
            with st.spinner(f"Generating with {provider}..."):
                try:
                    generated = generate_with_provider(provider, topic.strip())
                    title, body = extract_title_and_body(generated)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.session_state.generated_title = title
                    st.session_state.generated_content = body
                    st.session_state.last_provider = provider

    if st.session_state.generated_content:
        st.markdown(
            f"""
            <section class="surface-card">
                <div class="surface-title">Draft workspace</div>
                <div class="surface-copy">Generated with {st.session_state.last_provider.title()}. Refine the copy, inspect the preview, then export the post when it is ready.</div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        title = st.text_input("Title", value=st.session_state.generated_title)
        content = st.text_area("Content (Markdown)", value=st.session_state.generated_content, height=440)

        word_count, heading_count, read_time = _content_metrics(title, content)
        stat_col_1, stat_col_2, stat_col_3 = st.columns(3, gap="medium")
        with stat_col_1:
            _metric_card("Word count", word_count, "A quick readout of current draft length.")
        with stat_col_2:
            _metric_card("Headings", heading_count, "Use sections to keep the article scannable.")
        with stat_col_3:
            _metric_card("Read time", read_time, "Estimated at roughly 200 words per minute.")

        save_col, copy_col, spacer_col = st.columns([0.22, 0.22, 0.56])
        with save_col:
            if st.button("Save to _posts", use_container_width=True):
                if not content.strip():
                    st.error("No content to save")
                else:
                    try:
                        filename = save_post(title.strip() or "Untitled", content.strip())
                    except Exception as exc:
                        st.error(str(exc))
                    else:
                        st.session_state.last_saved_filename = filename
                        st.success(f"Saved post: {filename}")

        with copy_col:
            _render_copy_button(title, content)

        editor_tab, preview_tab = st.tabs(["Editor", "Preview"])
        with editor_tab:
            st.markdown(
                """
                <section class="surface-card">
                    <div class="surface-title">Markdown notes</div>
                    <div class="surface-copy">Use <code>#</code> headings, short sections, bullet lists, and a clear conclusion to keep the draft easy to publish.</div>
                </section>
                """,
                unsafe_allow_html=True,
            )
            st.code(content or "", language="markdown")

        with preview_tab:
            st.markdown(
                """
                <section class="surface-card">
                    <div class="surface-title">Live preview</div>
                    <div class="surface-copy">This is how the post reads once the markdown structure is applied.</div>
                </section>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"# {title}" if title else "# Untitled")
            st.markdown(content)

        st.session_state.generated_title = title
        st.session_state.generated_content = content


if __name__ == "__main__":
    main()