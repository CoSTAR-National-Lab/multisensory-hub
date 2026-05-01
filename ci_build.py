"""
CI-only entry point: runs the conversion pipeline without starting the dev server.
Used by .github/workflows/deploy.yml — do not run locally.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from docx_to_mdx import (
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    DOCS_FOLDER,
    find_docx_files,
    process_document,
    copy_to_docusaurus,
)

if OUTPUT_FOLDER.exists():
    shutil.rmtree(OUTPUT_FOLDER)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

docx_files = find_docx_files(INPUT_FOLDER)
if not docx_files:
    print(f"No .docx files found in {INPUT_FOLDER}/")
    sys.exit(1)

for docx_path in docx_files:
    print(f"Processing {docx_path.name}...")
    process_document(docx_path, OUTPUT_FOLDER)

copy_to_docusaurus(OUTPUT_FOLDER, DOCS_FOLDER)
print("Pipeline complete.")
