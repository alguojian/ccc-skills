from __future__ import annotations

import argparse
import math
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageFont

WIDTH = 2160
HEIGHT = 2880
NAVY = "#07142F"
TEAL = "#00D6C9"
BLUE = "#1B8CFF"
PURPLE = "#6A35FF"
WHITE = "#FFFFFF"
BG = "#F7F9FC"
BG2 = "#EAF0FA"

TITLE_KEYWORDS = [
    "工作流",
    "自动化",
    "提示词",
    "改得更",
    "一篇水文",
    "复盘",
    "实测",
    "避坑",
    "真正",
    "提效",
    "顺了",
    "别再",
    "AI",
]
TECH_TOKENS = ["Claude Code", "Claude", "ChatGPT", "Prompt", "MCP", "AI"]

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DEFAULT_OUTPUT = ROOT / "output" / "cover.png"
DEFAULT_TEMPLATE_REFERENCE = ASSETS / "template-reference.png"
DEFAULT_ROBOT_REFERENCE = ASSETS / "robot-reference.png"
DEFAULT_ROBOT = ASSETS / "robot-cube.png"
DEFAULT_BRAND_HEADER = ASSETS / "brand-header.png"

FONT_CANDIDATES_BOLD = [
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\Dengb.ttf"),
]
FONT_CANDIDATES_REGULAR = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\Deng.ttf"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
]


@dataclass
class LineLayout:
    text: str
    emphasize: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a digital project cover.")
    parser.add_argument("--title", help="Article title to render.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output PNG path.")
    parser.add_argument("--prepare-assets", action="store_true", help="Prepare local assets from reference images.")
    parser.add_argument("--template-reference", help="Path to the full template reference image.")
    parser.add_argument("--robot-reference", help="Path to the robot reference image.")
    return parser.parse_args()


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REGULAR
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    raise FileNotFoundError("No supported Chinese font found in C:\\Windows\\Fonts.")


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    rgb = ImageColor.getrgb(value)
    return (rgb[0], rgb[1], rgb[2], alpha)


def blend_color(start: str, end: str, t: float) -> tuple[int, int, int, int]:
    s = ImageColor.getrgb(start)
    e = ImageColor.getrgb(end)
    return (
        int(s[0] + (e[0] - s[0]) * t),
        int(s[1] + (e[1] - s[1]) * t),
        int(s[2] + (e[2] - s[2]) * t),
        255,
    )


def copy_reference(source: str | None, target: Path) -> None:
    if not source:
        return
    src = Path(source)
    if not src.exists():
        raise FileNotFoundError(f"Reference image not found: {src}")
    shutil.copyfile(src, target)


def remove_light_background(image: Image.Image, threshold: int = 244) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)
                continue
            avg = (r + g + b) / 3
            if avg > threshold - 10 and max(r, g, b) - min(r, g, b) < 16:
                fade = max(0, min(255, int((threshold - avg) * 24)))
                pixels[x, y] = (r, g, b, fade)
    return rgba


def trim_transparent(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def clear_low_alpha(image: Image.Image, cutoff: int = 5) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a < cutoff:
                pixels[x, y] = (r, g, b, 0)
    return rgba


def resize_contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def render_gradient_text_mask(
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    stroke_width: int = 0,
) -> tuple[Image.Image, tuple[int, int]]:
    temp = Image.new("L", (10, 10), 0)
    draw = ImageDraw.Draw(temp)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.text(
        (-bbox[0], -bbox[1]),
        text,
        fill=255,
        font=font,
        stroke_width=stroke_width,
    )
    return mask, (width, height)


def gradient_fill(size: tuple[int, int], colors: Sequence[str], diagonal: bool = False) -> Image.Image:
    width, height = size
    img = Image.new("RGBA", size)
    px = img.load()
    stops = [ImageColor.getrgb(color) for color in colors]
    for y in range(height):
        for x in range(width):
            pos = (x + y) / max(1, (width + height - 2)) if diagonal else x / max(1, width - 1)
            if len(stops) == 2:
                left, right = stops
                rgb = tuple(int(left[i] + (right[i] - left[i]) * pos) for i in range(3))
            else:
                segment = pos * (len(stops) - 1)
                idx = min(len(stops) - 2, int(segment))
                local = segment - idx
                rgb = tuple(
                    int(stops[idx][i] + (stops[idx + 1][i] - stops[idx][i]) * local) for i in range(3)
                )
            px[x, y] = (*rgb, 255)
    return img


def make_text_image(
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    fill: str = NAVY,
    gradient: bool = False,
    stroke_fill: str | None = None,
    stroke_width: int = 0,
    rotate: float = 0.0,
    shadow: bool = True,
) -> Image.Image:
    mask, size = render_gradient_text_mask(text, font, stroke_width=stroke_width)
    width, height = size
    if gradient:
        fill_layer = gradient_fill((width, height), [TEAL, BLUE, PURPLE], diagonal=False)
    else:
        fill_layer = Image.new("RGBA", (width, height), hex_rgba(fill))
    text_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_img.paste(fill_layer, (0, 0), mask)

    if stroke_fill and stroke_width > 0:
        outer_mask, outer_size = render_gradient_text_mask(text, font, stroke_width=stroke_width)
        stroke_img = Image.new("RGBA", outer_size, hex_rgba(stroke_fill))
        base = Image.new("RGBA", outer_size, (0, 0, 0, 0))
        base.paste(stroke_img, (0, 0), outer_mask)
        paste_x = (outer_size[0] - width) // 2
        paste_y = (outer_size[1] - height) // 2
        base.alpha_composite(text_img, (paste_x, paste_y))
        text_img = base

    if rotate:
        text_img = text_img.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)

    if shadow:
        shadow_layer = Image.new("RGBA", (text_img.width + 32, text_img.height + 32), (0, 0, 0, 0))
        shadow_mask = text_img.getchannel("A").filter(ImageFilter.GaussianBlur(10))
        shadow_img = Image.new("RGBA", text_img.size, hex_rgba("#6A35FF", 42))
        shadow_layer.paste(shadow_img, (16, 16), shadow_mask)
        shadow_layer.alpha_composite(text_img, (0, 0))
        text_img = shadow_layer

    return text_img


def draw_segment_line(
    line: str,
    font: ImageFont.FreeTypeFont,
    *,
    highlight_tokens: Iterable[str],
) -> Image.Image:
    tokens = sorted(highlight_tokens, key=len, reverse=True)
    cursor = 0
    segments: list[tuple[str, bool]] = []
    while cursor < len(line):
        matched = None
        for token in tokens:
            if line[cursor:].startswith(token):
                matched = token
                break
        if matched:
            segments.append((matched, True))
            cursor += len(matched)
        else:
            segments.append((line[cursor], False))
            cursor += 1

    segment_images = [
        make_text_image(text, font, fill=NAVY, gradient=highlight, shadow=True)
        for text, highlight in segments
        if text
    ]
    width = sum(img.width for img in segment_images)
    height = max(img.height for img in segment_images)
    line_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = 0
    for img in segment_images:
        y = height - img.height
        line_img.alpha_composite(img, (x, y))
        x += img.width
    return line_img


def visual_length(text: str) -> float:
    length = 0.0
    for token in re.findall(r"[A-Za-z0-9+#.]+|.", text):
        if re.fullmatch(r"[A-Za-z0-9+#.]+", token):
            length += max(1.4, len(token) * 0.58)
        else:
            length += 1.0
    return length


def split_balanced(title: str, line_count: int) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9+#.]+|.", title)
    if line_count <= 1 or len(tokens) <= 1:
        return [title]

    total = sum(visual_length(token) for token in tokens)
    targets = [total / line_count] * line_count
    lines: list[list[str]] = [[] for _ in range(line_count)]
    current_line = 0
    current_len = 0.0
    remaining_tokens = len(tokens)

    for token in tokens:
        token_len = visual_length(token)
        remaining_tokens -= 1
        must_keep = line_count - current_line - 1
        should_break = (
            current_line < line_count - 1
            and current_len >= targets[current_line]
            and remaining_tokens >= must_keep
        )
        if should_break and lines[current_line]:
            current_line += 1
            current_len = 0.0
        lines[current_line].append(token)
        current_len += token_len

    result = ["".join(parts).strip() for parts in lines if "".join(parts).strip()]
    return result or [title]


def choose_line_count(title: str) -> int:
    length = visual_length(title)
    if length <= 7:
        return 2
    if length <= 15:
        return 3
    if length <= 20:
        return 4
    return 5


def split_by_cover_pattern(title: str) -> tuple[list[str], int] | None:
    for marker in ("把", "让", "给"):
        marker_idx = title.find(marker)
        if marker_idx <= 0:
            continue
        prefix = title[: marker_idx + 1]
        remainder = title[marker_idx + 1 :]
        for verb in ("改", "做", "写", "变", "提", "省", "搞", "调", "顺", "拆", "讲", "学"):
            verb_idx = remainder.find(verb)
            if verb_idx <= 1:
                continue
            middle = remainder[:verb_idx]
            suffix = remainder[verb_idx:]
            if (
                2.0 <= visual_length(prefix) <= 7.5
                and 2.0 <= visual_length(middle) <= 8.0
                and 2.0 <= visual_length(suffix) <= 9.0
            ):
                return [prefix, middle, suffix], 1
    return None


def emphasize_index(lines: Sequence[str]) -> int:
    if not lines:
        return 0
    middle = (len(lines) - 1) / 2
    scores: list[float] = []
    for index, line in enumerate(lines):
        score = 0.0
        if any(keyword in line for keyword in TITLE_KEYWORDS):
            score += 10
        if any(token in line for token in TECH_TOKENS):
            score += 4
        score += max(0, 3 - abs(index - middle))
        length = visual_length(line)
        if 2.4 <= length <= 6.8:
            score += 2
        if len(lines) == 3 and index == 1:
            score += 2
        scores.append(score)
    return max(range(len(lines)), key=lambda idx: scores[idx])


def layout_title(title: str) -> list[LineLayout]:
    normalized = re.sub(r"\s+", "", title).strip()
    if not normalized:
        raise ValueError("Title cannot be empty.")
    patterned = split_by_cover_pattern(normalized)
    if patterned:
        lines, index = patterned
    else:
        count = choose_line_count(normalized)
        lines = split_balanced(normalized, count)
        index = emphasize_index(lines)
    return [LineLayout(text=line, emphasize=(idx == index)) for idx, line in enumerate(lines)]


def fit_font_size(text: str, *, base_size: int, max_width: int, bold: bool, min_size: int = 90) -> int:
    size = base_size
    while size >= min_size:
        font = load_font(size, bold=bold)
        mask, (width, _) = render_gradient_text_mask(text, font)
        if width <= max_width:
            return size
        size -= 8
    return min_size


def paint_soft_shape(
    base: Image.Image,
    *,
    box: tuple[int, int, int, int],
    radius: int,
    angle: float,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
    blur: int = 18,
) -> None:
    x0, y0, x1, y1 = box
    overlay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((0, 0, overlay.width - 1, overlay.height - 1), radius=radius, fill=fill, outline=outline, width=4)
    overlay = overlay.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    overlay = overlay.filter(ImageFilter.GaussianBlur(blur))
    overlay = clear_low_alpha(overlay, cutoff=8)
    px = x0 - (overlay.width - (x1 - x0)) // 2
    py = y0 - (overlay.height - (y1 - y0)) // 2
    base.alpha_composite(overlay, (px, py))


def create_background() -> Image.Image:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), hex_rgba(BG))
    base_gradient = gradient_fill((WIDTH, HEIGHT), [WHITE, BG2], diagonal=True).filter(ImageFilter.GaussianBlur(60))
    canvas.alpha_composite(base_gradient, (0, 0))

    top_glow = Image.new("RGBA", (760, 760), (0, 0, 0, 0))
    glow = ImageDraw.Draw(top_glow)
    glow.ellipse((0, 0, 760, 760), fill=hex_rgba(BLUE, 14))
    top_glow = top_glow.filter(ImageFilter.GaussianBlur(120))
    top_glow = clear_low_alpha(top_glow, cutoff=8)
    canvas.alpha_composite(top_glow, (-180, -160))

    bottom_glow = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    glow = ImageDraw.Draw(bottom_glow)
    glow.ellipse((0, 0, 900, 900), fill=hex_rgba(PURPLE, 18))
    bottom_glow = bottom_glow.filter(ImageFilter.GaussianBlur(160))
    bottom_glow = clear_low_alpha(bottom_glow, cutoff=8)
    canvas.alpha_composite(bottom_glow, (1320, 1940))

    paint_soft_shape(
        canvas,
        box=(1340, 110, 2140, 680),
        radius=160,
        angle=-24,
        fill=hex_rgba(WHITE, 52),
        outline=hex_rgba("#DCE7F8", 38),
        blur=34,
    )
    paint_soft_shape(
        canvas,
        box=(1380, 220, 2240, 760),
        radius=160,
        angle=-24,
        fill=hex_rgba(WHITE, 28),
        outline=hex_rgba("#EAF0FA", 26),
        blur=36,
    )
    paint_soft_shape(
        canvas,
        box=(140, 1750, 900, 2300),
        radius=132,
        angle=-24,
        fill=hex_rgba(WHITE, 30),
        outline=hex_rgba("#EAF0FA", 26),
        blur=42,
    )
    paint_soft_shape(
        canvas,
        box=(820, 2240, 1900, 2800),
        radius=220,
        angle=0,
        fill=hex_rgba(WHITE, 44),
        outline=hex_rgba("#EDF3FD", 24),
        blur=50,
    )
    return canvas


def build_brand_header(robot_icon: Image.Image) -> Image.Image:
    header = Image.new("RGBA", (820, 210), (0, 0, 0, 0))
    icon = resize_contain(robot_icon, (138, 138))
    shadow = Image.new("RGBA", (icon.width + 30, icon.height + 30), (0, 0, 0, 0))
    mask = icon.getchannel("A").filter(ImageFilter.GaussianBlur(12))
    shadow.paste(Image.new("RGBA", icon.size, hex_rgba(BLUE, 55)), (15, 18), mask)
    header.alpha_composite(shadow, (0, 10))
    header.alpha_composite(icon, (0, 0))

    font = load_font(86, bold=True)
    text_img = make_text_image("数字项目部", font, fill=NAVY, shadow=False)
    header.alpha_composite(text_img, (158, 14))

    underline = Image.new("RGBA", (240, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(underline)
    for x in range(underline.width):
        color = blend_color(TEAL, PURPLE, x / max(1, underline.width - 1))
        draw.rounded_rectangle((x, 0, x + 16, 12), radius=6, fill=color)
    underline = underline.filter(ImageFilter.GaussianBlur(0.5))
    header.alpha_composite(underline, (182, 132))

    return trim_transparent(header)


def draw_pill(canvas: Image.Image, text: str) -> None:
    pill = Image.new("RGBA", (360, 104), (0, 0, 0, 0))
    mask = Image.new("L", pill.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pill.width, pill.height), radius=52, fill=255)
    fill = gradient_fill(pill.size, [TEAL, BLUE, PURPLE])
    pill.paste(fill, (0, 0), mask)
    pill = pill.filter(ImageFilter.GaussianBlur(0.4))
    font = load_font(58, bold=True)
    text_img = make_text_image(text, font, fill=WHITE, shadow=False)
    x = (pill.width - text_img.width) // 2
    y = (pill.height - text_img.height) // 2 - 4
    pill.alpha_composite(text_img, (x, y))
    canvas.alpha_composite(pill, (1690, 124))


def draw_brand_area(canvas: Image.Image) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    line_y = 2420
    gradient_line = gradient_fill((360, 10), [TEAL, PURPLE])
    overlay.alpha_composite(gradient_line, (138, line_y))
    draw.ellipse((430, line_y - 10, 450, line_y + 10), fill=hex_rgba(PURPLE))

    title_font = load_font(88, bold=True)
    subtitle_font = load_font(56, bold=False)
    title_img = make_text_image("数字项目部", title_font, fill=NAVY, shadow=False)
    sub_img = make_text_image("用 AI 提升认知 · 用项目创造价值", subtitle_font, fill="#7180A0", shadow=False)
    overlay.alpha_composite(title_img, (140, 2510))
    overlay.alpha_composite(sub_img, (142, 2640))
    canvas.alpha_composite(overlay)


def draw_platform(canvas: Image.Image) -> None:
    platform = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(platform)
    center = (1630, 2460)
    for offset, alpha in [(0, 120), (34, 82), (76, 46)]:
        bbox = (
            center[0] - 420 - offset,
            center[1] - 150 - offset // 3,
            center[0] + 420 + offset,
            center[1] + 150 + offset // 3,
        )
        draw.ellipse(bbox, fill=hex_rgba(WHITE, alpha), outline=hex_rgba("#DCE7F8", max(26, alpha - 40)), width=6)

    ring = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.arc((1110, 2220, 2080, 2710), start=182, end=354, fill=hex_rgba(TEAL, 180), width=10)
    ring_draw.arc((1120, 2234, 2090, 2724), start=10, end=168, fill=hex_rgba(PURPLE, 150), width=8)
    ring = ring.filter(ImageFilter.GaussianBlur(1))
    canvas.alpha_composite(platform)
    canvas.alpha_composite(ring)


def draw_title_block(canvas: Image.Image, title: str) -> None:
    layout = layout_title(title)
    normal_size_map = {2: 304, 3: 268, 4: 230, 5: 194}
    focus_size_map = {2: 448, 3: 408, 4: 330, 5: 268}
    line_gap_map = {2: 34, 3: 30, 4: 28, 5: 24}
    count = len(layout)
    normal_base = normal_size_map.get(count, 190)
    focus_base = focus_size_map.get(count, 260)
    line_gap = line_gap_map.get(count, 24)
    max_width = 1600
    rendered: list[Image.Image] = []

    for line in layout:
        if line.emphasize:
            font_size = fit_font_size(line.text, base_size=focus_base, max_width=max_width, bold=True, min_size=160)
            font = load_font(font_size, bold=True)
            img = make_text_image(
                line.text,
                font,
                gradient=True,
                shadow=True,
                rotate=-3.2 if len(line.text) >= 3 else 0.0,
            )
        else:
            font_size = fit_font_size(line.text, base_size=normal_base, max_width=max_width, bold=True, min_size=120)
            font = load_font(font_size, bold=True)
            img = draw_segment_line(line.text, font, highlight_tokens=TECH_TOKENS)
        rendered.append(img)

    total_height = sum(img.height for img in rendered) + line_gap * (len(rendered) - 1)
    title_top = 430
    title_bottom = 1660
    y = title_top + (title_bottom - title_top - total_height) // 2

    emphasis_y = y
    for img, line in zip(rendered, layout):
        x = (WIDTH - img.width) // 2
        canvas.alpha_composite(img, (x, y))
        if line.emphasize:
            emphasis_y = y + img.height // 2
        y += img.height + line_gap

    accent = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(accent)
    brush_start_x = 160
    brush_y = max(800, emphasis_y + 34)
    for index in range(14):
        color = blend_color(TEAL, BLUE, index / 13)
        draw.line(
            (
                brush_start_x,
                brush_y + index * 3,
                brush_start_x + 380 - index * 12,
                brush_y - 24 + index,
            ),
            fill=color,
            width=18,
        )

    swoosh = Image.new("RGBA", (900, 220), (0, 0, 0, 0))
    swoosh_draw = ImageDraw.Draw(swoosh)
    for idx in range(10):
        color = blend_color(BLUE, PURPLE, idx / 9)
        swoosh_draw.arc((20, 50 + idx, 840, 200 + idx), start=200, end=332, fill=color, width=8)
    swoosh = swoosh.filter(ImageFilter.GaussianBlur(0.6))
    accent.alpha_composite(swoosh, (530, emphasis_y + 110))

    arrow = Image.new("RGBA", (360, 240), (0, 0, 0, 0))
    arrow_draw = ImageDraw.Draw(arrow)
    for idx in range(12):
        color = blend_color(TEAL, BLUE, idx / 11)
        arrow_draw.arc((20, 30 + idx, 300, 210 + idx), start=18, end=110, fill=color, width=8)
    arrow_draw.polygon([(282, 22), (345, 56), (296, 94)], fill=hex_rgba(TEAL))
    arrow = arrow.filter(ImageFilter.GaussianBlur(0.5))
    accent.alpha_composite(arrow, (1640, 1480))
    canvas.alpha_composite(accent)


def paste_robot(canvas: Image.Image, robot: Image.Image) -> None:
    robot_img = resize_contain(robot, (760, 760))
    shadow = Image.new("RGBA", (robot_img.width + 120, robot_img.height + 120), (0, 0, 0, 0))
    mask = robot_img.getchannel("A").filter(ImageFilter.GaussianBlur(36))
    shadow_color = Image.new("RGBA", robot_img.size, hex_rgba(PURPLE, 60))
    shadow.paste(shadow_color, (56, 66), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    shadow_x = 1260
    shadow_y = 1730
    canvas.alpha_composite(shadow, (shadow_x, shadow_y))
    canvas.alpha_composite(robot_img, (1320, 1780))


def prepare_assets(template_reference: str | None, robot_reference: str | None) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    copy_reference(template_reference, DEFAULT_TEMPLATE_REFERENCE)
    copy_reference(robot_reference, DEFAULT_ROBOT_REFERENCE)

    if not DEFAULT_ROBOT_REFERENCE.exists():
        raise FileNotFoundError("robot-reference.png is missing. Pass --robot-reference to prepare assets.")

    robot = Image.open(DEFAULT_ROBOT_REFERENCE).convert("RGBA")
    robot = remove_light_background(robot)
    robot = trim_transparent(robot)
    robot.save(DEFAULT_ROBOT)

    brand_header = build_brand_header(robot)
    brand_header.save(DEFAULT_BRAND_HEADER)


def render_cover(title: str, output_path: Path) -> Path:
    if not DEFAULT_ROBOT.exists() or not DEFAULT_BRAND_HEADER.exists():
        raise FileNotFoundError("Missing brand assets. Run --prepare-assets first.")

    canvas = create_background()
    draw_platform(canvas)

    brand_header = Image.open(DEFAULT_BRAND_HEADER).convert("RGBA")
    brand_header = resize_contain(brand_header, (760, 220))
    canvas.alpha_composite(brand_header, (104, 112))

    draw_pill(canvas, "AI 文章")
    draw_title_block(canvas, title)
    draw_brand_area(canvas)

    robot = Image.open(DEFAULT_ROBOT).convert("RGBA")
    paste_robot(canvas, robot)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = canvas.convert("RGB")
    if canvas.size != (WIDTH, HEIGHT):
        raise RuntimeError(f"Unexpected canvas size: {canvas.size}")
    canvas.save(output_path, format="PNG")
    return output_path


def main() -> int:
    args = parse_args()

    try:
        if args.prepare_assets:
            prepare_assets(args.template_reference, args.robot_reference)
            print(f"Prepared assets under {ASSETS}")
            if not args.title:
                return 0

        if not args.title:
            raise ValueError("--title is required unless you only run --prepare-assets.")

        output_path = Path(args.output).expanduser().resolve()
        render_cover(args.title, output_path)
        print(output_path)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
