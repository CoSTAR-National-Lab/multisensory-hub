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
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


def _c_error(msg: str) -> None:
    print(f"{Fore.RED}{Style.BRIGHT}{msg}{Style.RESET_ALL}")

def _c_warn(msg: str) -> None:
    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")

def _c_ok(msg: str) -> None:
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")

def _c_info(msg: str) -> None:
    print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")


# Configuration
INPUT_FOLDER = Path("report")
OUTPUT_FOLDER = Path("mdx")
DOCUSAURUS_DIR = Path("docusaurus-site")
DOCS_FOLDER = DOCUSAURUS_DIR / "docs"
REFERENCES_DATA_PATH = DOCUSAURUS_DIR / "src" / "data" / "references.ts"

# SharePoint download config — set these to enable automatic fetching.
# Defaults to the well-known Azure CLI public client (no app registration needed).
# Set SHAREPOINT_FETCH=0 to skip the download step entirely.
SHAREPOINT_FETCH     = os.environ.get("SHAREPOINT_FETCH", "0") != "0"
SHAREPOINT_CLIENT_ID = os.environ.get("SHAREPOINT_CLIENT_ID", "04b07795-8542-4462-a58f-a12c68021efc")
SHAREPOINT_TENANT_ID = os.environ.get("SHAREPOINT_TENANT_ID", "rhul.ac.uk")
# Drive item ID from the SharePoint URL (the d=w<id> parameter, without the leading 'w')
SHAREPOINT_ITEM_ID   = os.environ.get("SHAREPOINT_ITEM_ID", "33cce5b6dafa485eac746bc64f20aed8")
SHAREPOINT_DEST_NAME = os.environ.get("SHAREPOINT_DEST_NAME", "Multisensory_Hub_April.docx")
# Token cache file so you only log in once
TOKEN_CACHE_PATH = Path(".sharepoint_token_cache.json")

# MDX imports for Docusaurus - using relative paths from @site
MDX_IMPORTS = """import Callout from '@site/src/components/interactive/Callout';
import Chart from '@site/src/components/interactive/Chart';
import DataTable from '@site/src/components/interactive/DataTable';
import InteractiveDemo from '@site/src/components/interactive/InteractiveDemo';
import CollapsibleSection from '@site/src/components/interactive/CollapsibleSection';
import QuoteBlock from '@site/src/components/interactive/QuoteBlock';
import LatencyChart from '@site/src/components/interactive/LatencyChart';
import RefPopup from '@site/src/components/RefPopup';
import TrackedBlock from '@site/src/components/interactive/TrackedBlock';

"""

# Simplified imports for pages without citations
MDX_IMPORTS_SIMPLE = """import Callout from '@site/src/components/interactive/Callout';
import Chart from '@site/src/components/interactive/Chart';
import DataTable from '@site/src/components/interactive/DataTable';
import InteractiveDemo from '@site/src/components/interactive/InteractiveDemo';
import CollapsibleSection from '@site/src/components/interactive/CollapsibleSection';
import QuoteBlock from '@site/src/components/interactive/QuoteBlock';
import LatencyChart from '@site/src/components/interactive/LatencyChart';
import TrackedBlock from '@site/src/components/interactive/TrackedBlock';

"""

# References page imports
MDX_IMPORTS_REFERENCES = """import ReferenceList from '@site/src/components/interactive/ReferenceList';
import { references } from '@site/src/data/references';

"""


# Global list to collect all pipeline warnings (shown en masse at the end)
WARNINGS = []


def fetch_from_sharepoint() -> bool:
    """Download the report docx from SharePoint via Microsoft Graph API.

    Uses MSAL interactive (device-code) auth with a persistent token cache so
    the user only needs to log in once.  Returns True if a file was downloaded,
    False if the step was skipped (no credentials configured).
    """
    if not SHAREPOINT_FETCH or not SHAREPOINT_CLIENT_ID or not SHAREPOINT_TENANT_ID:
        return False

    try:
        import msal
        import requests as http_requests
    except ImportError:
        _c_warn("  [SharePoint] msal/requests not installed — run: pip install msal requests")
        return False

    # ------------------------------------------------------------------
    # Build a token cache backed by a local file
    # ------------------------------------------------------------------
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))

    app = msal.PublicClientApplication(
        SHAREPOINT_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{SHAREPOINT_TENANT_ID}",
        token_cache=cache,
    )

    scopes = ["https://graph.microsoft.com/Files.Read"]

    # Try silent first (uses cached token / refresh token)
    accounts = app.get_accounts()
    result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None

    if not result:
        # Use device code flow: prints a URL + code you open in any browser.
        # This works even when interactive/redirect flows are blocked by Conditional Access.
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            _c_error(f"  [SharePoint] Could not start device flow: {flow}")
            return False
        print("\n" + "=" * 60)
        print("  SharePoint login required.")
        print(f"  1. Open:  {flow['verification_uri']}")
        print(f"  2. Enter: {flow['user_code']}")
        print("  3. Sign in with your RHUL account")
        print("=" * 60)
        result = app.acquire_token_by_device_flow(flow)  # blocks until login complete

    # Persist updated cache
    if cache.has_state_changed:
        TOKEN_CACHE_PATH.write_text(cache.serialize(), encoding="utf-8")

    if "access_token" not in result:
        _c_error(f"  [SharePoint] Auth failed: {result.get('error_description', result)}")
        return False

    token = result["access_token"]

    # ------------------------------------------------------------------
    # Download the file via Graph API
    # ------------------------------------------------------------------
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{SHAREPOINT_ITEM_ID}/content"
    print(f"  [SharePoint] Downloading item {SHAREPOINT_ITEM_ID}...")
    resp = http_requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)

    if resp.status_code == 200:
        dest = INPUT_FOLDER / SHAREPOINT_DEST_NAME
        INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)
        _c_ok(f"  [SharePoint] Saved {len(resp.content) // 1024} KB → {dest}")
        return True

    # If /me/drive doesn't work the file may be on a SharePoint site drive;
    # fall back to the shares/driveItem endpoint using the encoded sharing URL.
    if resp.status_code in (400, 403, 404):
        _c_warn(f"  [SharePoint] /me/drive returned {resp.status_code}, trying shares endpoint...")
        import base64
        sharing_url = (
            "https://rhul.sharepoint.com/:w:/r/sites/StoryFutures/Shared%20Documents/"
            "CoSTAR/R%26D/Users/Multisensory%20Pillar/"
            "Multisensory%20Hub_April.docx"
        )
        # Graph API encodes the URL as unpadded base64 with u! prefix
        encoded = base64.urlsafe_b64encode(sharing_url.encode()).rstrip(b"=").decode()
        share_id = "u!" + encoded
        url2 = f"https://graph.microsoft.com/v1.0/shares/{share_id}/driveItem/content"
        resp2 = http_requests.get(url2, headers={"Authorization": f"Bearer {token}"}, timeout=60)
        if resp2.status_code == 200:
            dest = INPUT_FOLDER / SHAREPOINT_DEST_NAME
            INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp2.content)
            _c_ok(f"  [SharePoint] Saved {len(resp2.content) // 1024} KB → {dest}")
            return True
        _c_error(f"  [SharePoint] shares endpoint returned {resp2.status_code}: {resp2.text[:200]}")

    _c_error(f"  [SharePoint] Download failed ({resp.status_code}): {resp.text[:200]}")
    return False


def find_docx_files(folder: Path) -> list[Path]:
    """Scan folder for Word documents, excluding temporary owner files."""
    return [f for f in folder.glob("*.docx") if not f.name.startswith("~$")]


def convert_docx_to_md(docx_path: Path, extract_media_to: Path = None) -> str:
    """Use pandoc to convert Word document to markdown with media extraction."""
    # Disable simple/multiline/grid table formats so Pandoc always outputs pipe
    # tables (|col|col|), which extract_chart_data_tables can parse reliably.
    cmd = ["pandoc", str(docx_path),
           "-t", "markdown+pipe_tables-simple_tables-multiline_tables-grid_tables",
           "--wrap=none"]

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


def _find_page_for_position(markdown: str, pages: list[dict], char_position: int) -> int:
    """Map a character position in the full markdown to a page index.

    Reconstructs the H1/H2 split boundaries from the original markdown
    to determine which page a given character offset falls within.
    """
    header_pattern = re.compile(r"^(#{1,2})\s+(.+)$", re.MULTILINE)
    matches = list(header_pattern.finditer(markdown))

    if not matches:
        return 0

    # Build boundaries: each page corresponds to a range [start, end) in the markdown
    boundaries = []
    first_match_start = matches[0].start()

    # Preamble (content before first header)
    if first_match_start > 0:
        preamble = markdown[:first_match_start].strip()
        if preamble:
            boundaries.append((0, first_match_start))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        boundaries.append((start, end))

    # Find which boundary range the position falls in
    for page_idx, (start, end) in enumerate(boundaries):
        if start <= char_position < end:
            return page_idx

    # Fallback: last page
    return len(boundaries) - 1


def collect_anchor_registry(markdown: str, pages: list[dict]) -> dict:
    """Scan the full markdown for anchor targets and map each to its final page.

    Collects:
    - Word _Ref anchors: []{#_Ref205972686 .anchor}
    - H3/H4/H5/H6 heading slugs (auto-generated fragment targets)

    Returns dict: anchor_id -> {page_index, page_slug, fragment, page_level}
    """
    registry = {}

    # Collect _Ref anchors
    ref_pattern = re.compile(r'\[\]\{#(_Ref\d+)\s+\.anchor\}')
    for match in ref_pattern.finditer(markdown):
        anchor_id = match.group(1)
        page_idx = _find_page_for_position(markdown, pages, match.start())
        if page_idx < len(pages):
            registry[anchor_id] = {
                'page_index': page_idx,
                'page_slug': pages[page_idx]['slug'],
                'fragment': anchor_id,
                'page_level': pages[page_idx]['level'],
            }

    # Collect H3-H6 heading slugs (these are sub-headings within pages)
    heading_pattern = re.compile(r'^(#{3,6})\s+(.+)$', re.MULTILINE)
    for match in heading_pattern.finditer(markdown):
        heading_text = match.group(2).strip()
        heading_slug = slugify(heading_text)
        page_idx = _find_page_for_position(markdown, pages, match.start())
        if page_idx < len(pages):
            registry[heading_slug] = {
                'page_index': page_idx,
                'page_slug': pages[page_idx]['slug'],
                'fragment': heading_slug,
                'page_level': pages[page_idx]['level'],
            }

    # Also register H2 heading slugs (they become separate pages, fragment is empty)
    h2_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)
    for match in h2_pattern.finditer(markdown):
        heading_text = match.group(1).strip()
        heading_slug = slugify(heading_text)
        page_idx = _find_page_for_position(markdown, pages, match.start())
        if page_idx < len(pages):
            registry[heading_slug] = {
                'page_index': page_idx,
                'page_slug': pages[page_idx]['slug'],
                'fragment': '',  # H2 is the page itself, no fragment needed
                'page_level': pages[page_idx]['level'],
            }

    return registry


def build_page_url_map(pages: list[dict]) -> dict:
    """Map each page index to its Docusaurus URL path.

    Mirrors the routing logic in save_mdx_files() and Docusaurus folder-based
    routing with routeBasePath: '/':
    - Pre-H1 content / first H1 -> '/'
    - Subsequent H1s -> '/<h1slug>/<doc-id>' (category link page)
    - H2s before first H1 -> '/' (merged into homepage)
    - H2s after an H1 -> '/<h1slug>/<h1slug-h2slug>'
    """
    url_map = {}
    found_first_h1 = False
    current_h1_slug = None
    current_h1_position = 0

    for i, page in enumerate(pages):
        if page['level'] == 1:
            if not found_first_h1:
                found_first_h1 = True
                url_map[i] = '/'
            else:
                current_h1_position += 1
                current_h1_slug = page['slug']
                # H1 overview pages are linked via _category_.json which makes
                # the category URL serve the doc, so the URL is just /<h1-slug>
                url_map[i] = f'/{current_h1_slug}'
        else:
            # H2
            if not found_first_h1:
                # Pre-H1 H2s are merged into homepage
                url_map[i] = '/'
            else:
                if current_h1_slug:
                    url_map[i] = f'/{current_h1_slug}/{page["slug"]}'
                else:
                    url_map[i] = f'/{page["slug"]}'

    return url_map


def build_title_link_registry(markdown: str, pages: list[dict], url_map: dict) -> dict:
    """Map every heading's display text (case-insensitive) to its full Docusaurus URL.

    H1 / H2 headings  → page URL (no fragment)
    H3 – H6 headings  → page URL + '#' + slug fragment

    Returns dict: stripped_lowercase_text -> url_string
    """
    registry = {}
    fmt = re.compile(r'[*_`\[\]()\\]')

    def clean(text: str) -> str:
        return fmt.sub('', text).lower().strip()

    # H1 / H2 pages → their page URL
    for i, page in enumerate(pages):
        url = url_map.get(i, '/')
        registry[clean(page['title'])] = url

    # H3–H6 sub-headings → page URL + fragment
    sub_heading = re.compile(r'^(#{3,6})\s+(.+)$', re.MULTILINE)
    for match in sub_heading.finditer(markdown):
        heading_text = match.group(2).strip()
        heading_slug = slugify(heading_text)
        page_idx = _find_page_for_position(markdown, pages, match.start())
        if page_idx < len(pages):
            url = url_map.get(page_idx, '/')
            registry[clean(heading_text)] = f'{url}#{heading_slug}'

    return registry


def resolve_bare_title_links(content: str, title_registry: dict) -> tuple[str, list[str]]:
    """Replace [Title] references with Docusaurus links where the title matches a heading.

    Skips:
    - Image alt text  ``![Alt](...)``
    - Existing links  ``[text](url)``  or  ``[text][ref]``
    - Content inside fenced code blocks or inline code spans

    Returns:
        new_content  – content with matched titles converted to links
        unresolved   – de-duplicated list of texts that had no matching heading
    """
    # Unescape pandoc bracket escaping (\[ → [ and \] → ]) before matching,
    # so bare links written as \[Title\] in the pandoc output are still found.
    content = content.replace('\\[', '[').replace('\\]', ']')

    fmt = re.compile(r'[*_`\[\]()\\]')
    bare_link = re.compile(r'(?<!!)\[([^\]\n]+)\](?!\(|\[)')
    code_block = re.compile(r'(```[\s\S]*?```|`[^`\n]+`)')

    unresolved: list[str] = []
    seen: set[str] = set()

    def replace(match: re.Match) -> str:
        text = match.group(1)
        # Format: [Title to search: label to display]
        # The part before the colon is used to find the heading in the registry.
        # The part after the colon is used as the button label.
        # If there is no colon, the full text is used for both.
        if ':' in text:
            search_text, label = text.split(':', 1)
            search_text = search_text.strip()
            label = label.strip()
        else:
            search_text = text
            label = text
        key = fmt.sub('', search_text).lower().strip()
        if key not in title_registry:
            # Fall back to the full text as the key — handles headings whose title
            # contains a colon (e.g. "Case study: Arcade") where the colon is
            # structural rather than a search/label separator.
            full_key = fmt.sub('', text).lower().strip()
            if full_key in title_registry:
                key = full_key
        if key in title_registry:
            url = title_registry[key]
            return f'<a href="{url}" className="button button--secondary button--sm">{label}</a>'
        if key not in seen:
            seen.add(key)
            unresolved.append(text)
        return match.group(0)

    # Split on code blocks (capturing group keeps delimiters in the list)
    segments = code_block.split(content)
    new_parts = []
    for j, segment in enumerate(segments):
        if j % 2 == 0:
            new_parts.append(bare_link.sub(replace, segment))
        else:
            new_parts.append(segment)  # leave code verbatim

    return ''.join(new_parts), unresolved


def rewrite_internal_links(content: str, page_index: int, anchor_registry: dict, url_map: dict) -> str:
    """Rewrite [text](#fragment) links to point to the correct cross-page URL.

    For each internal link:
    - If target is on the same page: leave as-is
    - If target is on a different page: rewrite to [text](/page-url#fragment)
    - If target is unknown: leave unchanged
    """
    def replace_link(match):
        full_match = match.group(0)
        link_text = match.group(1)
        fragment = match.group(2)

        # Look up the fragment in the anchor registry
        if fragment not in anchor_registry:
            return full_match

        target_info = anchor_registry[fragment]
        target_page_idx = target_info['page_index']

        # Same page - leave as-is
        if target_page_idx == page_index:
            return full_match

        # Different page - rewrite with cross-page URL
        target_url = url_map.get(target_page_idx, '/')
        target_fragment = target_info['fragment']
        if target_fragment:
            return f'[{link_text}]({target_url}#{target_fragment})'
        else:
            return f'[{link_text}]({target_url})'

    # Match markdown links with fragment-only targets: [text](#fragment)
    # Also handles [text](#fragment) where text may contain nested brackets
    pattern = re.compile(r'\[([^\]]*)\]\(#([^)]+)\)')
    return pattern.sub(replace_link, content)


def replace_top_level_headings_placeholder(content: str, pages: list[dict], url_map: dict) -> str:
    """Replace [top-level headings] with a markdown list of clickable H1 section links.

    Skips the first H1 (homepage, url '/') and any References section.
    """
    if '[top-level headings]' not in content:
        return content

    links = []
    for i, page in enumerate(pages):
        if page['level'] != 1:
            continue
        url = url_map.get(i, '')
        if not url or url == '/':
            continue  # skip homepage
        title = page['title'].replace('\\', '')
        if title.lower().startswith('reference'):
            continue
        links.append(f'- [{title}]({url})')

    replacement = '\n'.join(links)
    return content.replace('[top-level headings]', replacement)


def preserve_ref_anchors(content: str) -> str:
    """Convert Word _Ref anchors to HTML span elements before fix_mdx_syntax strips them.

    Converts []{#_Ref... .anchor} to <span id="_Ref..."></span>
    Special handling: when anchors appear inside image alt text (![...]),
    the span is placed before the image to avoid invalid MDX.
    """
    # Handle anchors inside image markup: ![...[]{#_Ref... .anchor}...](...)
    # Place the anchor on its own line before the image
    content = re.sub(
        r'(!\[)\[\]\{#(_Ref\d+)\s+\.anchor\}',
        r'<span id="\2"></span>\n\n\1',
        content
    )

    # Handle remaining standalone anchors: []{#_RefNNNNN .anchor}
    content = re.sub(
        r'\[\]\{#(_Ref\d+)\s+\.anchor\}',
        r'<span id="\1"></span>',
        content
    )

    # Clean up any remaining anchor attributes (e.g. inside other contexts)
    content = re.sub(
        r'\{#(_Ref\d+)\s+\.anchor\}',
        r'',
        content
    )

    return content


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

    # Remove Pandoc attributes entirely (instead of escaping them)
    # These are Word formatting artifacts that leave visible remnants
    content = re.sub(r'\{\.mark\}', '', content)
    content = re.sub(r'\{\.underline\}', '', content)

    # Fix image attributes with curly braces - remove them entirely as they're not valid in MDX
    content = re.sub(r'\]\([^)]+\)\{[^}]+\}', lambda m: m.group(0).split('{')[0], content)

    # Fix image paths - use absolute path from site root for nested folders
    content = re.sub(r'\!\[([^\]]*)\]\(mdx/media/', r'![\1](/media/', content)
    content = re.sub(r'\!\[([^\]]*)\]\(media/', r'![\1](/media/', content)

    # Action 12: Flag missing or generic alt text
    generic_patterns = [
        "A picture", "A screenshot", "A close up", "A group of",
        "image", "Image", "graphic", "Graphic", "figure", "Figure"
    ]
    img_pattern = re.compile(r'\!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)]+)\)')
    for img_match in img_pattern.finditer(content):
        alt_text = img_match.group(1).strip()
        img_path = img_match.group(2)

        is_generic = False
        reason = ""

        if not alt_text:
            is_generic = True
            reason = "missing (empty)"
        elif len(alt_text) < 5:
            is_generic = True
            reason = f"too short (\"{alt_text}\")"
        else:
            for pattern in generic_patterns:
                if alt_text.lower().startswith(pattern.lower()):
                    is_generic = True
                    reason = f"generic (starts with \"{pattern}\")"
                    break

        if is_generic:
            # Try to get figure number from the alt text itself
            fig_match = re.match(r'^(Figure\s+\d+)', alt_text, re.IGNORECASE) if alt_text else None
            if not fig_match:
                # Fall back: look at content within ~200 chars after the image for "Figure N"
                lookahead = content[img_match.end():img_match.end() + 200]
                fig_match = re.search(r'(Figure\s+\d+)', lookahead, re.IGNORECASE)
            fig_label = f" [{fig_match.group(1)}]" if fig_match else ""
            msg = f"[A11y] Image{fig_label} {img_path} has {reason} alt text. Consider adding a descriptive alt in Word."
            if msg not in WARNINGS:
                WARNINGS.append(msg)

    # Extract Figure N: captions from image alt text and render as visible <figcaption>
    # Keeps alt text intact for accessibility; adds figcaption for sighted readers
    def add_figure_caption(match):
        alt = match.group(1).strip()
        src = match.group(2)
        if re.match(r'^Figure\s+\d+[:.]\s*', alt, re.IGNORECASE):
            # Alt text may contain markdown links [text](url); convert to <a> tags
            # so the figcaption is valid JSX (raw markdown links break MDX parsing)
            caption = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', alt)
            return f'![{alt}]({src})\n\n<figcaption>{caption}</figcaption>'
        return match.group(0)

    # Allow one level of bracket nesting in alt text (e.g. [link text](url) inside alt)
    content = re.sub(r'!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)]+)\)', add_figure_caption, content)

    # Convert Pandoc paragraph captions (`: text` after an image) to <figcaption>
    # so they share styling with the LatencyChart figcaption
    content = re.sub(
        r'(!\[[^\]]*\]\([^)]+\))\n\n^: (.+)$',
        lambda m: m.group(1) + '\n\n<figcaption>' + m.group(2).strip() + '</figcaption>',
        content,
        flags=re.MULTILINE
    )

    # Fix URLs in angle brackets - convert <https://...> to just the URL without brackets
    content = re.sub(r'<(https?://[^>]+)>', r'\1', content)

    # Fix backslashes escaping brackets in content (common in Pandoc output)
    content = content.replace('\\[', '[').replace('\\]', ']')

    # Fix 3: HTML comments FIRST (before dash normalization to avoid corrupting <!--)
    # Replace <!-- --> with {/* */}
    content = re.sub(r'<!--', r'{/*', content)
    content = re.sub(r'-->', r'*/}', content)

    # STEP: Normalize dashes AFTER HTML comment conversion
    # Protect -- inside HTML/JSX tags (e.g. className="button--sm") before normalising,
    # then restore afterwards so JSX attributes are never mangled.
    _html_tag = re.compile(r'<[^>]+>')
    _DD = '\x00DD\x00'
    content = _html_tag.sub(lambda m: m.group(0).replace('--', _DD), content)

    # Em-dash: --- to — (but not at line start which could be frontmatter delimiter)
    # Only convert --- that's surrounded by word characters or spaces (not line-initial)
    content = re.sub(r'(?<=\w)---(?=\w)', '—', content)
    content = re.sub(r'(?<=\w)---(?=\s)', '—', content)
    content = re.sub(r'(?<=\s)---(?=\w)', '—', content)
    content = re.sub(r'(?<=\s)---(?=\s)', '—', content)

    # For compound words (letter--letter), use regular hyphen (e.g., high--speed -> high-speed)
    content = re.sub(r'([a-zA-Z])--([a-zA-Z])', r'\1-\2', content)

    # For number ranges (digit--digit), use en-dash (e.g., 20--22 -> 20–22)
    content = re.sub(r'(\d)--(\d)', r'\1–\2', content)

    # Any remaining -- becomes en-dash (but not part of --- or inside JSX comments {/* */})
    content = re.sub(r'(?<!-)--(?!-)', '–', content)

    # Restore double-dashes protected inside HTML/JSX tags
    content = content.replace(_DD, '--')

    # Fix 4: Clean up bold and italic marker artifacts
    # Preserve legitimate **text** and *text* formatting for rendering

    def clean_formatting(text):
        # Fix " --**" at end of lines (artifact from pandoc)
        text = re.sub(r' --\*\*(\s|$)', r' --\1', text)

        # Note: Removed the ":**" fix as it was incorrectly removing valid closing bold markers
        # The pattern `:**` followed by space is often a legitimate bold closer like "**Title:**"

        # Fix leading whitespace inside bold-italic markers: "*** text***" -> "***text***"
        # Must run before ** and * fixes to avoid partial matches.
        # After word char: move space outside
        text = re.sub(r'(\w)\*\*\*\s+([^*\n]+?\*\*\*)', r'\1 ***\2', text)
        # After punctuation: ",*** text***" -> ", ***text***" (move space outside)
        text = re.sub(r'([^\w\s*])(\*\*\*)\s+([^*\n]+?\*\*\*)', r'\1 \2\3', text)
        # After whitespace or start: remove the leading space
        text = re.sub(r'\*\*\*\s+([^*\n]+?\*\*\*)', r'***\1', text)

        # Fix trailing whitespace inside bold-italic markers: "***text ***" -> "***text***"
        text = re.sub(r'\*\*\*([^*\n]+?)\s+\*\*\*(\w)', r'***\1*** \2', text)
        text = re.sub(r'\*\*\*([^*\n]+?)\s+\*\*\*(?=[^a-zA-Z0-9]|$)', r'***\1***', text)

        # Fix leading whitespace inside bold markers: "** Adaptation**" -> "**Adaptation**"
        # Use [^*\n] to avoid matching across lines
        # When preceded by a word character, preserve the space before **
        text = re.sub(r'(\w)\*\*\s+([^*\n]+?\*\*)', r'\1 **\2', text)
        # When preceded by punctuation or start, just remove the leading space
        text = re.sub(r'\*\*\s+([^*\n]+?\*\*)', r'**\1', text)

        # Fix leading whitespace inside italic markers.
        # After a word char: "word* text*" -> "word *text*" (move space outside)
        text = re.sub(r'(\w)(?<!\*)\*\s+([^*\n]+?\*(?!\*))', r'\1 *\2', text)
        # After punctuation (e.g. comma): ",* text*" -> ", *text*" (move space outside so
        # the * is preceded by a space and MDX recognises it as an italic opener)
        text = re.sub(r'([^\w\s*])(\*{1,3})\s+([^*\n]+?\*)', r'\1 \2\3', text)
        # After whitespace or start of line: "* text*" -> "*text*"
        text = re.sub(r'(?<!\*)\*\s+([^*\n]+?\*(?!\*))', r'*\1', text)

        # Fix trailing whitespace inside bold markers: "**text: **" -> "**text:**"
        # This handles cases like "**Gen Z want goosebumps: **" where trailing space breaks bold
        # Use [^*\n] to avoid matching across lines
        # When followed by a word character, preserve the space after the closing **
        text = re.sub(r'\*\*([^*\n]+?)\s+\*\*(\w)', r'**\1** \2', text)
        # When followed by punctuation or end of line, just remove the trailing space
        text = re.sub(r'\*\*([^*\n]+?)\s+\*\*(?=[^a-zA-Z0-9]|$)', r'**\1**', text)

        # Fix trailing whitespace inside italic markers: "*text *" -> "*text*"
        # Same logic: preserve space after if followed by word character
        text = re.sub(r'(?<!\*)\*([^*\n]+?)\s+\*(?!\*)(\w)', r'*\1* \2', text)
        text = re.sub(r'(?<!\*)\*([^*\n]+?)\s+\*(?!\*)(?=[^a-zA-Z0-9]|$)', r'*\1*', text)

        # Fix bold split at hyphen: word**-**word -> word-word (Pandoc artefact when
        # bold formatting spans a hyphenated compound and splits at the hyphen)
        text = re.sub(r'\*\*-\*\*', '-', text)

        # Fix missing space after closing bold/bold+italic when followed directly by a word:
        # ***Arcade***is -> ***Arcade*** is
        text = re.sub(r'(?<=\w)(\*{2,3})(?=[a-zA-Z])', r'\1 ', text)

        # Ensure "Tip:" labels start on a new paragraph (not glued to preceding link/button)
        # Handles both bare [Case study: X]** Tip:** and resolved <a ...>** Tip:**
        text = re.sub(r'(\]|</a>)\*\*\s+Tip:', r'\1\n\n**Tip:', text)

        # Ensure numbered section headers start on a new paragraph wherever they appear
        # mid-line (e.g. "...matter.** 2) Chase..." -> "...matter.\n\n**2) Chase...")
        text = re.sub(r'(?<!\n)\*\*\s+(\d+\)\s)', r'\n\n**\1', text)

        # Fix m**u**ltisensory (single character bolding inside word - clearly an artifact)
        # Apply multiple times to catch adjacent occurrences
        for _ in range(3):
            text = re.sub(r'(\w)\*\*(\w)\*\*(\w)', r'\1\2\3', text)

        # Fix single character italic inside word: m*u*ltisensory -> multisensory
        for _ in range(3):
            text = re.sub(r'(\w)\*(\w)\*(\w)', r'\1\2\3', text)

        # Merge adjacent bold markers: **word** **word** -> **word word**
        text = re.sub(r'\*\*([^*]+)\*\*\s+\*\*([^*]+)\*\*', r'**\1 \2**', text)

        # Merge adjacent italic markers: *word* *word* -> *word word*
        # Be careful not to match ** (bold)
        text = re.sub(r'(?<!\*)\*([^*]+)\*\s+\*([^*]+)\*(?!\*)', r'*\1 \2*', text)

        # Fix lines that are ONLY "**" (empty bold)
        lines = text.split('\n')
        fixed_lines = []
        for line in lines:
            if line.strip() == '**':
                fixed_lines.append('')
            elif line.strip() == '*':
                fixed_lines.append('')
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    content = clean_formatting(content)

    return content


def create_mdx_content(page: dict, position: int, is_references_page: bool = False) -> str:
    """Create MDX file content with Docusaurus frontmatter and imports."""
    # Clean up the title - remove backslashes that might be escaping brackets (from Pandoc)
    # This prevents invalid YAML escape sequences like \[ in frontmatter
    title = page['title'].replace('\\', '')
    
    # Escape quotes in title for frontmatter
    safe_title = title.replace('"', '\\"')

    # Use the slug as the explicit ID to prevent collisions from numeric filename prefixes
    doc_id = page['slug']
    # url_slug overrides the URL path when set (H2 pages use short slug for URL,
    # prefixed slug for unique ID)
    url_slug = page.get('url_slug')

    # Compute reading time (approx 200 words per minute)
    words = len(re.findall(r'\w+', page['content']))
    reading_time = max(1, round(words / 200))

    # Frontmatter MUST come first in Docusaurus
    slug_line = f'\nslug: "{url_slug}"' if url_slug else ''
    frontmatter = f"""---
title: "{safe_title}"
id: "{doc_id}"{slug_line}
sidebar_position: {position}
custom_edit_url: null
readingTimeMinutes: {reading_time}
---

"""
    header_prefix = "#" * page["level"]
    # Clean up title for the main header as well
    clean_header_title = page['title'].replace('\\', '')

    # Inject inline reading time annotation if available
    reading_time_display = page.get('reading_time_display')
    if reading_time_display:
        aria_label = f"{reading_time_display} minute read"
        header_line = (
            f'{header_prefix} {clean_header_title} '
            f'<span className="reading-time" role="note" aria-label="{aria_label}">'
            f'<span aria-hidden="true">{reading_time_display} min</span></span>\n\n'
        )
        # Update frontmatter to reflect the displayed time (aggregate for H1s)
        frontmatter = frontmatter.replace(
            f'readingTimeMinutes: {reading_time}',
            f'readingTimeMinutes: {reading_time_display}'
        )
    else:
        header_line = f"{header_prefix} {clean_header_title}\n\n"

    # Fix MDX syntax issues in the content
    fixed_content = fix_mdx_syntax(page["content"])

    # Generate stable blockId for the whole page
    content_hash = hashlib.sha256(fixed_content.encode()).hexdigest()[:8]
    page_block_id = f"page-{doc_id}-{content_hash}"

    # Inject reading times into H3 sub-headings (skip references)
    if not is_references_page:
        fixed_content = inject_subheading_reading_times(fixed_content)

    # Handle references page specially
    if is_references_page:
        # Create a clean references page with the ReferenceList component
        return frontmatter + MDX_IMPORTS_REFERENCES + header_line + f"""
<TrackedBlock blockId="{page_block_id}" topic="references" label="{safe_title}">
<ReferenceList references={{references}} />
</TrackedBlock>
"""

    # Convert citations to interactive components
    fixed_content, has_citations = convert_citations_in_content(fixed_content)

    # Wrap main content in TrackedBlock
    topic = doc_id.split("-")[0] # Simple topic extraction
    tracked_content = f'<TrackedBlock blockId="{page_block_id}" topic="{topic}" label="{safe_title}">\n\n{fixed_content}\n\n</TrackedBlock>'

    # Choose imports based on whether page has citations
    imports = MDX_IMPORTS if has_citations else MDX_IMPORTS_SIMPLE

    # Correct order: frontmatter, imports, content
    return frontmatter + imports + header_line + tracked_content


def create_homepage_content(page: dict, is_references_page: bool = False) -> str:
    """Create the homepage index.mdx from the pre-H1 content."""
    title = page['title'].replace('\\', '')
    safe_title = title.replace('"', '\\"')

    # Compute reading time
    words = len(re.findall(r'\w+', page['content']))
    reading_time = max(1, round(words / 200))

    # Homepage frontmatter with slug: / to make it the root
    frontmatter = f"""---
title: "{safe_title}"
id: "index"
sidebar_position: 0
slug: /
custom_edit_url: null
readingTimeMinutes: {reading_time}
---

"""
    # Fix MDX syntax issues in the content
    fixed_content = fix_mdx_syntax(page["content"])

    # Generate stable blockId for the whole page
    content_hash = hashlib.sha256(fixed_content.encode()).hexdigest()[:8]
    page_block_id = f"page-index-{content_hash}"

    # Inject reading times into H3 sub-headings (skip references)
    if not is_references_page:
        fixed_content = inject_subheading_reading_times(fixed_content)

    if is_references_page:
        return frontmatter + MDX_IMPORTS_REFERENCES + f"# {title}\n\n" + f"""
<TrackedBlock blockId="{page_block_id}" topic="references" label="{safe_title}">
<ReferenceList references={{references}} />
</TrackedBlock>
"""

    # Convert citations
    fixed_content, has_citations = convert_citations_in_content(fixed_content)
    imports = MDX_IMPORTS if has_citations else MDX_IMPORTS_SIMPLE

    # Wrap main content in TrackedBlock
    tracked_content = f'<TrackedBlock blockId="{page_block_id}" topic="home" label="{safe_title}">\n\n{fixed_content}\n\n</TrackedBlock>'

    # Inject inline reading time annotation if available
    reading_time_display = page.get('reading_time_display')
    if reading_time_display:
        aria_label = f"{reading_time_display} minute read"
        header_line = (
            f'# {title} '
            f'<span className="reading-time" role="note" aria-label="{aria_label}">'
            f'<span aria-hidden="true">{reading_time_display} min</span></span>\n\n'
        )
        # Update frontmatter reading time to match displayed aggregate
        frontmatter = frontmatter.replace(
            f'readingTimeMinutes: {reading_time}',
            f'readingTimeMinutes: {reading_time_display}'
        )
    else:
        header_line = f"# {title}\n\n"

    return frontmatter + imports + header_line + fixed_content


def inject_subheading_reading_times(content: str) -> str:
    """Inject inline reading-time spans into H3 and H4 headings within page content.

    For each heading, counts words from that heading to the next heading of the
    same or higher level (or end of content) and appends a reading-time annotation.
    """
    # Process H3 and H4 headings
    target_pattern = re.compile(r'^(#{3,4})\s+(.+)$', re.MULTILINE)
    # All headings H1-H4 serve as section boundaries
    boundary_pattern = re.compile(r'^#{1,4}\s+', re.MULTILINE)

    matches = list(target_pattern.finditer(content))
    if not matches:
        return content

    all_heading_starts = [m.start() for m in boundary_pattern.finditer(content)]

    # Process in reverse so replacements don't shift positions
    for match in reversed(matches):
        prefix = match.group(1)  # '###' or '####'
        level = len(prefix)
        section_start = match.end()

        # Find the next heading of same or higher level (fewer or equal #)
        section_end = len(content)
        for pos in all_heading_starts:
            if pos <= match.start():
                continue
            # Check the actual level of the heading at this position
            heading_at_pos = boundary_pattern.match(content, pos)
            if heading_at_pos:
                boundary_level = len(heading_at_pos.group().rstrip().rstrip(' '))
                if boundary_level <= level:
                    section_end = pos
                    break

        section_text = content[section_start:section_end]
        words = len(re.findall(r'\w+', section_text))
        minutes = max(1, round(words / 200))

        heading_text = match.group(2)
        heading_id = slugify(heading_text)
        aria_label = f"{minutes} minute read"
        # Use a preceding <span id> anchor rather than {#id} syntax: in MDX files
        # {#...} is treated as a JSX expression and renders as literal text.
        replacement = (
            f'<span id="{heading_id}"></span>\n\n'
            f'{prefix} {heading_text} '
            f'<span className="reading-time" role="note" aria-label="{aria_label}">'
            f'<span aria-hidden="true">{minutes} min</span></span>'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


def compute_reading_times(pages: list[dict]) -> dict:
    """Compute per-page reading times based on each page's own content.

    Each page's content includes the heading and all sub-headings (H3-H6)
    that fall within that page, so this already reflects the full on-page
    reading time.

    Returns:
        {page_index: minutes} — at least 1 minute per page.
    """
    page_reading = {}
    for i, page in enumerate(pages):
        words = len(re.findall(r'\w+', page['content']))
        page_reading[i] = max(1, round(words / 200))
    return page_reading


def save_mdx_files(pages: list[dict], output_folder: Path,
                    anchor_registry: dict = None, url_map: dict = None,
                    title_link_registry: dict = None) -> tuple[list[Path], list[str]]:
    """Save pages as .mdx files with hierarchical folder structure.

    H1 sections become folders with collapsible categories.
    H2 sections become pages within those folders.

    Special case: Content before the first H1 (including any H2s) becomes
    the homepage (root index.mdx) with all content merged together.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    # Pre-compute reading times
    page_reading = compute_reading_times(pages)

    created_files = []
    all_unresolved: list[str] = []  # accumulate unresolved bare-title links
    current_h1_folder = None
    current_h1_slug = None
    current_h1_position = 0
    h2_position = 0
    found_first_h1 = False  # Track if we've encountered the first H1
    homepage_content = ""  # Accumulate content for the homepage
    homepage_title = "Home"  # Default title for homepage

    for i, page in enumerate(pages):
        is_references_page = page['slug'] == 'references' or page['title'].lower() == 'references'

        if page['level'] == 1:
            # Check if this is the very first H1 in the document
            is_first_h1 = not found_first_h1
            found_first_h1 = True

            if is_first_h1:
                # Apply cross-document link resolution before creating content
                resolved_content = page['content']
                if anchor_registry and url_map:
                    resolved_content = preserve_ref_anchors(resolved_content)
                    resolved_content = rewrite_internal_links(resolved_content, i, anchor_registry, url_map)
                if title_link_registry:
                    resolved_content, unresolved = resolve_bare_title_links(resolved_content, title_link_registry)
                    all_unresolved.extend(unresolved)
                resolved_content = replace_top_level_headings_placeholder(resolved_content, pages, url_map)
                # Use the first H1 as the homepage
                homepage_page = {
                    'title': page['title'],
                    'level': 1,
                    'slug': 'index',
                    'content': resolved_content,
                    'reading_time_display': page_reading.get(i) if not is_references_page else None,
                }
                content = create_homepage_content(homepage_page, is_references_page=is_references_page)
                filepath = output_folder / "index.mdx"
                filepath.write_text(content, encoding="utf-8")
                created_files.append(filepath)
                print(f"  Created: index.mdx (homepage from first H1: {page['title']})")
                
                # We skip creating a folder for the first H1 as it's now the homepage
                continue

            # Subsequent H1s: Create a new folder (category)
            current_h1_position += 1
            h2_position = 0
            current_h1_slug = page['slug']
            folder_name = f"{current_h1_position:02d}-{current_h1_slug}"
            current_h1_folder = output_folder / folder_name
            current_h1_folder.mkdir(parents=True, exist_ok=True)

            # Create _category_.json for collapsible sidebar
            category_meta = {
                "label": page['title'].replace('\\', ''),
                "position": current_h1_position,
                "collapsible": True,
                "collapsed": False,
                "link": {
                    "type": "doc",
                    "id": f"h1-{current_h1_position:02d}-{current_h1_slug}-overview"
                }
            }
            category_file = current_h1_folder / "_category_.json"
            category_file.write_text(json.dumps(category_meta, indent=2), encoding="utf-8")

            # Apply cross-document link resolution before creating content
            if anchor_registry and url_map:
                page['content'] = preserve_ref_anchors(page['content'])
                page['content'] = rewrite_internal_links(page['content'], i, anchor_registry, url_map)
            if title_link_registry:
                page['content'], unresolved = resolve_bare_title_links(page['content'], title_link_registry)
                all_unresolved.extend(unresolved)
            page['content'] = replace_top_level_headings_placeholder(page['content'], pages, url_map)

            # Save H1 content as index.mdx in the folder (linked via _category_.json)
            overview_page = page.copy()
            overview_page['title'] = page['title']
            overview_page['slug'] = f"h1-{current_h1_position:02d}-{current_h1_slug}-overview"
            overview_page['reading_time_display'] = page_reading.get(i) if not is_references_page else None
            content = create_mdx_content(overview_page, 1, is_references_page=is_references_page)
            filepath = current_h1_folder / "index.mdx"
            filepath.write_text(content, encoding="utf-8")
            created_files.append(filepath)
            print(f"  Created: {folder_name}/index.mdx")

        else:
            # H2: Handle based on whether we've hit the first H1 yet
            if not found_first_h1:
                # Before any H1 - merge into homepage content
                resolved_content = page['content']
                if anchor_registry and url_map:
                    resolved_content = preserve_ref_anchors(resolved_content)
                    resolved_content = rewrite_internal_links(resolved_content, i, anchor_registry, url_map)
                if title_link_registry:
                    resolved_content, unresolved = resolve_bare_title_links(resolved_content, title_link_registry)
                    all_unresolved.extend(unresolved)
                if not homepage_content:
                    # Use the first H2 title as the homepage title
                    homepage_title = page['title']
                    homepage_content = resolved_content
                    print(f"  Starting homepage with: {page['title']}")
                else:
                    # Add subsequent H2s as sections in the homepage
                    h2_header = f"\n\n## {page['title']}\n\n"
                    homepage_content += h2_header + resolved_content
                    print(f"    Merged H2 into homepage: {page['title']}")
            else:
                # After first H1: Normal H2 handling - save inside current H1 folder
                h2_position += 1
                if current_h1_folder is None:
                    # This happens if there are H2s before any H1, or after the first H1 which we skipped folder creation for
                    filename = f"{h2_position:02d}-{page['slug']}.mdx"
                    filepath = output_folder / filename
                else:
                    filename = f"{h2_position:02d}-{page['slug']}.mdx"
                    filepath = current_h1_folder / filename
                    page['url_slug'] = page['slug']  # short slug for URL override
                    page['slug'] = f"{current_h1_slug}-{page['slug']}"

                # Apply cross-document link resolution before creating content
                if anchor_registry and url_map:
                    page['content'] = preserve_ref_anchors(page['content'])
                    page['content'] = rewrite_internal_links(page['content'], i, anchor_registry, url_map)
                if title_link_registry:
                    page['content'], unresolved = resolve_bare_title_links(page['content'], title_link_registry)
                    all_unresolved.extend(unresolved)
                page['content'] = replace_top_level_headings_placeholder(page['content'], pages, url_map)

                # Set reading time for H2 pages (skip references)
                if not is_references_page:
                    page['reading_time_display'] = page_reading.get(i)

                content = create_mdx_content(page, h2_position, is_references_page=is_references_page)
                filepath.write_text(content, encoding="utf-8")
                created_files.append(filepath)
                print(f"  Created: {filepath.relative_to(output_folder)}")

    # Handle case where the document has no H1s at all, OR has content before the first H1
    if not found_first_h1 and homepage_content:
        # Case 1: No H1s at all - existing logic
        homepage_page = {
            'title': homepage_title,
            'level': 1,
            'slug': 'index',
            'content': homepage_content
        }
        content = create_homepage_content(homepage_page, is_references_page=False)
        filepath = output_folder / "index.mdx"
        filepath.write_text(content, encoding="utf-8")
        created_files.append(filepath)
        print(f"  Created: index.mdx (homepage with merged content from start of doc)")
    elif homepage_content:
        # Case 2: Content before first H1 - create as a separate introduction/overview page
        # Since first H1 is the homepage, we need to decide where this goes.
        # Let's put it in a "00-introduction" folder or similar if we want it to be first,
        # but the prompt says "Please use Header 1 and header1 contents as this homepage".
        # If there's content BEFORE header 1, it might be an abstract or title page.
        # For now, let's prepend it to the homepage content if it exists.
        homepage_path = output_folder / "index.mdx"
        if homepage_path.exists():
            current_home_content = homepage_path.read_text(encoding="utf-8")
            # We need to insert it AFTER the frontmatter of the homepage
            parts = current_home_content.split("---\n\n", 1)
            if len(parts) == 2:
                new_content = parts[0] + "---\n\n" + fix_mdx_syntax(homepage_content) + "\n\n" + parts[1]
                homepage_path.write_text(new_content, encoding="utf-8")
                print(f"  Prepended pre-H1 content to index.mdx")

    return created_files, all_unresolved


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

        # Replace latency chart embed marker (primary — set in Word doc)
        # Matches both inline code `[CHART: latency-tolerance]` (Pandoc Code style)
        # and plain text [CHART: latency-tolerance]
        content = re.sub(
            r'`\[CHART:\s*latency-tolerance\]`|\[CHART:\s*latency-tolerance\]',
            '\n\n<LatencyChart />\n\n',
            content
        )


        # Warn about spaces immediately before reference superscripts
        for m in re.finditer(r'(\S[^\S\n]+)<sup>(\d[^<]*)</sup>', content):
            # Extract a short snippet for context (up to 60 chars around the match)
            start = max(0, m.start() - 20)
            end = min(len(content), m.end() + 20)
            snippet = content[start:end].replace('\n', ' ')
            WARNINGS.append(f"[Ref] Space before reference in {mdx_file.name}: ...{snippet!r}...")

        # Warn about punctuation immediately before reference superscripts
        for m in re.finditer(r'([.,;:!?])[^\S\n]*<sup>(\d[^<]*)</sup>', content):
            start = max(0, m.start() - 20)
            end = min(len(content), m.end() + 20)
            snippet = content[start:end].replace('\n', ' ')
            WARNINGS.append(f"[Ref] Punctuation before reference in {mdx_file.name}: ...{snippet!r}...")

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

    # Copy data files from report/ into Docusaurus src/data/
    src_data_folder = docs_folder.parent / "src" / "data"
    src_data_folder.mkdir(parents=True, exist_ok=True)
    for data_file in INPUT_FOLDER.glob("*.json"):
        dest = src_data_folder / data_file.name
        shutil.copy2(data_file, dest)
        print(f"  Copied {data_file.name} to {dest}")

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
    # Increase memory limit for Node.js to avoid OOM
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    
    if sys.platform == "win32":
        process = subprocess.Popen(
            "npm start",
            cwd=docusaurus_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            env=env,
        )
    else:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=docusaurus_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
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


def remove_word_toc(markdown: str) -> str:
    """Remove Microsoft Word generated Table of Contents from markdown.

    Handles two cases:
    1. TOC has a visible heading (e.g. "Table of Contents", "Contents") — skip from
       that heading to the next H1.
    2. No explicit heading — detect 3+ TOC-style link lines (blank lines between them
       are tolerated) and skip to the next H1.
    """
    lines = markdown.splitlines()
    n = len(lines)

    # TOC entry patterns produced by pandoc from Word hyperlinked TOCs:
    #   [Title [9](#_Toc12345)](#_Toc12345)
    #   [Title [9](#section-slug)](#section-slug)
    #   [Title](#section-slug)   (some pandoc versions)
    toc_entry = re.compile(
        r'^\[.+\]\(#_?Toc\d+\)'           # any link to #_TocNNN
        r'|^\[.+? \[\d+\]\(#.+?\)\]\(#.+?\)'  # [Text [N](#x)](#x) with page number
        r'|^\[.+\]\(#[-\w]+\)\s*$',       # plain [Text](#slug) — whole line
        re.IGNORECASE
    )

    # Heading-style TOC titles (various pandoc renderings of the Word TOC title)
    toc_heading = re.compile(
        r'^#{1,3}\s*(table\s+of\s+contents|contents)\s*$'
        r'|^\*{1,2}(table\s+of\s+contents|contents)\*{1,2}\s*.*$'
        r'|\[?\*{0,2}(table\s+of\s+contents|contents)\*{0,2}\]?.*\{.*\.TOC',
        re.IGNORECASE
    )

    def skip_to_next_h1(start: int) -> int:
        """Return the index of the next H1 line at or after `start`."""
        for k in range(start, n):
            if re.match(r'^#\s', lines[k]):
                return k
        return n  # no H1 found — skip to end

    result = []
    i = 0
    # Only scan the first 150 lines for a TOC (it's always near the top)
    toc_search_limit = min(150, n)

    while i < n:
        clean = lines[i].strip()

        if i < toc_search_limit:
            # Strategy 1: explicit TOC heading detected → skip to next H1
            if toc_heading.match(clean):
                i = skip_to_next_h1(i + 1)
                continue

            # Strategy 2: TOC entry line — look ahead (tolerating blank lines)
            # to see if there are 3+ such lines in a cluster
            if toc_entry.match(clean):
                j = i
                toc_count = 0
                scanned = 0
                while j < n and scanned < 30:
                    jclean = lines[j].strip()
                    if toc_entry.match(jclean):
                        toc_count += 1
                    elif jclean:          # non-empty, non-TOC → end of cluster
                        break
                    j += 1
                    scanned += 1

                if toc_count >= 3:
                    i = skip_to_next_h1(j)
                    continue

            # Remove "What are you looking for?" navigation prompts before TOC entries
            if "What are you looking for?" in lines[i]:
                next_clean = lines[i + 1].strip() if i + 1 < n else ""
                if toc_entry.match(next_clean):
                    i += 1
                    continue

        result.append(lines[i])
        i += 1

    return "\n".join(result)


def extract_chart_data_tables(markdown: str) -> str:
    """Detect [CHART-DATA: <id>] markers followed by a markdown table, extract
    the data as JSON into report/, and replace the marker+table with
    [CHART: <id>] so the rest of the pipeline injects the component.

    Table columns expected (order-independent, case-insensitive):
      Group | Label | Value (ms) | Error (ms) | Threshold | Citations

    Mendeley/Pandoc superscripts in the Citations cell (e.g. ^46^ or ^46,47^)
    are parsed into a list of integer reference numbers.
    """
    # Pandoc escapes [ and ] in plain paragraphs → \[CHART-DATA: ...\]
    # Also handle unescaped form and backtick-wrapped inline-code form.
    # The table may be a pipe table (|col|) or a Pandoc grid table (+---+---+).
    # An optional end tag [/CHART-DATA] or [/CHART-DATA <id>] (escaped or
    # backtick-wrapped) may follow the table; any whitespace around the table
    # (between prefix/table and table/suffix) is consumed and discarded.
    marker_pattern = re.compile(
        r'`?\\?\[CHART-DATA:\s*(?P<chart_id>[^\]\\\n]+?)\\?\]`?'
        r'\s*'
        r'(?P<table>(?:(?:\|[^\n]+|\+[-=:+| ]+)\n)+)'
        r'\s*'
        r'(?:`?\\?\[/CHART-DATA(?:\s+[^\]\\\n]+?)?\\?\]`?)?',
        re.MULTILINE
    )

    def _parse_cell_citations(cell: str) -> list[int]:
        """Extract reference numbers from superscripts like ^46^ or ^46,47^."""
        nums = []
        for m in re.finditer(r'\^([\d,\s]+)\^', cell):
            for part in m.group(1).split(','):
                part = part.strip()
                if part.isdigit():
                    nums.append(int(part))
        return nums

    def _col_index(headers: list[str], *candidates: str) -> int:
        """Find column index by trying candidate names (case-insensitive)."""
        for h in headers:
            for c in candidates:
                if c.lower() in h.lower():
                    return headers.index(h)
        return -1

    def _wrap_label(text: str, width: int = 28) -> str:
        """Auto-wrap long label text at word boundaries, matching R str_wrap behaviour."""
        words = text.split()
        lines, current, current_len = [], [], 0
        for word in words:
            if current and current_len + 1 + len(word) > width:
                lines.append(' '.join(current))
                current, current_len = [word], len(word)
            else:
                current.append(word)
                current_len += (1 if current_len else 0) + len(word)
        if current:
            lines.append(' '.join(current))
        return '\n'.join(lines)

    def _replace_table(match: re.Match) -> str:
        chart_id = match.group('chart_id').strip()
        raw_table = match.group('table')

        rows = [
            [cell.strip() for cell in line.strip().strip('|').split('|')]
            for line in raw_table.strip().splitlines()
            if line.strip()
            and line.strip().startswith('|')           # skip +---+ grid separators
            and not re.match(r'^\s*\|[-:| ]+\|\s*$', line)  # skip pipe-table divider
        ]
        if len(rows) < 2:
            return match.group(0)  # not enough rows — leave unchanged

        headers = rows[0]
        i_group     = _col_index(headers, 'group')
        i_label     = _col_index(headers, 'label')
        i_value     = _col_index(headers, 'value')
        i_error     = _col_index(headers, 'error')
        i_threshold = _col_index(headers, 'threshold')
        i_citations = _col_index(headers, 'citation', 'ref')

        if -1 in (i_group, i_label, i_value, i_threshold):
            WARNINGS.append(f"[CHART-DATA] Could not identify required columns in {chart_id} table — skipping")
            return match.group(0)

        tolerance_bars = []
        imperceptible_bars = []
        legend_text = None

        for row in rows[1:]:
            if not row or not any(cell.strip() for cell in row):
                continue

            # Strip Pandoc backslash-escapes (e.g. \[LEGEND\] → [LEGEND])
            group = re.sub(r'\\(.)', r'\1', row[i_group].strip()) if i_group < len(row) else ''

            # Legend row: first cell is [LEGEND]
            if group.upper() == '[LEGEND]':
                raw = row[i_label].strip() if i_label < len(row) else ''
                legend_text = re.sub(r'\\(.)', r'\1', raw)
                continue

            if len(row) <= max(i_group, i_label, i_value, i_threshold):
                continue

            raw_label = re.sub(r'\\(.)', r'\1', row[i_label])  # unescape \[ etc.
            # Extract citations from dedicated column or (if none) from label cell;
            # then strip the ^N^ markers from the label text itself.
            if i_citations != -1 and i_citations < len(row):
                citations = _parse_cell_citations(row[i_citations])
            else:
                citations = _parse_cell_citations(raw_label)
                raw_label = re.sub(r'\s*\^[\d,\s]+\^', '', raw_label).strip()
            label     = _wrap_label(raw_label)
            raw_val   = re.sub(r'[^\d.]', '', row[i_value])
            raw_err   = re.sub(r'[^\d.]', '', row[i_error]) if i_error != -1 and i_error < len(row) else '0'
            threshold = row[i_threshold].strip()

            try:
                value    = float(raw_val) if raw_val else 0.0
                errorBar = float(raw_err) if raw_err else 0.0
            except ValueError:
                continue

            entry = {'label': label, 'value': value, 'errorBar': errorBar}
            if citations:
                entry['citations'] = citations

            if threshold.lower() == 'not noticeable':
                imperceptible_bars.append(entry)
            else:
                entry['group'] = group
                tolerance_bars.append(entry)

        # Compute shared xMax (rounded up to nearest 25)
        all_vals = [b['value'] + b['errorBar'] for b in tolerance_bars + imperceptible_bars]
        raw_max  = max(all_vals) if all_vals else 275
        x_max    = int(math.ceil(raw_max / 25) * 25)

        meta_block = {
            'xAxisLabel':          'Value (ms)',
            'xMax':                x_max,
            'toleranceColour':     '#440154FF',
            'imperceptibleColour': '#5DC863FF',
        }
        if legend_text:
            meta_block['legend'] = legend_text

        payload = {
            'meta':             meta_block,
            'toleranceBars':    tolerance_bars,
            'imperceptibleBars': imperceptible_bars,
        }

        out_path = INPUT_FOLDER / 'latency_data.json'
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"  [CHART-DATA] Wrote {out_path} ({len(tolerance_bars)} tolerance bars, {len(imperceptible_bars)} imperceptible bars)")

        return f'\n\n[CHART: {chart_id}]\n\n'

    # First, strip any legacy \[CHART: id\] or [CHART: id] embed markers that were
    # manually added to Word in a previous pass — the pipeline now generates them
    # automatically from [CHART-DATA: id], so keeping both would create duplicates.
    markdown = re.sub(r'\\?\[CHART(?!-DATA):\s*[^\]\\\n]+\\?\]', '', markdown)

    return marker_pattern.sub(_replace_table, markdown)


def process_document(docx_path: Path, output_folder: Path) -> list[dict]:
    """Process a single Word document through the pipeline."""
    print(f"\nProcessing: {docx_path}")

    print("  Converting to markdown with pandoc (extracting media)...")
    markdown = convert_docx_to_md(docx_path, extract_media_to=output_folder)

    # Remove Word-generated TOC
    print("  Removing Word-generated Table of Contents...")
    markdown = remove_word_toc(markdown)

    # Extract [CHART-DATA: ...] tables → write JSON → replace with [CHART: ...] marker
    print("  Extracting chart data tables...")
    markdown = extract_chart_data_tables(markdown)

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

    print("  Building cross-document link registry...")
    anchor_registry = collect_anchor_registry(markdown, pages)
    url_map = build_page_url_map(pages)
    print(f"  Registered {len(anchor_registry)} link targets across {len(url_map)} pages")

    print("  Building title-link registry...")
    title_link_registry = build_title_link_registry(markdown, pages, url_map)
    print(f"  Indexed {len(title_link_registry)} headings for bare-title linking")

    print("  Saving MDX files...")
    _, unresolved_titles = save_mdx_files(pages, output_folder, anchor_registry, url_map, title_link_registry)

    # Note: index.mdx (homepage) is created by save_mdx_files from pre-H1 content

    for title in unresolved_titles:
        WARNINGS.append(f"[Links] Unresolved bare-title link: [{title}]")

    return pages


def main():
    """Main entry point for the pipeline."""
    print("=" * 60)
    print("Word to MDX + Docusaurus Pipeline")
    print("=" * 60)

    # Check pandoc
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        _c_ok(f"Using pandoc: {result.stdout.decode().split(chr(10))[0]}")
    except FileNotFoundError:
        _c_error("ERROR: pandoc not found. Please install pandoc first.")
        _c_error("  https://pandoc.org/installing.html")
        sys.exit(1)

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, check=True, shell=True)
        _c_ok(f"Using npm: v{result.stdout.decode().strip()}")
    except FileNotFoundError:
        _c_error("ERROR: npm not found. Please install Node.js first.")
        sys.exit(1)

    # Optionally fetch the latest report from SharePoint
    if SHAREPOINT_FETCH:
        print("\n" + "-" * 60)
        print("Fetching report from SharePoint...")
        fetch_from_sharepoint()
    else:
        _c_info("\n[INFO] SHAREPOINT_FETCH=0 — using local files in report/")

    # Find Word documents
    docx_files = find_docx_files(INPUT_FOLDER)
    if not docx_files:
        _c_warn(f"\nNo .docx files found in {INPUT_FOLDER}/")
        sys.exit(0)

    print(f"\nFound {len(docx_files)} Word document(s) in {INPUT_FOLDER}/")

    # Clear output folder before processing to avoid mixing old and new content
    if OUTPUT_FOLDER.exists():
        print(f"\nClearing previous output in {OUTPUT_FOLDER}/...")
        shutil.rmtree(OUTPUT_FOLDER)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Process each document
    for docx_path in docx_files:
        process_document(docx_path, OUTPUT_FOLDER)

    # Print accessibility summary
    if WARNINGS:
        _c_warn("\n" + "!" * 60)
        _c_warn(f"{len(WARNINGS)} warning(s) found:")
        _c_warn("!" * 60)
        for warning in WARNINGS:
            _c_warn(f"  - {warning}")
        _c_warn("!" * 60)
    else:
        _c_ok("\n[OK] No warnings.")

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
            _c_warn("\n⚠️  Build completed with errors:")
            _c_warn(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            _c_warn("\nYou can still start the dev server to see partial results.")
            response = input("\nContinue to start dev server? (y/n): ").lower()
            if response != 'y':
                print("Exiting.")
                sys.exit(1)
        else:
            _c_ok("[OK] Build successful!")
    except subprocess.TimeoutExpired:
        _c_warn("Build timed out, but continuing...")

    # Start Docusaurus server
    print("\n" + "-" * 60)
    print("Starting Docusaurus development server...")

    server_process = start_docusaurus_server(DOCUSAURUS_DIR)

    # Wait for server (Docusaurus will auto-open browser)
    print("  Waiting for server to be ready...")
    url = "http://localhost:3000"

    if wait_for_server(url, timeout=180):
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
