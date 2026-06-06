#!/usr/bin/env python3
"""Generate yearly-refresh and white-logo watchlist report from manifest.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from PIL import Image


ACTIVE_STATUSES = {"downloaded", "existing_target", "reused_existing"}
YEAR_RE = re.compile(r"(?<!\d)(20[0-4]\d)(?!\d)")


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def collect_years(*values: str | None) -> set[int]:
    years: set[int] = set()
    for value in values:
        if not value:
            continue
        for match in YEAR_RE.finditer(str(value)):
            years.add(int(match.group(1)))
    return years


def is_active(entry: dict[str, Any]) -> bool:
    return entry.get("status") in ACTIVE_STATUSES and bool(entry.get("logo_file"))


def annual_reason(entry: dict[str, Any]) -> str | None:
    if not is_active(entry):
        return None
    year = entry.get("conference_year")
    try:
        year_int = int(year)
    except Exception:
        year_int = None
    years = collect_years(
        entry.get("source_url"),
        entry.get("official_link"),
        entry.get("page_title"),
        entry.get("logo_file"),
    )
    if year_int and year_int in years:
        return f"source contains latest conference year {year_int}"
    if years:
        return "source contains year marker " + ", ".join(str(value) for value in sorted(years))
    if entry.get("conference_place"):
        return "conference place/year metadata present"
    return None


def svg_white_signal(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    white_hints = text.count("#fff") + text.count("#ffffff") + text.count("white")
    dark_hints = text.count("#000") + text.count("#000000") + text.count("black")
    if white_hints and white_hints >= dark_hints:
        return f"svg-white-hints={white_hints}, dark-hints={dark_hints}"
    return None


def raster_white_signal(path: Path) -> str | None:
    try:
        image = Image.open(path).convert("RGBA")
    except Exception:
        return None
    width, height = image.size
    if not width or not height:
        return None
    if hasattr(image, "get_flattened_data"):
        pixels = list(image.get_flattened_data())
    else:
        pixels = list(image.getdata())
    visible = [pixel for pixel in pixels if pixel[3] >= 24]
    if not visible:
        return "transparent-or-empty"
    white = [
        pixel
        for pixel in visible
        if pixel[0] >= 235 and pixel[1] >= 235 and pixel[2] >= 235
    ]
    white_ratio = len(white) / len(visible)
    visible_area = len(visible) / len(pixels)
    if visible_area < 0.65 and white_ratio >= 0.68:
        return f"white_ratio={white_ratio:.2f}, visible_area={visible_area:.2f}"
    return None


def white_signal(path: Path) -> str | None:
    if path.suffix.lower() == ".svg":
        return svg_white_signal(path)
    return raster_white_signal(path)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(value) for value in row) + " |")
    return "\n".join(lines)


def generate_report(manifest_path: Path, logo_dir: Path, output_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    annual_rows: list[list[Any]] = []
    white_rows: list[list[Any]] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        reason = annual_reason(entry)
        if reason:
            annual_rows.append(
                [
                    entry.get("title"),
                    entry.get("ccf_rank"),
                    entry.get("conference_year"),
                    entry.get("conference_place"),
                    entry.get("logo_file"),
                    reason,
                    entry.get("source_url") or entry.get("official_link"),
                ]
            )
        logo_file = entry.get("logo_file")
        if is_active(entry) and logo_file:
            signal = white_signal(logo_dir / str(logo_file))
            if signal:
                white_rows.append(
                    [
                        entry.get("title"),
                        entry.get("ccf_rank"),
                        logo_file,
                        signal,
                        entry.get("source_url") or entry.get("official_link"),
                    ]
                )

    annual_rows.sort(key=lambda row: (str(row[1] or "Z"), str(row[0] or "")))
    white_rows.sort(key=lambda row: (str(row[1] or "Z"), str(row[0] or "")))

    lines = [
        "# Logo Refresh Focus Report",
        "",
        "Generated from `manifest.json` after applying manual overrides and false-positive skips.",
        "",
        "## Year / City / Venue Sensitive Logos",
        "",
        "These active logo records contain year markers and/or conference-place metadata. Prioritize them in monthly incremental refreshes.",
        "",
        markdown_table(
            ["Conference", "CCF", "Year", "Place", "Logo", "Reason", "Source"],
            annual_rows,
        ),
        "",
        "## White Or White-Transparent Logo Watchlist",
        "",
        "These assets may disappear on white backgrounds. Render them on dark backgrounds during visual QA before deleting or judging them blank.",
        "",
        markdown_table(["Conference", "CCF", "Logo", "Signal", "Source"], white_rows),
        "",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "annual_sensitive": len(annual_rows),
                "white_watchlist": len(white_rows),
                "output": str(output_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(root / "manifest.json"))
    parser.add_argument("--logo-dir", default=str(root / "assets" / "logos"))
    parser.add_argument(
        "--output", default=str(root / "reports" / "logo_update_focus_latest.md")
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generate_report(
        Path(args.manifest).resolve(),
        Path(args.logo_dir).resolve(),
        Path(args.output).resolve(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
