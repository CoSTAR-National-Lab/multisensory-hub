---
name: refresh
description: Pull the latest report Word document from SharePoint, replace report/Multisensory Hub_Sept.docx, regenerate the MDX, rebuild, run the stray-asterisk check, and summarise what the author changed. Use when the user says /refresh, "grab the latest doc", "regenerate from SharePoint", or similar.
---

# Refresh the site from the latest Word report

The Word document on SharePoint is the single source of truth. This routine
pulls it, regenerates the site from it, and reports what changed.

## 1. Download the docx through the user's Chrome

SharePoint needs the user's authenticated session, so the fetch goes through
the Claude-in-Chrome extension, not curl.

Navigate a new tab to the direct-download endpoint (the `UniqueId` is the
`sourcedoc` GUID from the sharing link the user gave, lower-cased, with dashes):

```
https://rhul.sharepoint.com/sites/StoryFutures/_layouts/15/download.aspx?UniqueId=308db754-fd2d-4614-8f8c-dae5f46fd394
```

Chrome saves it to `~/Downloads` as `Multisensory Hub_Sept.docx`, or
`Multisensory Hub_Sept (N).docx` when a copy already exists – take the newest.
If nothing appears within a few seconds, Chrome may be showing an OS-level
Save dialog that only the user can click: ask them to click Save.
Appending `&download=1` to the `:w:/r/` sharing link does NOT work.
The tab ends on an unparseable URL afterwards; just close it.

## 2. Validate and replace

- Check the file starts with `PK` and contains `word/document.xml`.
- Compare its SHA-256 with `report/Multisensory Hub_Sept.docx`. If identical, stop: nothing to do.
- Keep a copy of the old docx (`git show HEAD:"report/Multisensory Hub_Sept.docx"`) for the diff in step 4.
- Copy the download over `report/Multisensory Hub_Sept.docx`.

## 3. Regenerate, build, check

From the repo root:

```
uv run python ci_build.py
cd docusaurus-site && npm run build && cd ..
uv run python docx_to_mdx.py --check-build
```

`ci_build.py` runs pandoc and the MDX pipeline without starting the dev
server (do not use `python docx_to_mdx.py` bare for this – it launches a dev
server on port 3000 that keeps the task alive). The check must report
"No stray emphasis markers"; any hit is bold/italic markup that failed to
render and is a bug to fix in `docx_to_mdx.py`, or a Word formatting glitch
to log in `issues.md`.

Baseline pipeline warnings that are harmless: case-study-steady-state
heading, current-technical-challenges duplicate, `[CHART: ...]` bare-title
links.

## 4. Summarise the author's changes

Convert old and new docx to plain text with pandoc (`-t plain --wrap=none`)
and diff them. Report the changed passages in a few bullets so the user knows
what the refresh brought in.

## 5. Commit and push

`docusaurus-site/docs/` and `mdx/` are generated and git-ignored; commit only
sources: the docx, `analytics/tracked-blocks.yml`, and
`docusaurus-site/docusaurus.config.ts` / `static/manifest.json` if the
pipeline bumped the analytics manifest version. Commit message pattern:
`Report <day> <Mon> <HH:MM>: <one-line gist of the changes>`.

Push to `costar master`; the deploy workflow regenerates, builds, runs the
asterisk check and publishes. Watch it with `gh run watch`.

Andy edits a separate working doc that is later copied over the SharePoint
file, so never edit the repo docx by hand; log rewordings in `issues.md`.
