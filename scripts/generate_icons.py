"""Sinh bộ icon PNG PWA cho Quiz Test NMPP 2026 với tông xanh dương nhạt."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT_DIR / "icons"

SPECS = [
    ("apple-touch-icon.png", 180),
    ("icon-192.png", 192),
    ("icon-512.png", 512),
]


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def create_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Nền gradient xanh dương nhạt (#7dd3fc -> #0ea5e9)
    top_rgb = (125, 211, 252)
    bot_rgb = (2, 132, 199)
    for y in range(size):
        t = y / max(1, size - 1)
        r = int(top_rgb[0] * (1 - t) + bot_rgb[0] * t)
        g = int(top_rgb[1] * (1 - t) + bot_rgb[1] * t)
        b = int(top_rgb[2] * (1 - t) + bot_rgb[2] * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Vòng trang trí nhẹ phía sau
    glow_r = int(size * 0.42)
    draw.ellipse(
        [size - glow_r, -int(glow_r * 0.5), size + int(glow_r * 0.5), glow_r],
        fill=(255, 255, 255, 42),
    )
    draw.ellipse(
        [-int(glow_r * 0.45), size - glow_r, int(glow_r * 0.75), size + int(glow_r * 0.3)],
        fill=(224, 242, 254, 38),
    )

    # Nhãn QUIZ nhỏ phía trên
    font_top = load_font(max(12, int(size * 0.115)), bold=True)
    font_main = load_font(max(20, int(size * 0.27)), bold=True)
    font_year = load_font(max(13, int(size * 0.135)), bold=True)

    # Vẽ chữ căn giữa
    cx = size / 2
    draw.text((cx, size * 0.24), "QUIZ TEST", fill=(240, 249, 255, 235), font=font_top, anchor="mm")
    draw.text((cx, size * 0.51), "NMPP", fill=(255, 255, 255, 255), font=font_main, anchor="mm")

    # Viên thuốc năm 2026
    pill_w = int(size * 0.46)
    pill_h = int(size * 0.19)
    pill_x0 = int(cx - pill_w / 2)
    pill_y0 = int(size * 0.69)
    draw.rounded_rectangle(
        [pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h],
        radius=pill_h // 2,
        fill=(255, 255, 255, 235),
    )
    draw.text(
        (cx, pill_y0 + pill_h / 2),
        "2026",
        fill=(3, 105, 161, 255),
        font=font_year,
        anchor="mm",
    )

    return img


def main() -> int:
    try:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        for filename, size in SPECS:
            target = ICONS_DIR / filename
            tmp = target.with_suffix(".png.tmp")
            img = create_icon(size)
            try:
                img.save(tmp, format="PNG", optimize=True)
                tmp.replace(target)
            finally:
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
            print(f"Đã tạo icon: {target.name} ({size}x{size})")
        return 0
    except Exception as exc:
        print(f"Lỗi tạo icon: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
