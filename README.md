# Multisensory Hub

A build pipeline that converts a structured Word document into an interactive, static Docusaurus site. The `.docx` file is the single source of truth; Python handles all conversion at build time, producing MDX pages with React components that render a fully static site.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Conversion | Python 3 + Pandoc | |
| Framework | Docusaurus | 3.9.2 |
| UI | React | 19.0.0 |
| Language | TypeScript | 5.6.2 |
| Markup | MDX | 3.0.0 |
| Search | @cmfcmf/docusaurus-search-local | 2.0.1 |
| Styling | CSS Modules + CSS custom properties | |
| Typography | Inter (primary), Lexend (accessibility) | |

No server-side runtime. The output is plain static HTML/JS/CSS.

---

## Pipeline Overview

```
report/*.docx
    |
    v
[Pandoc] ──> raw markdown + extracted media
    |
    v
[docx_to_mdx.py]
    ├── Remove Word TOC
    ├── Extract & structure Mendeley references -> references.ts
    ├── Split by H1/H2 into pages
    ├── Assign unique slugs, generate folder hierarchy
    ├── Build cross-document link registry
    ├── Rewrite internal links for correct cross-page targets
    ├── Preserve Word _Ref anchors as HTML elements
    ├── Fix MDX syntax (superscripts, braces, dashes, images)
    ├── Inject React component imports + frontmatter
    └── Post-process: convert <sup> citations to <RefPopup>
    |
    v
docusaurus-site/docs/**/*.mdx  +  static/media/*
    |
    v
[npm run build] ──> static site in build/
```

A single invocation of `python docx_to_mdx.py` runs the full pipeline: conversion, splitting, MDX generation, copying to Docusaurus, building, and launching the dev server.

---

## Conversion Features

### Document Splitting

The pipeline splits the Word document into a Docusaurus page hierarchy based on heading levels:

- **H1** headings become sidebar categories (folders with `_category_.json`). The first H1 becomes the homepage (`slug: /`).
- **H2** headings become individual pages within their parent H1 folder.
- **H3-H6** headings remain as in-page sections.
- Content before the first H1 (abstract, TOC, etc.) is merged into the homepage.

Each page gets auto-generated frontmatter (`title`, `id`, `sidebar_position`, `readingTimeMinutes`).

### Cross-Document Link Resolution

Word internal cross-references break when content is split across pages. The pipeline fixes this:

1. **Anchor registry** &mdash; Before splitting, scans the full markdown for all `_Ref` anchors and heading slugs. Maps each to its final page index.
2. **URL map** &mdash; Mirrors Docusaurus folder-based routing to compute the URL for every page.
3. **Link rewriting** &mdash; `[text](#fragment)` links pointing to targets on a different page are rewritten to `[text](/target-page#fragment)`. Same-page links are left unchanged.
4. **Anchor preservation** &mdash; Word `_Ref` bookmark anchors (`[]{#_Ref... .anchor}`) are converted to `<span id="...">` elements before the MDX syntax fixer strips them.

### Reference Extraction

Mendeley-formatted references in the Word document are parsed into structured data:

- Extracts author, title, journal, year, volume, pages, DOI, and URL from each numbered reference.
- Generates a TypeScript file (`references.ts`) with typed `Reference[]` data.
- In-text superscript citations (`^36^`) are converted to `<RefPopup>` components with hover tooltips showing the full reference.
- Handles single refs, ranges (`20-22`), and comma-separated (`25,26`).

### MDX Syntax Normalization

Pandoc output contains artifacts that break MDX compilation. The pipeline fixes:

- Word document anchors (`[]{#_Ref... .anchor}`, `{.mark}`, `{.underline}`)
- Caret superscripts (`^36^` &rarr; `<sup>36</sup>`)
- Unescaped curly braces (fatal in JSX/MDX)
- Image attributes (`{width="..." height="..."}`) stripped
- Image paths rewritten to absolute (`/media/...`)
- HTML comments converted to JSX (`<!-- -->` &rarr; `{/* */}`)
- Pandoc dash encoding (`---` &rarr; em-dash, `--` &rarr; en-dash for number ranges, hyphen for compound words)
- Bold/italic formatting artifacts (misplaced spaces, single-char formatting, empty markers)
- Angle-bracket URLs unescaped
- Word-generated Table of Contents removed

### Media Handling

- Pandoc extracts embedded images to `mdx/media/`.
- The pipeline copies media to `docusaurus-site/static/media/` for absolute-path serving.
- Image paths in markdown are rewritten to `/media/...`.

---

## Interactive Components

All components are React/TypeScript with CSS Modules. They are injected via MDX imports on every generated page.

| Component | Purpose |
|-----------|---------|
| `Callout` | Info/warning/tip/note boxes with icons |
| `Chart` | Bar, line, and pie charts with dynamic colors |
| `CollapsibleSection` | Expandable sections with smooth animation |
| `DataTable` | Searchable, sortable, filterable tables |
| `InteractiveDemo` | "Try it out" containers with particle animations |
| `QuoteBlock` | Styled blockquotes with attribution |
| `RefPopup` | Citation hover popup with copy and DOI linking |
| `ReferenceList` | Filterable, searchable reference bibliography |
| `ScrollProgress` | Page scroll progress indicator |
| `ReadingSettings` | Font, word spacing, and line spacing controls (persisted to localStorage) |

Components that require citation data (`RefPopup`) are imported only on pages that contain citations. The references page gets its own `ReferenceList` import with the generated `references` data.

---

## Accessibility

- **ReadingSettings menu** in the navbar: switch between Inter, Lexend (dyslexia-optimised), or system font. Adjust word spacing and line spacing. Preferences persist in localStorage.
- Dark mode with full CSS variable theming.
- Semantic HTML, ARIA labels, keyboard navigation.
- Reading time estimates in frontmatter.

---

## Project Structure

```
.
├── report/                     # Input: .docx files
├── docx_to_mdx.py             # Build pipeline (single file)
├── mdx/                        # Intermediate output
│   ├── *.md                    #   Pandoc markdown
│   ├── media/                  #   Extracted images
│   ├── index.mdx               #   Homepage
│   └── NN-slug/                #   H1 category folders
│       ├── _category_.json
│       ├── index.mdx           #     H1 overview page
│       └── NN-slug.mdx         #     H2 pages
├── docusaurus-site/
│   ├── docs/                   # Final MDX (copied from mdx/)
│   ├── static/media/           # Final images
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── interactive/    #   Content components
│   │   │   ├── ReadingSettings/#   Accessibility UI
│   │   │   └── RefPopup.tsx    #   Citation popups
│   │   ├── css/custom.css      # Theme & global styles
│   │   ├── data/references.ts  # Generated reference data
│   │   └── theme/              # Docusaurus theme overrides
│   ├── docusaurus.config.ts
│   ├── sidebars.ts             # Auto-generated from folder structure
│   └── package.json
└── AI_CONTEXT.md               # Project requirements
```

---

## Usage

### Prerequisites

- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html)
- Node.js 20+

### Run the Pipeline

```bash
python docx_to_mdx.py
```

This will:
1. Convert `.docx` files in `report/` to markdown via Pandoc
2. Process, split, and generate MDX files in `mdx/`
3. Copy to `docusaurus-site/docs/`
4. Run `npm run build` to verify
5. Start the Docusaurus dev server at `http://localhost:3000`

### Conversion Only (No Server)

```python
from pathlib import Path
from docx_to_mdx import process_document, copy_to_docusaurus, OUTPUT_FOLDER, DOCS_FOLDER

process_document(Path("report/YourDocument.docx"), OUTPUT_FOLDER)
copy_to_docusaurus(OUTPUT_FOLDER, DOCS_FOLDER)
```

### Build Only

```bash
cd docusaurus-site
npm run build
npm run serve   # preview at localhost:3000
```

---

## Design Decisions

- **Single pipeline file** &mdash; All conversion logic lives in `docx_to_mdx.py`. No parallel scripts or manual post-processing steps.
- **Static output** &mdash; Zero runtime server dependencies. The built site can be hosted on any static file server, S3, GitHub Pages, etc.
- **Interactivity for comprehension** &mdash; Components are used to reduce cognitive load (collapsibles, tabs, hover citations), not for decoration.
- **Word as source of truth** &mdash; The `.docx` file is the canonical document. All MDX is regenerated from scratch on each pipeline run.
