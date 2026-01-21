# AI project context – interactive report pipeline (Word → Docusaurus)

## project overview
This project converts a long, structured Word report (~20k words) into a **static but highly interactive Docusaurus site**.  
The Word document is the **single source of truth** and makes full use of heading hierarchies.

The output is a **scholarly, explorable web report** – not a blog, marketing site, or generic documentation.

---

## core objectives
- preserve the full intellectual and hierarchical structure of the original report
- reduce cognitive load via progressive disclosure
- support multiple reading paths (e.g. summary-first, methods-first, results-only)
- enable interactive exploration of figures, assumptions, and models
- produce a fully static site suitable for citation and long-term archiving

---

## constraints
- output must be compatible with **Docusaurus static builds**
- no server-side rendering at runtime
- all interactivity must be:
  - client-side (react / javascript), or
  - precomputed at build time
- python is used **only at build time**
- markdown / MDX must remain human-readable, diffable, and versionable
- accessibility and mobile readability are first-class concerns

---

## pipeline assumptions
- input format: `.docx`
- conversion via **Pandoc** to markdown
- a single python script, **`docx_to_mdx.py`**, orchestrates the pipeline:
  - running pandoc
  - markdown normalisation
  - splitting content by heading level
  - generating front matter
  - creating Docusaurus category/sidebars metadata
  - upgrading selected files to MDX
  - injecting controlled interactive structures
- final authoring formats: `.md` and `.mdx`

---

## implementation rule (important)
**Any requested changes, enhancements, or fixes must be implemented by modifying `docx_to_mdx.py`.**

The AI should:
- propose changes as edits, additions, or refactors to `docx_to_mdx.py`
- avoid suggesting manual post-processing steps
- avoid introducing parallel scripts unless explicitly requested
- assume `docx_to_mdx.py` is the canonical build pipeline

---

## interaction philosophy
Interactivity is used **only when it improves comprehension**, not for novelty.

Preferred patterns:
- collapsible sections for technical depth
- admonitions for rationale, caveats, and assumptions
- tabs for parallel explanations (e.g. summary / technical / replication)
- interactive figures where parameter changes affect interpretation

Avoid:
- decorative animations
- dense dashboards without narrative framing
- interactivity that obscures the main claim

---

## tone and audience
Primary audience:
- technically literate readers
- peer reviewers
- methodologically curious researchers

Tone:
- precise
- neutral
- explicit about assumptions and trade-offs
- no hype or marketing language
