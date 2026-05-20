"""One-time script to auto-populate blank entries in analytics/tracked-blocks.yml.

Assigns block_id (slugified heading), label (clean heading), topic, and concept
for every entry that currently has block_id: ''.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not found — run: pip install pyyaml")

# ---------------------------------------------------------------------------
# Topic mapping: normalised heading substring → topic slug
# Order matters — first match wins.
# ---------------------------------------------------------------------------
TOPIC_RULES: list[tuple[list[str], str]] = [
    # Chapter 03 – multisensory value
    (["economic value", "social-emotional", "cultural value"], "value"),
    # Chapter 04 – multisensory experience
    (["sensory substitution", "crossmodal", "multisensory attention",
      "holistic experiential", "latency tolerance", "tolerance of spatial",
      "prior experience", "perceptual", "filling in", "steady state",
      "watch-based haptic", "current, rising"], "multisensory-experience"),
    # Chapter 05 – vision
    (["flicker", "light and dark", "visual illusion", "colour blindness",
      "low vision", "lighting and brightness", "motion sensitivity",
      "cognitive load", "low spatial resolution", "abba voyage",
      "shinjuku", "3d digital signage"], "vision"),
    # Chapter 06 – hearing
    (["hearing diversity", "sound overload", "spatial audio",
      "in pursuit of repetitive beats", "jeff wayne", "arcade"], "hearing"),
    # Chapter 07 – touch
    (["active and passive", "temperature", "localisation", "social touch",
      "water droplets", "sensory and physical diversity", "assistive"], "touch"),
    # Chapter 08 – smell
    (["adaptation", "sensitivity", "fragrance", "impaired sense of smell",
      "jorvik"], "smell"),
    # Chapter 09 – sense of space
    (["presence", "spatial illusion", "motion sickness", "the matrix",
      "disney holotile", "shared reality", "cosm"], "space"),
    # Chapter 10 – personal and peripersonal space
    (["interpersonal space", "peripersonal space", "peripersonal space sensitivity",
      "managing the bubble"], "personal-space"),
    # Chapter 11 – interoception
    (["bodily signal", "individual differences", "data protection",
      "brainstorms"], "interoception"),
    # Chapter 12 – proprioception and body map
    (["masking bulky", "influencing strength", "proprioceptive diversity",
      "sensory mismatch", "body of mine"], "proprioception"),
    # Chapter 13 – interactivity
    (["full-body real-time", "motion capture", "physiological data",
      "alternate channels"], "interactivity"),
    # Shared headings that need context — best-guess defaults
    (["current technical challenges"], "touch"),     # appears in touch & smell chapters
    (["context"], "smell"),                           # "Context" is a smell sub-section
    (["diversity"], "personal-space"),                # "Diversity" is in ch10
    (["inclusion"], "multisensory-experience"),
    (["why multisensory", "design lessons", "what next"], "multisensory-experience"),
]


def infer_topic(heading_norm: str) -> str:
    for keywords, topic in TOPIC_RULES:
        if any(kw in heading_norm for kw in keywords):
            return topic
    return "multisensory-experience"  # safe fallback


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def clean_heading(heading: str) -> str:
    """Strip trailing read-time annotation, e.g. ' 6 min'."""
    return re.sub(r"\s+\d+\s+min\s*$", "", heading).strip()


def main() -> None:
    config_path = Path("analytics") / "tracked-blocks.yml"
    if not config_path.exists():
        sys.exit(f"Not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    blocks: list[dict] = raw.get("blocks", [])

    # Track used block_ids to avoid collisions within this run
    used_ids: set[str] = {b["block_id"] for b in blocks if b.get("block_id")}

    changed = 0
    for block in blocks:
        if block.get("block_id"):
            continue  # already configured

        label = clean_heading(block["heading"])
        heading_norm = label.lower()

        # Generate a unique block_id
        base_slug = slugify(label)
        slug = base_slug
        counter = 2
        while slug in used_ids:
            slug = f"{base_slug}-{counter}"
            counter += 1
        used_ids.add(slug)

        topic = infer_topic(heading_norm)

        block["block_id"] = slug
        block["label"] = label
        block["topic"] = topic
        block["concept"] = topic  # refine manually later if needed
        changed += 1

    raw["blocks"] = blocks
    config_path.write_text(
        yaml.dump(raw, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Done — populated {changed} entries in {config_path}")


if __name__ == "__main__":
    main()
