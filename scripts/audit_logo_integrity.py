#!/usr/bin/env python3
"""Audit conference-logo manifest entries for false-positive reuse.

This is intentionally separate from the crawler so it can be run after any
manifest generation pass, including batch merges. It checks machine-readable
false-positive overrides and heuristic risks that are easy to miss during
large-scale logo crawling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import re
from typing import Any


IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}
GENERIC_LOGO_STEMS = {
    "cloud",
    "logo",
    "brand",
    "banner",
    "header",
    "masthead",
    "image",
    "bg",
    "background",
}
SAFE_SHARED_STEMS = {
    # Known umbrella/joint-event assets can be added here after manual review.
}
SAFE_SHARED_HASH_TITLE_SETS = {
    frozenset({"EDBT", "ICDT"}),  # Joint EDBT/ICDT event branding.
}
SUSPICIOUS_SOURCE_TERMS = {
    "avatar",
    "background",
    "carousel",
    "cropped-ny",
    "exhibitor",
    "favicon",
    "gallery",
    "googleusercontent",
    "hero",
    "hotel",
    "openreview",
    "partner",
    "photo",
    "profile",
    "secunet",
    "slider",
    "speaker",
    "sponsor",
    "unsplash",
    "venue",
    "wikimedia",
}


def normalize(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def logo_stem(logo_file: str | None) -> str:
    if not logo_file:
        return ""
    name = Path(str(logo_file)).name
    suffix = Path(name).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        name = name[: -len(suffix)]
    name = re.sub(r"(?i)[-_ ]?logo$", "", name)
    name = re.sub(r"(?<!\d)(20[0-4]\d)(?!\d)", "", name)
    return name.strip(" -_")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def entry_key(entry: dict[str, Any]) -> tuple[str, str]:
    return (str(entry.get("source_path") or ""), str(entry.get("title") or ""))


def override_key(item: dict[str, Any]) -> tuple[str, str]:
    return (str(item.get("source_path") or ""), str(item.get("title") or ""))


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_None._\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        escaped = []
        for value in row:
            text = "" if value is None else str(value)
            escaped.append(text.replace("|", "\\|").replace("\n", " ").strip())
        lines.append("| " + " | ".join(escaped) + " |")
    return "\n".join(lines) + "\n"


def audit(manifest_path: Path, overrides_path: Path | None) -> tuple[str, int]:
    manifest = load_json(manifest_path)
    entries = [entry for entry in manifest.get("entries", []) if isinstance(entry, dict)]
    overrides_payload: dict[str, Any] = {}
    if overrides_path and overrides_path.exists():
        overrides_payload = load_json(overrides_path)

    confirmed_overrides = [
        item
        for item in overrides_payload.get("confirmed_bad_mappings", [])
        if isinstance(item, dict)
    ]
    high_review = [
        item
        for item in overrides_payload.get("high_confidence_manual_review", [])
        if isinstance(item, dict)
    ]
    by_key = {entry_key(entry): entry for entry in entries}

    confirmed_hits: list[list[Any]] = []
    for item in confirmed_overrides:
        entry = by_key.get(override_key(item))
        if not entry:
            continue
        bad_logo = str(item.get("bad_logo_file") or "")
        if bad_logo and str(entry.get("logo_file") or "") == bad_logo:
            confirmed_hits.append(
                [
                    item.get("title"),
                    item.get("source_path"),
                    bad_logo,
                    item.get("recommended_status"),
                    item.get("replacement_source_url"),
                    item.get("bad_reason"),
                ]
            )

    active_high_review: list[dict[str, Any]] = []
    for item in high_review:
        entry = by_key.get(override_key(item))
        if not entry:
            continue
        current_logo = str(item.get("current_logo_file") or "").strip()
        if current_logo and str(entry.get("logo_file") or "") != current_logo:
            continue
        active_high_review.append(item)

    logo_to_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        logo = str(entry.get("logo_file") or "").strip()
        if logo:
            logo_to_entries[logo].append(entry)

    shared_logo_warnings: list[list[Any]] = []
    for logo, users in sorted(logo_to_entries.items()):
        titles = sorted({str(entry.get("title") or "") for entry in users})
        if len(titles) <= 1:
            continue
        stem_key = normalize(logo_stem(logo))
        if stem_key in SAFE_SHARED_STEMS:
            continue
        shared_logo_warnings.append(
            [
                logo,
                ", ".join(titles),
                "; ".join(sorted({str(entry.get("source_path") or "") for entry in users})),
                "same logo_file used by multiple distinct conference titles",
            ]
        )

    asset_root = manifest_path.parent / "assets" / "logos"
    hash_to_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_url_warnings: list[list[Any]] = []
    acronym_warnings: list[list[Any]] = []
    for entry in entries:
        logo = str(entry.get("logo_file") or "").strip()
        title = str(entry.get("title") or "").strip()
        if not logo or not title:
            continue

        asset_path = asset_root / logo
        if asset_path.exists() and asset_path.is_file():
            digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
            hash_to_entries[digest].append(entry)

        source_url = str(entry.get("source_url") or "")
        source_url_key = source_url.lower()
        source_hits = sorted(term for term in SUSPICIOUS_SOURCE_TERMS if term in source_url_key)
        if source_hits:
            source_url_warnings.append(
                [
                    title,
                    entry.get("source_path"),
                    logo,
                    source_url,
                    ", ".join(source_hits),
                ]
            )

        title_key = normalize(title)
        stem = logo_stem(logo)
        stem_key = normalize(stem)
        if not stem_key or not title_key:
            continue
        context_keys = [
            normalize(str(entry.get("dblp") or "")),
            normalize(str(entry.get("description") or "")),
            normalize(str(entry.get("source_path") or "")),
        ]
        strong_match = (
            stem_key == title_key
            or stem_key.startswith(title_key)
            or title_key.startswith(stem_key)
            or any(stem_key and stem_key in key for key in context_keys)
        )
        is_generic = stem_key in GENERIC_LOGO_STEMS
        if (not strong_match) or is_generic:
            acronym_warnings.append(
                [
                    title,
                    entry.get("source_path"),
                    logo,
                    stem,
                    entry.get("official_link"),
                    "generic logo stem" if is_generic else "logo stem does not strongly match title/dblp/description/source_path",
                ]
            )

    duplicate_hash_warnings: list[list[Any]] = []
    for digest, users in sorted(hash_to_entries.items()):
        titles = sorted({str(entry.get("title") or "") for entry in users})
        if len(titles) <= 1:
            continue
        if frozenset(titles) in SAFE_SHARED_HASH_TITLE_SETS:
            continue
        duplicate_hash_warnings.append(
            [
                digest[:16],
                ", ".join(titles),
                ", ".join(sorted({str(entry.get("logo_file") or "") for entry in users})),
                "; ".join(sorted({str(entry.get("source_path") or "") for entry in users})),
                "same image bytes used by multiple distinct conference titles",
            ]
        )

    lines: list[str] = []
    lines.extend(
        [
            "# Conference Logo Integrity Audit",
            "",
            f"Manifest: `{manifest_path}`",
            f"Entries scanned: {len(entries)}",
            "",
            "## Confirmed bad mappings still present",
            "",
            markdown_table(
                ["Conference", "Source path", "Bad logo", "Recommended status", "Replacement source", "Reason"],
                confirmed_hits,
            ),
            "## Shared logo-file warnings",
            "",
            markdown_table(["Logo", "Conference titles", "Source paths", "Warning"], shared_logo_warnings),
            "## Duplicate content-hash warnings",
            "",
            markdown_table(
                ["Hash", "Conference titles", "Logo files", "Source paths", "Warning"],
                duplicate_hash_warnings,
            ),
            "## Suspicious source-url warnings",
            "",
            markdown_table(
                ["Conference", "Source path", "Logo", "Source URL", "Matched terms"],
                source_url_warnings,
            ),
            "## Acronym/generic-stem warnings",
            "",
            markdown_table(
                ["Conference", "Source path", "Logo", "Logo stem", "Official link", "Warning"],
                acronym_warnings,
            ),
        ]
    )
    if active_high_review:
        lines.extend(
            [
                "## High-confidence manual-review queue from overrides",
                "",
                markdown_table(
                    ["Conference", "Source path", "Current logo", "Risk", "Recommended action"],
                    [
                        [
                            item.get("title"),
                            item.get("source_path"),
                            item.get("current_logo_file"),
                            item.get("risk_reason"),
                            item.get("recommended_action"),
                        ]
                        for item in active_high_review
                    ],
                ),
            ]
        )

    exit_code = 1 if confirmed_hits else 0
    return "\n".join(lines).rstrip() + "\n", exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("manifest.json"))
    parser.add_argument(
        "--overrides", type=Path, default=Path("audit/false_positive_overrides.json")
    )
    parser.add_argument("--report", type=Path, help="Optional markdown report output path")
    parser.add_argument("--no-fail", action="store_true", help="Always exit 0")
    args = parser.parse_args()

    report, exit_code = audit(args.manifest, args.overrides)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0 if args.no_fail else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
