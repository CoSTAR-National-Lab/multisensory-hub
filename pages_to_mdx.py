"""
Standalone throwaway script: convert report/other_pages/pages.docx into
individual Docusaurus pages (src/pages/<slug>.mdx).

Each Word Title-style paragraph becomes one page. python-docx is used to
detect Title-styled paragraphs (pandoc loses this style information).
Images are copied to static/media/subpages/<slug>/.
CSS is inherited from the site's global custom.css automatically.

Do NOT merge this into docx_to_mdx.py.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document as DocxDocument

DOCX_PATH    = Path("report/other_pages/pages.docx")
PAGES_OUT    = Path("docusaurus-site/src/pages")
STATIC_MEDIA = Path("docusaurus-site/static/media/subpages")
TMP_MEDIA    = Path("_tmp_subpage_media")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = re.sub(r"[*_`\[\]()#]", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:50] or "untitled"


def get_page_titles(docx_path: Path) -> list[str]:
    """Use python-docx to find Title-styled paragraphs in order."""
    doc = DocxDocument(str(docx_path))
    return [p.text.strip() for p in doc.paragraphs
            if p.style.name == "Title" and p.text.strip()]


def run_pandoc(docx_path: Path, media_dir: Path) -> str:
    media_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pandoc", str(docx_path),
        "-t", "markdown+pipe_tables-simple_tables-multiline_tables-grid_tables",
        "--wrap=none",
        "--extract-media", str(media_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode("utf-8").replace("\r\n", "\n")


def split_pages(md: str, titles: list[str]) -> list[tuple[str, str]]:
    """
    Split markdown into (title, body) pairs using known Title-style text.

    Pandoc puts the first Title in metadata (invisible in content) and
    renders subsequent Titles as plain paragraphs in the markdown body.
    """
    if not titles:
        return []

    sections = []
    remaining = md

    for i, title in enumerate(titles[:-1]):
        next_title = titles[i + 1]
        # Subsequent titles appear as a standalone paragraph line
        pattern = re.compile(
            r'\n\n' + re.escape(next_title) + r'\n\n',
            re.MULTILINE,
        )
        m = pattern.search(remaining)
        if m:
            body = remaining[:m.start()].strip()
            sections.append((title, body))
            remaining = remaining[m.end():].strip()
        else:
            sections.append((title, remaining.strip()))
            remaining = ""

    sections.append((titles[-1], remaining.strip()))
    return sections


def fix_image_syntax(body: str) -> str:
    """Remove pandoc's {width=... height=...} attributes after image links."""
    return re.sub(r'(!\[[^\]]*\]\([^)]+\))\{[^}]*\}', r'\1', body)


def copy_images_and_rewrite(body: str, slug: str) -> str:
    """Copy extracted images to static/media/subpages/<slug>/ and fix paths."""
    dest_dir = STATIC_MEDIA / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    def replace(m):
        alt = m.group(1)
        src = m.group(2)
        img_src = Path(src)
        if not img_src.is_absolute():
            img_src = Path.cwd() / img_src
        if img_src.exists():
            shutil.copy2(img_src, dest_dir / img_src.name)
            new_src = f"/media/subpages/{slug}/{img_src.name}"
        else:
            new_src = src
        return f"![{alt}]({new_src})"

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace, body)


def make_mdx(title: str, body: str) -> str:
    return f"""---
title: "{title}"
---

# {title}

{body}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not DOCX_PATH.exists():
        print(f"ERROR: {DOCX_PATH} not found")
        sys.exit(1)

    titles = get_page_titles(DOCX_PATH)
    if not titles:
        print("No Title-styled paragraphs found in the document.")
        sys.exit(0)
    print(f"Found Title pages: {titles}")

    if TMP_MEDIA.exists():
        shutil.rmtree(TMP_MEDIA)

    print(f"Converting {DOCX_PATH} with pandoc...")
    try:
        md = run_pandoc(DOCX_PATH, TMP_MEDIA)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: pandoc failed:\n{e.stderr.decode()}")
        sys.exit(1)

    pages = split_pages(md, titles)
    print(f"Generating {len(pages)} page(s)...")
    PAGES_OUT.mkdir(parents=True, exist_ok=True)

    for title, body in pages:
        slug = slugify(title)
        body = fix_image_syntax(body)
        body = copy_images_and_rewrite(body, slug)
        content = make_mdx(title, body)
        out_path = PAGES_OUT / f"{slug}.mdx"
        out_path.write_text(content, encoding="utf-8")
        print(f"  -> {out_path}")

    shutil.rmtree(TMP_MEDIA, ignore_errors=True)
    print("Done.")


if __name__ == "__main__":
    main()
