#!/usr/bin/env python3
"""Generate the Open Graph / social-share card for the Multisensory Hub site.

Outputs static/img/social-card.jpg at 1200x630 (the standard OG ratio) on one
of the CoSTAR brand gradients supplied by CoSTAR comms (web-sized copies in
assets/). Default is Light A, a pale blush-grey; the National Lab orange is
also there. Re-run after changing the title/tagline, or pass another gradient:
    make_social_card.py assets/costar-gradient-national.jpg
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

# --- brand palette (CoSTAR, from src/css/custom.css) --------------------------
# All type is dark ink so it holds up on any of the light gradients.
INK = (16, 19, 20)        # #101314  heading colour
INK_SOFT = (60, 60, 64)   # softer dark for the tagline
WHITE = (255, 255, 255)

# CoSTAR logo-ray colours, used for the accent strip under the title
RAYS = [(0, 171, 214), (0, 81, 217), (239, 0, 89), (255, 87, 0), (255, 151, 1)]

HERE = Path(__file__).resolve().parent
GRADIENT = HERE / "assets" / "costar-gradient-light-a.jpg"
OUT = HERE.parent / "static" / "img" / "social-card.jpg"

# Optional overrides for trying other gradients: make_social_card.py <gradient> [<out>]
import sys
if len(sys.argv) > 1:
    GRADIENT = Path(sys.argv[1])
if len(sys.argv) > 2:
    OUT = Path(sys.argv[2])


def _first_existing(*paths: str) -> str:
    for p in paths:
        if Path(p).exists():
            return p
    raise FileNotFoundError(f"none of these fonts exist: {paths}")


BOLD = _first_existing(
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",   # macOS
    r"C:\Windows\Fonts\arialbd.ttf",                       # Windows
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
)
REG = _first_existing(
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def brand_gradient() -> Image.Image:
    """The chosen CoSTAR gradient, scaled to cover and centre-cropped to W x H."""
    src = Image.open(GRADIENT).convert("RGB")
    scale = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    left = (src.width - W) // 2
    top = (src.height - H) // 2
    return src.crop((left, top, left + W, top + H))


def centered(draw: ImageDraw.ImageDraw, y: int, text: str,
             font: ImageFont.FreeTypeFont, fill) -> None:
    """Draw text horizontally centered on the canvas at vertical position y."""
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)


def main() -> None:
    img = brand_gradient()
    draw = ImageDraw.Draw(img)

    # Everything is centered and kept within a safe zone so platforms that
    # crop toward a square (Miro, iMessage, WhatsApp) don't clip the content.
    f_eyebrow = ImageFont.truetype(BOLD, 22)
    f_title = ImageFont.truetype(BOLD, 88)
    f_tag = ImageFont.truetype(REG, 36)
    f_url = ImageFont.truetype(BOLD, 26)

    centered(draw, 218, EYEBROW, f_eyebrow, INK)
    centered(draw, 256, TITLE, f_title, INK)

    # Five-segment ray strip (CoSTAR logo colours), centered beneath the title.
    # Set on a white bar so the blue ray doesn't vanish into the blue gradient.
    seg, gap = 26, 6
    strip_w = 5 * seg + 4 * gap
    x0 = (W - strip_w) / 2
    draw.rectangle([x0 - gap, 369, x0 + strip_w + gap, 381], fill=WHITE)
    for i, colour in enumerate(RAYS):
        x = x0 + i * (seg + gap)
        draw.rectangle([x, 372, x + seg, 378], fill=colour)

    centered(draw, 398, TAGLINE, f_tag, INK_SOFT)
    centered(draw, H - MARGIN - 6, URL, f_url, INK)

    img.save(OUT, "JPEG", quality=92, progressive=True)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
