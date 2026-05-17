import datetime
import os
import re


POSTS_DIR = os.path.join(os.getcwd(), "_posts")
os.makedirs(POSTS_DIR, exist_ok=True)


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def extract_title_and_body(generated: str):
    lines = generated.splitlines()
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
        title = first
        body = "\n".join(lines[1:]).lstrip()

    return title, body


def save_post(title: str, content: str, posts_dir: str = POSTS_DIR) -> str:
    date = datetime.date.today().isoformat()
    slug = slugify(title)
    filename = f"{date}-{slug}.md"
    path = os.path.join(posts_dir, filename)

    cleaned_title = title.replace('"', "'")
    front_matter = (
        f"---\nlayout: post\ntitle: \"{cleaned_title}\"\ndate: {date}\n---\n\n"
    )
    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(front_matter + content)

    return filename