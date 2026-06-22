#!/usr/bin/env python3
"""Generate the Open Graph / social-share card for the Multisensory Hub site.

Outputs static/img/social-card.jpg at 1200x630 (the standard OG ratio), using
the site's indigo brand palette. Re-run after changing the title/tagline.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- content -----------------------------------------------------------------
EYEBROW = "INTERACTIVE REPORT · COSTAR NATIONAL LAB"
TITLE = "Multisensory Hub"
TAGLINE = "Exploring the science of multisensory experiences"
URL = "multisensory.costarnetwork.co.uk"

# --- geometry ----------------------------------------------------------------
W, H = 1200, 630
MARGIN = 90

# --- brand palette (from src/css/custom.css) ---------------------------------
TOP = (55, 48, 163)       # #3730a3  primary-darkest
BOTTOM = (79, 70, 229)    # #4f46e5  primary-darker
ACCENT = (165, 180, 252)  # #a5b4fc  primary-lighter
WHITE = (255, 255, 255)
MUTED = (199, 210, 254)   # #c7d2fe  primary-lightest

OUT = Path(__file__).resolve().parents[1] / "static" / "img" / "social-card.jpg"

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def diagonal_gradient() -> Image.Image:
    """Indigo gradient running top-left (dark) to bottom-right (lighter)."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        ry = y / (H - 1)
        for x in range(W):
            t = ry * 0.65 + (x / (W - 1)) * 0.35
            px[x, y] = (
                int(TOP[0] + (BOTTOM[0] - TOP[0]) * t),
                int(TOP[1] + (BOTTOM[1] - TOP[1]) * t),
                int(TOP[2] + (BOTTOM[2] - TOP[2]) * t),
            )
    return img


def add_dot_grid(img: Image.Image) -> None:
    """Faintly lighten a dot grid for a precise, scholarly texture."""
    px = img.load()
    for y in range(70, H, 36):
        for x in range(70, W, 36):
            for dy in range(2):
                for dx in range(2):
                    r, g, b = px[x + dx, y + dy]
                    px[x + dx, y + dy] = (min(r + 16, 255), min(g + 16, 255), min(b + 26, 255))


def centered(draw: ImageDraw.ImageDraw, y: int, text: str,
             font: ImageFont.FreeTypeFont, fill) -> None:
    """Draw text horizontally centered on the canvas at vertical position y."""
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)


def main() -> None:
    img = diagonal_gradient()
    add_dot_grid(img)
    draw = ImageDraw.Draw(img)

    # Everything is centered and kept within a safe zone so platforms that
    # crop toward a square (Miro, iMessage, WhatsApp) don't clip the content.
    f_eyebrow = ImageFont.truetype(BOLD, 22)
    f_title = ImageFont.truetype(BOLD, 88)
    f_tag = ImageFont.truetype(REG, 36)
    f_url = ImageFont.truetype(BOLD, 26)

    centered(draw, 218, EYEBROW, f_eyebrow, ACCENT)
    centered(draw, 256, TITLE, f_title, WHITE)

    # Short accent underline, centered beneath the title.
    draw.rectangle([(W - 90) / 2, 372, (W + 90) / 2, 378], fill=ACCENT)

    centered(draw, 398, TAGLINE, f_tag, MUTED)
    centered(draw, H - MARGIN - 6, URL, f_url, ACCENT)

    img.save(OUT, "JPEG", quality=92, progressive=True)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
