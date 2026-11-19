#!/usr/bin/env python3
"""Composite the gta6-meme-x-01 meme: AI Vice City background + real make.fun
ghost (press-kit asset) + programmatic storage bar + crisp text overlay.

Layout (1600x1600 canvas):
  - top text:    "GTA VI IS 212 GB."
  - ghost:       real mascot, floating above the storage bar, ~470px tall
  - bar labels:  "GTA VI" (left) / "EVERYTHING ELSE" (right)
  - storage bar: magenta fill 85% with "212 GB", dark remainder 15%
  - bottom text: "IT ATE MY WHOLE CONSOLE."
  - footer:      "MY AI AGENT ON make.fun PAID FOR THE SSD."
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1600
BG = "research/media-generation-vice-city-sunset-bg-0-43a677d4-5a6c-4a23-a335-19d1181c0d7d.png"
GHOST = "research/press/ghost-trimmed.png"
OUT = "meme-212gb-v2.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MAGENTA = (196, 28, 131)        # make.fun brand magenta #c41c83
BAR_BG = (22, 20, 34)           # dark bar background
WHITE = (255, 255, 255)
BLACK = (25, 20, 25)


def font(size):
    return ImageFont.truetype(FONT, size)


def draw_centered(draw, cx, y, text, fnt, stroke):
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2 - bbox[0], y - bbox[1]), text, font=fnt,
              fill=WHITE, stroke_width=stroke, stroke_fill=BLACK)


def fit_font(draw, text, max_width, start_size, stroke=0):
    """Largest font size (<= start_size) whose rendered width fits max_width."""
    size = start_size
    while size > 20:
        fnt = font(size)
        bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
        if bbox[2] - bbox[0] <= max_width:
            return fnt
        size -= 2
    return font(20)


def main():
    base = Image.open(BG).convert("RGB").resize((W, H), Image.LANCZOS)

    # --- subtle dark gradient at the top so the top text reads ---
    overlay = Image.new("L", (1, H))
    for y in range(H):
        # alpha 110 at y=0, fading to 0 by y=320
        overlay.putpixel((0, y), max(0, int(110 * (1 - y / 320))) if y < 320 else 0)
    overlay = overlay.resize((W, H))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    base = Image.composite(dark, base, overlay)

    draw = ImageDraw.Draw(base)

    # --- top text ---
    draw_centered(draw, W // 2, 55, "GTA VI IS 212 GB.",
                  fit_font(draw, "GTA VI IS 212 GB.", 1480, 140, 11), 11)

    # --- storage bar label above the bar, left only ("GTA VI") ---
    bar_x0, bar_x1 = 97, 1503
    bar_y0, bar_y1 = 1080, 1235
    draw.text((bar_x0, 1005), "GTA VI", font=font(58), fill=WHITE,
              stroke_width=4, stroke_fill=BLACK)

    # --- storage bar: dark shell + magenta fill (85%) ---
    draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=28,
                           fill=BAR_BG, outline=(255, 255, 255, 90), width=3)
    fill_w = int((bar_x1 - bar_x0) * 0.85)
    fill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fill_layer)
    fd.rounded_rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y1], radius=28,
                         fill=MAGENTA + (255,))
    # square off the fill's right edge (it is a fill level, not a pill)
    fd.rectangle([bar_x0 + fill_w - 28, bar_y0, bar_x0 + fill_w, bar_y1],
                 fill=MAGENTA + (255,))
    # clip the fill to the bar shell
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=28, fill=255)
    base.paste(Image.alpha_composite(base.convert("RGBA"), fill_layer)
               .convert("RGB"), (0, 0), mask)
    draw = ImageDraw.Draw(base)
    draw_centered(draw, bar_x0 + fill_w // 2, bar_y0 + 28, "212 GB",
                  font(88), 6)

    # --- soft contact shadow under the ghost, on the bar ---
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([W // 2 - 260, bar_y0 - 28, W // 2 + 260, bar_y0 + 34],
               fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base = Image.alpha_composite(base.convert("RGBA"), shadow)

    # --- ghost: real mascot, floating above the bar (raised clear of labels) ---
    ghost = Image.open(GHOST).convert("RGBA")
    gh = 470
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    gx = W // 2 - gw // 2
    gy = bar_y0 - 28 - gh + 40 - 120  # floats, clear of the bar labels
    base.alpha_composite(ghost, (gx, gy))
    base = base.convert("RGB")

    draw = ImageDraw.Draw(base)

    # --- "EVERYTHING ELSE" label below the bar's right end (under the sliver) ---
    lbl = "EVERYTHING ELSE"
    f_lbl = font(44)
    bbox = draw.textbbox((0, 0), lbl, font=f_lbl, stroke_width=3)
    draw.text((bar_x1 - (bbox[2] - bbox[0]), 1252), lbl, font=f_lbl,
              fill=WHITE, stroke_width=3, stroke_fill=BLACK)

    # --- bottom text + footer pitch ---
    bottom = "IT ATE MY WHOLE CONSOLE."
    draw_centered(draw, W // 2, 1330, bottom,
                  fit_font(draw, bottom, 1480, 110, 9), 9)
    draw_centered(draw, W // 2, 1480, "MY AI AGENT ON make.fun PAID FOR THE SSD.",
                  font(54), 5)

    base.save(OUT, "PNG")
    print("saved", OUT, base.size)
    # also a 480px preview: exactly what the judge sees (square at 480x480)
    base.resize((480, 480), Image.LANCZOS).save("meme-212gb-v2-480.png", "PNG")
    print("saved meme-212gb-v2-480.png (480x480 judge view)")


if __name__ == "__main__":
    main()
