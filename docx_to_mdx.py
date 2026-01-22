"""
Pipeline to convert Word documents to MDX pages and serve with Docusaurus.

1. Scans a folder for .docx files
2. Uses pandoc to convert to markdown
3. Splits markdown into pages based on H1 and H2 headers
4. Saves all files as .mdx with interactive component imports
5. Parses Mendeley references and generates structured reference data
6. Copies to Docusaurus docs folder
7. Builds and serves the site, opening in browser
"""

import json
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


# Configuration
INPUT_FOLDER = Path("report")
OUTPUT_FOLDER = Path("mdx")
DOCUSAURUS_DIR = Path("docusaurus-site")
DOCS_FOLDER = DOCUSAURUS_DIR / "docs"
REFERENCES_DATA_PATH = DOCUSAURUS_DIR / "src" / "data" / "references.ts"

# MDX imports for Docusaurus - using relative paths from @site
MDX_IMPORTS = """import Callout from '@site/src/components/interactive/Callout';
import Chart from '@site/src/components/interactive/Chart';
import DataTable from '@site/src/components/interactive/DataTable';
import InteractiveDemo from '@site/src/components/interactive/InteractiveDemo';
import CollapsibleSection from '@site/src/components/interactive/CollapsibleSection';
import QuoteBlock from '@site/src/components/interactive/QuoteBlock';
import RefPopup from '@site/src/components/RefPopup';

"""

# Simplified imports for pages without citations
MDX_IMPORTS_SIMPLE = """import Callout from '@site/src/components/interactive/Callout';
import Chart from '@site/src/components/interactive/Chart';
import DataTable from '@site/src/components/interactive/DataTable';
import InteractiveDemo from '@site/src/components/interactive/InteractiveDemo';
import CollapsibleSection from '@site/src/components/interactive/CollapsibleSection';
import QuoteBlock from '@site/src/components/interactive/QuoteBlock';

"""

# References page imports
MDX_IMPORTS_REFERENCES = """import ReferenceList from '@site/src/components/interactive/ReferenceList';
import { references } from '@site/src/data/references';

"""


def find_docx_files(folder: Path) -> list[Path]:
    """Scan folder for Word documents."""
    return list(folder.glob("*.docx"))


def convert_docx_to_md(docx_path: Path, extract_media_to: Path = None) -> str:
    """Use pandoc to convert Word document to markdown with media extraction."""
    cmd = ["pandoc", str(docx_path), "-t", "markdown", "--wrap=none"]

    # Extract media to specified folder
    if extract_media_to:
        extract_media_to.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--extract-media", str(extract_media_to)])

    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode("utf-8")


def slugify(text: str) -> str:
    """Convert header text to a valid filename slug."""
    text = re.sub(r"[*_`\[\]()#]", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text[:50] if text else "untitled"


def parse_reference_line(line: str) -> dict | None:
    """Parse a single Mendeley reference line into structured data.

    Mendeley references typically follow this pattern:
    Authors. Title. *Journal* Volume, Pages (Year) doi:XXX
    or for books:
    Authors. *Book Title*. (Publisher, Year)
    """
    # Match the reference number at the start
    num_match = re.match(r'^(\d+)\\?\.\s*', line)
    if not num_match:
        return None

    num = int(num_match.group(1))
    rest = line[num_match.end():]

    # Extract DOI if present
    doi = None
    doi_match = re.search(r'doi:(10\.\S+?)\.?(?:\s|$)', rest)
    if doi_match:
        doi = doi_match.group(1).rstrip('.')
        rest = rest[:doi_match.start()].strip()

    # Extract URL if present (for web references)
    url = None
    url_match = re.search(r'(https?://[^\s\)]+)', rest)
    if url_match:
        url = url_match.group(1).rstrip('.,')

    # Extract year - look for (YYYY) pattern
    year = None
    year_match = re.search(r'\((\d{4})\)', rest)
    if year_match:
        year = year_match.group(1)

    # Try to extract journal (in *italics*) - first occurrence
    journal = None
    journal_start = None  # Track the start position in 'rest'
    journal_end = None    # Track the end position in 'rest'
    journal_match = re.search(r'\*([^*]+)\*', rest)
    if journal_match:
        journal = journal_match.group(1)
        journal_start = journal_match.start()
        journal_end = journal_match.end()
        # Skip if this looks like "et al." which is author formatting
        if journal.lower() == 'et al.':
            # Look for next italic text as journal
            second_match = re.search(r'\*([^*]+)\*', rest[journal_end:])
            if second_match:
                journal = second_match.group(1)
                # Adjust positions to be relative to 'rest'
                journal_start = journal_end + second_match.start()
                journal_end = journal_end + second_match.end()

    # Extract volume and pages after journal
    volume = None
    pages = None
    if journal_end:
        after_journal = rest[journal_end:].strip()
        # Look for patterns like "38, 1--25" or "vol. 5" or just "1--28"
        vol_pages_match = re.match(r'(\d+)(?:,\s*|\s+)([\d\-–—]+)', after_journal)
        if vol_pages_match:
            volume = vol_pages_match.group(1)
            pages = vol_pages_match.group(2).replace('–', '-').replace('—', '-')
        else:
            # Try just pages
            pages_match = re.match(r'([\d\-–—]+)', after_journal)
            if pages_match:
                pages = pages_match.group(1).replace('–', '-').replace('—', '-')

    # Extract authors and title
    # Take text before the journal for author/title extraction
    if journal_start is not None:
        author_title_part = rest[:journal_start].strip()
    else:
        # No journal - take everything before year or URL
        if year_match:
            author_title_part = rest[:year_match.start()].strip()
        elif url_match:
            author_title_part = rest[:url_match.start()].strip()
        else:
            author_title_part = rest.strip()

    # Clean up trailing punctuation
    author_title_part = author_title_part.rstrip('. ')

    # Now split authors from title
    # Standard pattern: "LastName, F., LastName, F. & LastName, F. Title text here"
    # Authors section typically contains: commas, ampersand, initials (single caps with periods)

    authors = ""
    title = ""

    # Handle "et al." in authors
    et_al_match = re.search(r'(.*?\*et al\.\*)\s*(.+)', author_title_part)
    if et_al_match:
        authors = et_al_match.group(1).strip().rstrip('.')
        title = et_al_match.group(2).strip().rstrip('.')
    else:
        # Try to find the boundary between authors and title
        # Authors typically end with a period after an initial or after an ampersand section
        # Title typically starts with a capital letter

        # Pattern: Look for last author pattern (initial or name) followed by title
        # Common endings: "X. Y." or "& Name, I."
        author_end_patterns = [
            # Match: "Name, I. J. Title" or "Name, I. Title"
            r'^(.+?[A-Z]\.\s*[A-Z]?\.?)\s+([A-Z][a-z].+)$',
            # Match: "& Name, I. Title"
            r'^(.+?&\s+[^.]+\.)\s+([A-Z].+)$',
            # Match: "Name, I. & Name, J. Title"
            r'^(.+?[A-Z]\.)\s+([A-Z][a-z].+)$',
        ]

        found_split = False
        for pattern in author_end_patterns:
            match = re.match(pattern, author_title_part)
            if match:
                authors = match.group(1).strip().rstrip('.')
                title = match.group(2).strip().rstrip('.')
                found_split = True
                break

        if not found_split:
            # Fallback: use whole thing as combined author-title
            # This happens for non-standard formats
            title = author_title_part.rstrip('.')
            authors = ""

    # If we have journal but it looks like a book title (no authors found), swap
    if not authors and journal and not title:
        title = journal
        journal = None

    # Final cleanup
    title = title.rstrip('.')
    if not title and authors:
        title = authors
        authors = ""

    return {
        "num": num,
        "authors": authors,
        "title": title,
        "journal": journal,
        "year": year,
        "volume": volume,
        "pages": pages,
        "doi": doi,
        "url": url,
    }


def extract_references_from_markdown(markdown: str) -> list[dict]:
    """Extract all numbered references from the References section."""
    references = []

    # Find the References section
    ref_section_match = re.search(r'^#\s*References\s*$', markdown, re.MULTILINE)
    if not ref_section_match:
        return references

    ref_content = markdown[ref_section_match.end():]

    # Find numbered reference starts (1\. or just 1.)
    # Then capture everything until the next numbered reference or end
    ref_start_pattern = re.compile(r'^(\d+)\\?\.\s+', re.MULTILINE)

    starts = list(ref_start_pattern.finditer(ref_content))

    for i, match in enumerate(starts):
        start_pos = match.start()
        # End at next reference or end of content
        end_pos = starts[i + 1].start() if i + 1 < len(starts) else len(ref_content)

        # Extract full reference text and clean up
        full_ref = ref_content[start_pos:end_pos].strip()
        # Join multi-line references into single line
        full_ref = ' '.join(full_ref.split())
        # Convert Pandoc's --- back to em dash
        full_ref = full_ref.replace('---', '—')

        parsed = parse_reference_line(full_ref)
        if parsed:
            references.append(parsed)

    return references


def generate_references_typescript(references: list[dict], output_path: Path) -> None:
    """Generate a TypeScript file with references data."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ts_content = """// Auto-generated references data from Mendeley citations
// Do not edit manually - regenerate by running the conversion pipeline

export interface Reference {
  num: number;
  authors: string;
  title: string;
  journal?: string;
  year?: string;
  volume?: string;
  pages?: string;
  doi?: string;
  url?: string;
}

export const references: Reference[] = """

    # Convert to JSON with proper formatting
    refs_json = json.dumps(references, indent=2, ensure_ascii=False)
    ts_content += refs_json + ";\n"

    output_path.write_text(ts_content, encoding="utf-8")
    print(f"  Generated references data: {output_path}")


def convert_citations_in_content(content: str) -> tuple[str, bool]:
    """Check if content has citation markers.

    Returns tuple of (content, has_citations).
    Note: Citations are left as <sup> tags to be converted by post-processing.
    """
    has_citations = bool(re.search(r'<sup>\d+(?:[-–—,]\d+)*</sup>', content))

    # Return content unchanged - post-processing will convert to popups
    return content, has_citations


def split_markdown_by_headers(markdown: str) -> list[dict]:
    """Split markdown content by H1 and H2 headers."""
    header_pattern = re.compile(r"^(#{1,2})\s+(.+)$", re.MULTILINE)

    pages = []
    matches = list(header_pattern.finditer(markdown))

    if not matches:
        return [{
            "title": "Document",
            "level": 1,
            "slug": "document",
            "content": markdown.strip()
        }]

    first_match_start = matches[0].start()
    if first_match_start > 0:
        preamble = markdown[:first_match_start].strip()
        if preamble:
            pages.append({
                "title": "Introduction",
                "level": 1,
                "slug": "introduction",
                "content": preamble
            })

    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()
        slug = slugify(title)
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        content = markdown[content_start:content_end].strip()

        pages.append({
            "title": title,
            "level": level,
            "slug": slug,
            "content": content
        })

    return pages


def ensure_unique_slugs(pages: list[dict]) -> list[dict]:
    """Ensure all slugs are unique by appending numbers if needed."""
    seen = {}
    for page in pages:
        original_slug = page["slug"]
        slug = original_slug
        counter = 1
        while slug in seen:
            slug = f"{original_slug}-{counter}"
            counter += 1
        page["slug"] = slug
        seen[slug] = True
    return pages


def fix_mdx_syntax(content: str) -> str:
    """Fix common MDX syntax issues that cause compilation errors."""

    # Fix 1: Escape caret characters that look like malformed superscript
    # Pattern: [^digits^ should be escaped
    content = re.sub(r'\[\^(\d+)\^', r'[\\^\1\\^', content)

    # Fix standalone superscript patterns like ^11^, ^th^, ^xxix^, ^20--22^
    # Convert numeric citations to plain superscripts (tooltips added in post-processing)
    def convert_citation(match):
        citation = match.group(1)
        # Just convert to plain superscript - post-processing will add links and tooltips
        if re.match(r'^\d+', citation):
            return f'<sup>{citation}</sup>'
        else:
            return f'<sup>{citation}</sup>'

    content = re.sub(r'\^([\d\-\–\—,]+)\^', convert_citation, content)
    content = re.sub(r'\^([a-z]+)\^', r'<sup>\1</sup>', content)
    content = re.sub(r'\^([ivxlcdm]+)\^', r'<sup>\1</sup>', content)

    # Fix 2: Fix unescaped curly braces in text (common acorn error)
    # Remove Word document anchors like []{#_Ref123456 .anchor}
    content = re.sub(r'\[\]\{#[^}]+\}', '', content)

    # Escape {.mark}, {.underline} and similar patterns which are causing issues
    content = re.sub(r'\{\.mark\}', r'\\{.mark\\}', content)
    content = re.sub(r'\{\.underline\}', r'\\{.underline\\}', content)

    # Fix image attributes with curly braces - remove them entirely as they're not valid in MDX
    content = re.sub(r'\]\([^)]+\)\{[^}]+\}', lambda m: m.group(0).split('{')[0], content)

    # Fix image paths - use absolute path from site root for nested folders
    content = re.sub(r'\!\[([^\]]*)\]\(mdx/media/', r'![\1](/media/', content)
    content = re.sub(r'\!\[([^\]]*)\]\(media/', r'![\1](/media/', content)

    # Fix URLs in angle brackets - convert <https://...> to just the URL without brackets
    content = re.sub(r'<(https?://[^>]+)>', r'\1', content)

    # Fix 3: HTML comments need to be on their own line or use {/* */}
    # Replace <!-- with {/*
    content = re.sub(r'<!--', r'{/*', content)
    # Replace --> with */}
    content = re.sub(r'-->', r'*/}', content)

    return content


def create_mdx_content(page: dict, position: int, is_references_page: bool = False) -> str:
    """Create MDX file content with Docusaurus frontmatter and imports."""
    # Escape quotes in title for frontmatter
    safe_title = page['title'].replace('"', '\\"')

    # Use the slug as the explicit ID to prevent collisions from numeric filename prefixes
    doc_id = page['slug']

    # Compute reading time (approx 200 words per minute)
    words = len(re.findall(r'\w+', page['content']))
    reading_time = max(1, round(words / 200))

    # Frontmatter MUST come first in Docusaurus
    frontmatter = f"""---
title: "{safe_title}"
id: "{doc_id}"
sidebar_position: {position}
custom_edit_url: null
readingTimeMinutes: {reading_time}
---

"""
    header_prefix = "#" * page["level"]
    header_line = f"{header_prefix} {page['title']}\n\n"

    # Fix MDX syntax issues in the content
    fixed_content = fix_mdx_syntax(page["content"])

    # Handle references page specially
    if is_references_page:
        # Create a clean references page with the ReferenceList component
        return frontmatter + MDX_IMPORTS_REFERENCES + header_line + """
<ReferenceList references={references} />
"""

    # Convert citations to interactive components
    fixed_content, has_citations = convert_citations_in_content(fixed_content)

    # Choose imports based on whether page has citations
    imports = MDX_IMPORTS if has_citations else MDX_IMPORTS_SIMPLE

    # Correct order: frontmatter, imports, content
    return frontmatter + imports + header_line + fixed_content


def create_index_content(pages: list[dict]) -> str:
    """Create index.mdx file with links to all pages."""
    content = """---
title: "Multisensory Hub Report"
sidebar_position: 0
slug: /
---

import Callout from '@site/src/components/interactive/Callout';

# Multisensory Hub Report

<Callout type="info" title="Welcome">
Explore the science and practice of multisensory experiences. Use the sidebar to navigate through different sections.
</Callout>

## Contents

Use the sidebar to navigate through the report sections.
"""
    return content


def save_mdx_files(pages: list[dict], output_folder: Path) -> list[Path]:
    """Save pages as .mdx files with hierarchical folder structure.

    H1 sections become folders with collapsible categories.
    H2 sections become pages within those folders.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    created_files = []
    current_h1_folder = None
    current_h1_slug = None
    current_h1_position = 0
    h2_position = 0

    for i, page in enumerate(pages):
        is_references_page = page['slug'] == 'references' or page['title'].lower() == 'references'

        if page['level'] == 1:
            # H1: Create a new folder (category)
            current_h1_position += 1
            h2_position = 0
            current_h1_slug = page['slug']
            folder_name = f"{current_h1_position:02d}-{current_h1_slug}"
            current_h1_folder = output_folder / folder_name
            current_h1_folder.mkdir(parents=True, exist_ok=True)

            # Create _category_.json for collapsible sidebar
            category_meta = {
                "label": page['title'],
                "position": current_h1_position,
                "collapsible": True,
                "collapsed": False,
                "link": {
                    "type": "doc",
                    "id": f"{current_h1_slug}-overview"
                }
            }
            category_file = current_h1_folder / "_category_.json"
            category_file.write_text(json.dumps(category_meta, indent=2), encoding="utf-8")

            # Save H1 content as index.mdx in the folder (linked via _category_.json)
            # Create a modified page dict for the overview
            overview_page = page.copy()
            overview_page['title'] = page['title']  # Keep original title for the page
            # Use a globally unique ID by combining current H1 slug and overview
            overview_page['slug'] = f"{current_h1_slug}-overview"
            # Sidebar position 1 for the index page (though it will be hidden by Docusaurus if it's the category link)
            content = create_mdx_content(overview_page, 1, is_references_page=is_references_page)
            filepath = current_h1_folder / "index.mdx"
            filepath.write_text(content, encoding="utf-8")
            created_files.append(filepath)
            print(f"  Created: {folder_name}/index.mdx")

        else:
            # H2: Save inside current H1 folder
            h2_position += 1
            if current_h1_folder is None:
                # No H1 yet, save at root level
                filename = f"{i + 1:02d}-{page['slug']}.mdx"
                filepath = output_folder / filename
            else:
                filename = f"{h2_position:02d}-{page['slug']}.mdx"
                filepath = current_h1_folder / filename
                # Make the ID globally unique by prefixing with parent H1 slug (without slash)
                page['slug'] = f"{current_h1_slug}-{page['slug']}"

            content = create_mdx_content(page, h2_position, is_references_page=is_references_page)
            filepath.write_text(content, encoding="utf-8")
            created_files.append(filepath)
            print(f"  Created: {filepath.relative_to(output_folder)}")

    return created_files


def post_process_mdx_files(folder: Path) -> None:
    """Post-process MDX files to fix any remaining issues."""

    # First, load references from the intermediate markdown file
    references_map = {}
    md_file = OUTPUT_FOLDER / "Multisensory Hub_Jan26.md"
    if md_file.exists():
        md_content = md_file.read_text(encoding='utf-8')
        # Find the References section
        ref_section_match = re.search(r'^#\s*References\s*$(.+)', md_content, re.MULTILINE | re.DOTALL)
        if ref_section_match:
            ref_section = ref_section_match.group(1)
            # Match numbered references: "32\. Author text..."
            ref_matches = re.findall(r'(\d+)\\\. (.+?)(?=\n\d+\\\.|\Z)', ref_section, re.DOTALL)
            for num, text in ref_matches:
                clean_text = text.strip().replace('\n', ' ')[:300]
                references_map[num] = clean_text

    for mdx_file in folder.glob("**/*.mdx"):
        content = mdx_file.read_text(encoding="utf-8")
        original = content

        # Fix any remaining media paths to use absolute paths
        content = content.replace("mdx/media/", "/media/")
        content = re.sub(r'\]\(media/', r'](/media/', content)

        # Remove any remaining Word anchors
        content = re.sub(r'\[\]\{#[^}]+\}', '', content)

        # Convert existing <sup>number</sup> to reference popups with copy and navigation buttons
        def add_ref_popup(match):
            num = match.group(1)
            ref_text = references_map.get(num, f"Reference {num}")
            # Escape quotes for HTML/JSX attribute
            ref_text_escaped = ref_text.replace('"', '&quot;').replace("'", '&apos;').replace('{', '{{').replace('}', '}}')

            # Use RefPopup component
            popup_html = f'<RefPopup refNum="{num}" refText="{ref_text_escaped}" />'
            return popup_html

        content = re.sub(
            r'<sup>(\d+)</sup>',
            add_ref_popup,
            content
        )

        # Handle ranges like <sup>20-22</sup>
        def add_range_popup(match):
            nums = match.group(1)
            first_num = nums.split('-')[0].split('–')[0].split('—')[0]
            ref_text = references_map.get(first_num, f"References {nums}")
            ref_text_escaped = ref_text.replace('"', '&quot;').replace("'", '&apos;').replace('{', '{{').replace('}', '}}')
            return f'<RefPopup refNum="{nums}" refText="{ref_text_escaped}" />'

        content = re.sub(
            r'<sup>(\d+[-–\—]\d+)</sup>',
            add_range_popup,
            content
        )

        # Handle comma-separated like <sup>25,26</sup>
        def add_multi_popup(match):
            nums = match.group(1)
            first_num = nums.split(',')[0]
            ref_text = references_map.get(first_num, f"References {nums}")
            ref_text_escaped = ref_text.replace('"', '&quot;').replace("'", '&apos;').replace('{', '{{').replace('}', '}}')
            return f'<RefPopup refNum="{nums}" refText="{ref_text_escaped}" />'

        content = re.sub(
            r'<sup>(\d+,\d+)</sup>',
            add_multi_popup,
            content
        )

        # Special handling for references page - add anchor IDs
        if 'references' in mdx_file.name.lower():
            # Add anchor IDs to numbered references like "1. Author..."
            content = re.sub(
                r'^(\d+)\\\. ',
                r'<span id="ref-\1">\1.</span> ',
                content,
                flags=re.MULTILINE
            )

        # Fix frontmatter order - must come BEFORE imports
        # Pattern: imports... \n---\ntitle:... \n---\n
        if content.startswith("import ") and "---\ntitle:" in content:
            # Extract imports section (everything before first ---)
            imports_match = re.match(r'(import .*?\n\n)(---.*?---\n\n)(.*)', content, re.DOTALL)
            if imports_match:
                imports = imports_match.group(1)
                frontmatter = imports_match.group(2)
                rest = imports_match.group(3)
                # Reorder: frontmatter first, then imports, then content
                content = frontmatter + imports + rest

        if content != original:
            mdx_file.write_text(content, encoding="utf-8")
            print(f"    Post-processed: {mdx_file.name}")


def copy_to_docusaurus(source_folder: Path, docs_folder: Path) -> None:
    """Copy MDX files, folders, and media to Docusaurus docs folder."""
    # Clear existing docs
    if docs_folder.exists():
        # Only clear subdirectories and .md/.mdx/.json files to avoid deleting important docusaurus files if any
        # though we are in a dedicated docs folder
        shutil.rmtree(docs_folder)
    docs_folder.mkdir(parents=True, exist_ok=True)

    # Copy all content (folders, MDX files, JSON files) except media and intermediate .md files
    for item in source_folder.iterdir():
        if item.name == "media":
            continue
        if item.suffix == ".md":
            # Skip intermediate markdown files
            continue
        dest = docs_folder / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Copy media folder to static folder for absolute paths
    media_source = source_folder / "media"
    if media_source.exists():
        static_folder = docs_folder.parent / "static" / "media"
        if static_folder.exists():
            shutil.rmtree(static_folder)
        shutil.copytree(media_source, static_folder)
        print(f"  Copied media folder to {static_folder}")

    print(f"  Copied content to {docs_folder}")

    # Remove any leftover 01-overview.mdx files if they exist (from previous versions of the script)
    for overview_file in docs_folder.glob("**/01-overview.mdx"):
        overview_file.unlink()

    # Remove duplicates from docs folder
    for folder in docs_folder.iterdir():
        if folder.is_dir():
            seen_slugs = {}
            # Get all mdx files in the folder, sorted by name
            mdx_files = sorted(list(folder.glob("*.mdx")))
            for mdx_file in mdx_files:
                if mdx_file.name == "index.mdx":
                    continue
                # The filename format is XX-slug.mdx
                parts = mdx_file.stem.split('-', 1)
                if len(parts) > 1:
                    slug = parts[1]
                    if slug in seen_slugs:
                        # Duplicate found, delete the one with higher prefix number (later in sorted list)
                        print(f"    Removing duplicate: {mdx_file.relative_to(docs_folder)}")
                        mdx_file.unlink()
                    else:
                        seen_slugs[slug] = mdx_file

    # Post-process all MDX files in the docs folder
    print("  Post-processing MDX files...")
    post_process_mdx_files(docs_folder)


def start_docusaurus_server(docusaurus_dir: Path) -> subprocess.Popen:
    """Start the Docusaurus development server."""
    print("\n  Starting Docusaurus server...")

    # Use npm start for development
    # On Windows, we need shell=True and different handling
    if sys.platform == "win32":
        process = subprocess.Popen(
            "npm start",
            cwd=docusaurus_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
        )
    else:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=docusaurus_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    return process


def wait_for_server(url: str = "http://localhost:3000", timeout: int = 60) -> bool:
    """Wait for the server to be ready."""
    import urllib.request
    import urllib.error
    import socket

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=5)
            if response.status == 200:
                return True
        except (urllib.error.URLError, ConnectionRefusedError, socket.timeout, TimeoutError, OSError):
            time.sleep(2)
    return False


def process_document(docx_path: Path, output_folder: Path) -> list[dict]:
    """Process a single Word document through the pipeline."""
    print(f"\nProcessing: {docx_path}")

    print("  Converting to markdown with pandoc (extracting media)...")
    markdown = convert_docx_to_md(docx_path, extract_media_to=output_folder)

    md_path = output_folder / f"{docx_path.stem}.md"
    output_folder.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")
    print(f"  Saved intermediate markdown: {md_path.name}")

    # Extract and process references
    print("  Extracting references from Mendeley citations...")
    references = extract_references_from_markdown(markdown)
    if references:
        print(f"  Found {len(references)} references")
        generate_references_typescript(references, REFERENCES_DATA_PATH)
    else:
        print("  No references found (will use empty list)")
        # Generate empty references file to prevent import errors
        generate_references_typescript([], REFERENCES_DATA_PATH)

    print("  Splitting by H1 and H2 headers...")
    pages = split_markdown_by_headers(markdown)
    pages = ensure_unique_slugs(pages)
    print(f"  Found {len(pages)} sections")

    print("  Saving MDX files...")
    save_mdx_files(pages, output_folder)

    # Create index
    index_content = create_index_content(pages)
    index_path = output_folder / "index.mdx"
    index_path.write_text(index_content, encoding="utf-8")
    print(f"  Created: index.mdx")

    return pages


def main():
    """Main entry point for the pipeline."""
    print("=" * 60)
    print("Word to MDX + Docusaurus Pipeline")
    print("=" * 60)

    # Check pandoc
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        print(f"Using pandoc: {result.stdout.decode().split(chr(10))[0]}")
    except FileNotFoundError:
        print("ERROR: pandoc not found. Please install pandoc first.")
        print("  https://pandoc.org/installing.html")
        sys.exit(1)

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, check=True, shell=True)
        print(f"Using npm: v{result.stdout.decode().strip()}")
    except FileNotFoundError:
        print("ERROR: npm not found. Please install Node.js first.")
        sys.exit(1)

    # Find Word documents
    docx_files = find_docx_files(INPUT_FOLDER)
    if not docx_files:
        print(f"\nNo .docx files found in {INPUT_FOLDER}/")
        sys.exit(0)

    print(f"\nFound {len(docx_files)} Word document(s) in {INPUT_FOLDER}/")

    # Process each document
    for docx_path in docx_files:
        process_document(docx_path, OUTPUT_FOLDER)

    # Copy to Docusaurus
    print("\n" + "-" * 60)
    print("Deploying to Docusaurus...")
    copy_to_docusaurus(OUTPUT_FOLDER, DOCS_FOLDER)

    # Test build first
    print("\n" + "-" * 60)
    print("Testing build...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=DOCUSAURUS_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=True
        )
        if result.returncode != 0:
            print("\n⚠️  Build completed with errors:")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            print("\nYou can still start the dev server to see partial results.")
            response = input("\nContinue to start dev server? (y/n): ").lower()
            if response != 'y':
                print("Exiting.")
                sys.exit(1)
        else:
            print("[OK] Build successful!")
    except subprocess.TimeoutExpired:
        print("Build timed out, but continuing...")

    # Start Docusaurus server
    print("\n" + "-" * 60)
    print("Starting Docusaurus development server...")

    server_process = start_docusaurus_server(DOCUSAURUS_DIR)

    # Wait for server (Docusaurus will auto-open browser)
    print("  Waiting for server to be ready...")
    url = "http://localhost:3000"

    if wait_for_server(url, timeout=90):
        print(f"\n  Server ready at {url}")
        # Don't open browser manually - Docusaurus will auto-open
        print("\n" + "=" * 60)
        print("SUCCESS! Your report is now live at:", url)
        print("Press Ctrl+C to stop the server.")
        print("=" * 60)

        # Keep running until interrupted
        try:
            while True:
                line = server_process.stdout.readline()
                if line:
                    print(f"  [Docusaurus] {line.strip()}")
                if server_process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            server_process.terminate()
    else:
        print("\n  ERROR: Server failed to start within timeout.")
        server_process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
