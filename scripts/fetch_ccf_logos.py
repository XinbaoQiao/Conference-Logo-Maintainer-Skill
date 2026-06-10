#!/usr/bin/env python3
"""Fetch CCF conference logos from CCFDDL official-site links.

The script is intentionally conservative:
- CCFDDL YAML provides the conference list and latest official links.
- Existing local logo files are reused by default.
- Only high-confidence logo-like image candidates are downloaded.
- A manifest and update checklist are written for later incremental runs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import ProxyHandler, Request, build_opener

import yaml
from PIL import Image


CCFDDL_TREE_URL = (
    "https://api.github.com/repos/ccfddl/ccf-deadlines/git/trees/main?recursive=1"
)
RAW_BASE_URL = "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/"
USER_AGENT = (
    "Better-Poster-Skill CCF Logo Fetcher/1.0 "
    "(data source: https://github.com/ccfddl/ccf-deadlines)"
)
PROXY_ENV_VARS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "all_proxy",
    "ALL_PROXY",
)
IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"}
VECTOR_EXTENSIONS = {".svg"}
CCF_RANKS = {"A", "B", "C"}
YEAR_RE = re.compile(r"(?<!\d)(20[0-4]\d)(?!\d)")
URL_IN_CSS_RE = re.compile(r"url\((['\"]?)(.*?)\1\)", re.IGNORECASE)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def safe_stem(value: str) -> str:
    value = value.strip().replace("/", "-")
    value = re.sub(r"[\\:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ._-")
    return value or "conference"


def collect_years(*values: str | None) -> list[int]:
    years: set[int] = set()
    for value in values:
        if not value:
            continue
        for match in YEAR_RE.finditer(value):
            years.add(int(match.group(1)))
    return sorted(years)


def infer_extension(url: str, content_type: str | None, payload: bytes) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return ".jpg" if suffix == ".jpeg" else suffix
    content_type = (content_type or "").split(";", 1)[0].strip().lower()
    if content_type == "image/svg+xml" or payload.lstrip()[:120].lower().startswith(b"<svg"):
        return ".svg"
    guessed = mimetypes.guess_extension(content_type or "")
    if guessed:
        guessed = ".jpg" if guessed == ".jpeg" else guessed.lower()
        if guessed in IMAGE_EXTENSIONS:
            return guessed
    try:
        image = Image.open(io.BytesIO(payload))
        fmt = (image.format or "").lower()
        if fmt == "jpeg":
            return ".jpg"
        if fmt:
            ext = f".{fmt}"
            if ext in IMAGE_EXTENSIONS:
                return ext
    except Exception:
        pass
    return ".png"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class ConferencePageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[dict[str, str]] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = True
        if tag_lower in {"img", "source"}:
            for attr in ("src", "data-src", "data-original", "data-lazy-src"):
                self._add_url(tag_lower, attr, attrs_dict.get(attr, ""), attrs_dict)
            for attr in ("srcset", "data-srcset"):
                self._add_srcset(tag_lower, attr, attrs_dict.get(attr, ""), attrs_dict)
        elif tag_lower == "meta":
            prop = " ".join(
                [
                    attrs_dict.get("property", ""),
                    attrs_dict.get("name", ""),
                    attrs_dict.get("itemprop", ""),
                ]
            )
            if "image" in prop.lower():
                self._add_url(tag_lower, "content", attrs_dict.get("content", ""), attrs_dict)
        elif tag_lower == "link":
            rel = attrs_dict.get("rel", "").lower()
            if any(word in rel for word in ("icon", "image_src", "preload")):
                self._add_url(tag_lower, "href", attrs_dict.get("href", ""), attrs_dict)
        elif tag_lower == "a":
            href = attrs_dict.get("href", "")
            if Path(urlparse(href).path).suffix.lower() in IMAGE_EXTENSIONS:
                self._add_url(tag_lower, "href", href, attrs_dict)

        style = attrs_dict.get("style", "")
        if "url(" in style.lower():
            for match in URL_IN_CSS_RE.finditer(style):
                self._add_url(tag_lower, "style", match.group(2), attrs_dict)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def _add_srcset(
        self, tag: str, attr: str, value: str, attrs_dict: dict[str, str]
    ) -> None:
        if not value:
            return
        for part in value.split(","):
            url = part.strip().split(" ")[0]
            self._add_url(tag, attr, url, attrs_dict)

    def _add_url(
        self, tag: str, attr: str, value: str, attrs_dict: dict[str, str]
    ) -> None:
        value = html.unescape(value or "").strip()
        if not value or value.startswith("data:") or value.startswith("mailto:"):
            return
        descriptor = " ".join(
            [
                tag,
                attr,
                attrs_dict.get("alt", ""),
                attrs_dict.get("title", ""),
                attrs_dict.get("class", ""),
                attrs_dict.get("id", ""),
                attrs_dict.get("rel", ""),
                attrs_dict.get("aria-label", ""),
            ]
        )
        self.candidates.append({"url": value, "descriptor": descriptor})

    @property
    def page_title(self) -> str:
        return " ".join(part for part in self.title_parts if part).strip()


class Fetcher:
    def __init__(
        self,
        *,
        timeout: float,
        sleep: float,
        keep_proxy: bool,
        verbose: bool,
    ) -> None:
        self.timeout = timeout
        self.sleep = sleep
        self.verbose = verbose
        if not keep_proxy:
            for name in PROXY_ENV_VARS:
                os.environ.pop(name, None)
            self.opener = build_opener(ProxyHandler({}))
        else:
            self.opener = build_opener()

    def read_url(self, url: str, *, max_bytes: int | None = None) -> tuple[bytes, str | None]:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with self.opener.open(request, timeout=self.timeout) as response:
            content_type = response.headers.get("Content-Type")
            if max_bytes is None:
                payload = response.read()
            else:
                payload = response.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    raise ValueError(f"response exceeds {max_bytes} bytes")
            if self.sleep:
                time.sleep(self.sleep)
            return payload, content_type

    def read_text(self, url: str, *, max_bytes: int = 2_500_000) -> str:
        payload, content_type = self.read_url(url, max_bytes=max_bytes)
        encoding = "utf-8"
        if content_type and "charset=" in content_type:
            encoding = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
        return payload.decode(encoding or "utf-8", errors="replace")


def read_cached_text(
    fetcher: Fetcher,
    url: str,
    cache_path: Path | None,
    max_bytes: int,
    reuse_cache: bool,
) -> str:
    if reuse_cache and cache_path and cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    text = fetcher.read_text(url, max_bytes=max_bytes)
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
    return text


def load_ccfddl_conferences(
    fetcher: Fetcher,
    include_non_ccf: bool,
    limit: int,
    verbose: bool,
    cache_dir: Path | None,
    reuse_cache: bool,
) -> list[dict[str, Any]]:
    tree_cache = cache_dir / "github-tree.json" if cache_dir else None
    if reuse_cache and tree_cache and tree_cache.exists():
        tree = json.loads(tree_cache.read_text(encoding="utf-8"))
    else:
        payload, _ = fetcher.read_url(CCFDDL_TREE_URL)
        tree = json.loads(payload.decode("utf-8"))
        if tree_cache:
            tree_cache.parent.mkdir(parents=True, exist_ok=True)
            tree_cache.write_text(json.dumps(tree), encoding="utf-8")
    paths = [
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob"
        and re.fullmatch(r"conference/[A-Z]+/[^/]+\.yml", item.get("path", ""))
    ]
    conferences: list[dict[str, Any]] = []
    sorted_paths = sorted(paths)
    for path_index, path in enumerate(sorted_paths, start=1):
        if verbose:
            print(
                f"[metadata {path_index}/{len(sorted_paths)}] {path}",
                flush=True,
            )
        try:
            cache_path = cache_dir / path if cache_dir else None
            text = read_cached_text(
                fetcher,
                urljoin(RAW_BASE_URL, path),
                cache_path,
                max_bytes=500_000,
                reuse_cache=reuse_cache,
            )
            records = yaml.safe_load(text) or []
        except Exception as exc:
            conferences.append(
                {
                    "title": Path(path).stem.upper(),
                    "source_path": path,
                    "status": "metadata_error",
                    "error": str(exc),
                }
            )
            if limit and len(conferences) >= limit:
                return conferences[:limit]
            continue
        if isinstance(records, dict):
            records = [records]
        for record in records:
            if not isinstance(record, dict):
                continue
            rank = record.get("rank") or {}
            ccf_rank = str(rank.get("ccf", "")).strip().upper()
            if not include_non_ccf and ccf_rank not in CCF_RANKS:
                continue
            record = dict(record)
            record["source_path"] = path
            record["ccf_rank"] = ccf_rank or None
            conferences.append(record)
            if limit and len(conferences) >= limit:
                return conferences[:limit]
    return conferences


def normalize_records_from_yaml(
    text: str, source_path: str, include_non_ccf: bool
) -> list[dict[str, Any]]:
    records = yaml.safe_load(text) or []
    if isinstance(records, dict):
        records = [records]
    normalized: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        rank = record.get("rank") or {}
        ccf_rank = str(rank.get("ccf", "")).strip().upper()
        if not include_non_ccf and ccf_rank not in CCF_RANKS:
            continue
        item = dict(record)
        item["source_path"] = source_path
        item["ccf_rank"] = ccf_rank or None
        normalized.append(item)
    return normalized


def load_local_ccfddl_conferences(
    conference_dir: Path, include_non_ccf: bool, limit: int, verbose: bool
) -> list[dict[str, Any]]:
    paths = sorted(
        path
        for path in conference_dir.glob("[A-Z]*/*.yml")
        if path.is_file()
    )
    conferences: list[dict[str, Any]] = []
    for path_index, path in enumerate(paths, start=1):
        rel_path = f"conference/{path.relative_to(conference_dir).as_posix()}"
        if verbose:
            print(f"[metadata {path_index}/{len(paths)}] {rel_path}", flush=True)
        try:
            text = path.read_text(encoding="utf-8")
            records = normalize_records_from_yaml(text, rel_path, include_non_ccf)
        except Exception as exc:
            conferences.append(
                {
                    "title": path.stem.upper(),
                    "source_path": rel_path,
                    "status": "metadata_error",
                    "error": str(exc),
                }
            )
            records = []
        conferences.extend(records)
        if limit and len(conferences) >= limit:
            return conferences[:limit]
    return conferences


def latest_conference_instance(record: dict[str, Any]) -> dict[str, Any] | None:
    confs = [item for item in record.get("confs", []) if isinstance(item, dict)]
    with_link = [item for item in confs if item.get("link")]
    if not with_link:
        return None

    def year_value(item: dict[str, Any]) -> int:
        try:
            return int(item.get("year") or 0)
        except Exception:
            return 0

    return max(with_link, key=year_value)


def existing_logo_index(output_dir: Path) -> list[dict[str, Any]]:
    indexed: list[dict[str, Any]] = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.name in {"fetch_ccf_logos.py", "manifest.json", "update_list.md", "README.md"}:
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        quality = 0
        if path.suffix.lower() in VECTOR_EXTENSIONS:
            quality += 100
        else:
            try:
                image = Image.open(path)
                width, height = image.size
                quality += min(80, int((width * height) ** 0.5 / 10))
            except Exception:
                quality -= 50
        indexed.append(
            {
                "path": path,
                "stem_key": normalize_key(path.stem),
                "quality": quality,
            }
        )
    return indexed


def previous_manifest_index(output_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in payload.get("entries", []):
        if not isinstance(entry, dict):
            continue
        logo_file = entry.get("logo_file")
        digest = entry.get("sha256")
        if logo_file and digest:
            indexed[(str(logo_file), str(digest))] = entry
    return indexed


def previous_manifest_entry_index(output_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in payload.get("entries", []):
        if not isinstance(entry, dict):
            continue
        key = (str(entry.get("source_path") or ""), str(entry.get("title") or ""))
        if key[0] or key[1]:
            indexed[key] = entry
    return indexed


def load_manual_overrides(path_value: str) -> dict[tuple[str, str], dict[str, Any]]:
    if not path_value:
        return {}
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for item in payload.get("entries", []):
        if not isinstance(item, dict):
            continue
        key = (str(item.get("source_path") or ""), str(item.get("title") or ""))
        if key[0] and key[1]:
            indexed[key] = item
    return indexed


def load_false_positive_skips(path_value: str) -> dict[tuple[str, str], dict[str, Any]]:
    if not path_value:
        return {}
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for item in payload.get("confirmed_bad_mappings", []):
        if not isinstance(item, dict):
            continue
        if item.get("recommended_status") != "no_logo_candidate":
            continue
        key = (str(item.get("source_path") or ""), str(item.get("title") or ""))
        if key[0] and key[1]:
            indexed[key] = item
    return indexed


def base_entry_for_record(record: dict[str, Any]) -> dict[str, Any]:
    title = str(record.get("title") or "").strip()
    latest = latest_conference_instance(record)
    entry: dict[str, Any] = {
        "title": title,
        "description": record.get("description"),
        "ccf_rank": record.get("ccf_rank"),
        "sub": record.get("sub"),
        "dblp": record.get("dblp"),
        "source_path": record.get("source_path"),
    }
    if latest:
        entry.update(
            {
                "conference_year": latest.get("year"),
                "conference_id": latest.get("id"),
                "conference_date": latest.get("date"),
                "conference_place": latest.get("place"),
                "official_link": latest.get("link"),
                "observed_years": collect_years(
                    str(latest.get("link") or ""), str(latest.get("year") or "")
                ),
            }
        )
    return entry


def apply_false_positive_skip(
    *,
    record: dict[str, Any],
    false_positive: dict[str, Any],
    previous_entry: dict[str, Any] | None,
    output_dir: Path,
    protected_logos: set[str] | None = None,
) -> dict[str, Any]:
    entry = base_entry_for_record(record)
    cleanup_previous_logo(
        output_dir, previous_entry, keep_logo=None, protected_logos=protected_logos
    )
    entry.update(
        {
            "status": "no_logo_candidate",
            "source_kind": "confirmed_false_positive_skip",
            "source_url": None,
            "error": false_positive.get("bad_reason")
            or "Confirmed false-positive mapping; skip crawling and leave logo blank.",
            "manual_cleanup_note": false_positive.get("replacement_confirmation"),
            "replaced_logo_file": false_positive.get("bad_logo_file"),
        }
    )
    if false_positive.get("replacement_source_url"):
        entry["manual_official_url"] = false_positive.get("replacement_source_url")
    return entry


def cleanup_previous_logo(
    output_dir: Path,
    previous_entry: dict[str, Any] | None,
    keep_logo: str | None,
    protected_logos: set[str] | None = None,
) -> None:
    old_logo = str((previous_entry or {}).get("logo_file") or "").strip()
    if not old_logo or old_logo == keep_logo:
        return
    if old_logo in (protected_logos or set()):
        return
    old_path = output_dir / old_logo
    if old_path.exists() and old_path.is_file():
        old_path.unlink()


def apply_manual_override(
    fetcher: Fetcher,
    *,
    record: dict[str, Any],
    override: dict[str, Any],
    previous_entry: dict[str, Any] | None,
    output_dir: Path,
    protected_logos: set[str] | None = None,
) -> dict[str, Any]:
    entry = base_entry_for_record(record)
    action = str(override.get("action") or "").strip()
    entry["manual_override_action"] = action
    entry["manual_override_note"] = override.get("note")

    if action == "manual_skip":
        cleanup_previous_logo(
            output_dir, previous_entry, keep_logo=None, protected_logos=protected_logos
        )
        entry.update(
            {
                "status": "no_logo_candidate",
                "source_kind": "manual_skip",
                "source_url": None,
                "error": "Manual correction provides only a conference URL; skip crawling and leave logo blank.",
            }
        )
        if override.get("official_url"):
            entry["manual_official_url"] = override.get("official_url")
        return entry

    if action != "exact_logo":
        entry.update(
            {
                "status": "metadata_error",
                "source_kind": "manual_override",
                "error": f"Unsupported manual override action: {action}",
            }
        )
        return entry

    logo_urls = manual_logo_urls_for_record(record, override)
    if not logo_urls:
        entry.update(
            {
                "status": "metadata_error",
                "source_kind": "manual_exact_logo",
                "error": "Manual exact-logo override is missing logo_url.",
            }
        )
        return entry

    fetch_errors: list[str] = []
    payload: bytes | None = None
    content_type: str | None = None
    metadata: dict[str, Any] | None = None
    logo_url = ""
    for candidate_url in logo_urls:
        try:
            payload, content_type = fetcher.read_url(candidate_url, max_bytes=8_000_000)
            metadata = validate_image(payload, candidate_url, content_type)
            if not metadata:
                raise ValueError("manual logo URL did not return a valid logo image")
            logo_url = candidate_url
            break
        except Exception as exc:
            fetch_errors.append(f"{candidate_url}: {exc}")
    if payload is None or metadata is None or not logo_url:
        entry.update(
            {
                "status": "page_error",
                "source_kind": "manual_exact_logo",
                "source_url": logo_urls[0],
                "error": "; ".join(fetch_errors),
            }
        )
        return entry

    filename = str(override.get("logo_file") or "").strip()
    if not filename:
        filename = f"{safe_stem(str(entry.get('title') or 'conference'))}{metadata['extension']}"
    target = output_dir / filename
    target.write_bytes(payload)
    cleanup_previous_logo(
        output_dir, previous_entry, keep_logo=target.name, protected_logos=protected_logos
    )
    entry.update(
        {
            "status": "downloaded",
            "logo_file": target.name,
            "sha256": sha256_bytes(payload),
            "source_url": logo_url,
            "source_kind": "manual_exact_logo",
            "width": metadata.get("width"),
            "height": metadata.get("height"),
            "mime": metadata.get("mime"),
            "asset_years": collect_years(logo_url, target.name),
        }
    )
    if override.get("annual_url_template"):
        entry["annual_url_template"] = override.get("annual_url_template")
    return entry


def render_annual_url_template(template: str, record: dict[str, Any]) -> str | None:
    latest = latest_conference_instance(record) or {}
    year_value = latest.get("year")
    try:
        year = int(year_value)
    except Exception:
        return None
    replacements = {
        "year": str(year),
        "yy": f"{year % 100:02d}",
        "upload_year": str(year - 1),
    }
    try:
        return template.format(**replacements)
    except KeyError:
        return None


def manual_logo_urls_for_record(record: dict[str, Any], override: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    template = str(override.get("annual_url_template") or "").strip()
    if template:
        rendered = render_annual_url_template(template, record)
        if rendered:
            urls.append(rendered)
    fallback = str(override.get("logo_url") or "").strip()
    if fallback and fallback not in urls:
        urls.append(fallback)
    return urls


def find_existing_logo(
    indexed: list[dict[str, Any]], title: str, aliases: list[str]
) -> Path | None:
    title_key = normalize_key(title)
    alias_keys = [normalize_key(value) for value in aliases if value]
    alias_keys = [key for key in alias_keys if key]
    matches: list[dict[str, Any]] = []
    for item in indexed:
        stem_key = item["stem_key"]
        title_hit = bool(
            title_key
            and (
                stem_key == title_key
                or stem_key == f"{title_key}logo"
            )
        )
        alias_hit = any(
            stem_key == key or stem_key == f"{key}logo" for key in alias_keys
        )
        if title_hit or alias_hit:
            matches.append(item)
    if not matches:
        return None
    matches.sort(key=lambda item: item["quality"], reverse=True)
    return matches[0]["path"]


def aliases_for(record: dict[str, Any]) -> list[str]:
    aliases = []
    for key in ("dblp", "description"):
        value = record.get(key)
        if isinstance(value, str):
            aliases.append(value)
    title = record.get("title")
    description = record.get("description")
    if isinstance(title, str) and isinstance(description, str):
        aliases.append(f"{title} {description}")
    return aliases


def candidate_base_score(candidate: dict[str, str], page_url: str, title: str, aliases: list[str]) -> int:
    absolute = urljoin(page_url, candidate["url"])
    parsed = urlparse(absolute)
    path_text = Path(parsed.path).name.lower()
    descriptor = candidate.get("descriptor", "").lower()
    text = f"{path_text} {parsed.query.lower()} {descriptor}"
    negative_text = f"{parsed.path.lower()} {descriptor}"
    normalized_text = normalize_key(text)
    title_match = False
    score = 0
    if "logo" in text:
        score += 80
    if any(word in text for word in ("wordmark", "masthead")):
        score += 45
    if "brand" in text:
        score += 20
    for value in [title, *aliases]:
        key = normalize_key(value)
        if key and len(key) >= 3 and key in normalized_text:
            title_match = True
            score += 90
            break
    header_context = any(
        word in text
        for word in (
            "site-logo",
            "custom-logo",
            "main-logo",
            "navbar",
            "header",
            "masthead",
            "logo-header",
        )
    )
    if "logo" in text and not title_match and not header_context:
        score -= 85
    if "brand" in text and not title_match and not header_context:
        score -= 70
    if "img" in descriptor:
        score += 10
    if parsed.path.lower().endswith(".svg"):
        score += 35
    if any(word in text for word in ("favicon", "apple-touch-icon", "touch-icon")):
        score -= 75
    if any(
        word in negative_text
        for word in (
            "sponsor",
            "partner",
            "supporter",
            "exhibitor",
            "slider",
            "carousel",
            "hero",
            "background",
            "venue",
            "card",
            "close",
            "search",
            "menu",
            "arrow",
        )
    ):
        score -= 180
    if any(word in text for word in ("avatar", "profile", "photo", "speaker")):
        score -= 60
    if any(word in negative_text for word in ("banner", "photo", "gallery")):
        score -= 90
    return score


def unique_candidates(
    candidates: list[dict[str, str]], page_url: str, title: str, aliases: list[str], limit: int
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    ranked: list[dict[str, Any]] = []
    for candidate in candidates:
        absolute = urljoin(page_url, candidate["url"])
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        absolute = absolute.split("#", 1)[0]
        if re.search(r"\s", absolute):
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        score = candidate_base_score(candidate, page_url, title, aliases)
        if score <= -40:
            continue
        ranked.append({"url": absolute, "descriptor": candidate["descriptor"], "score": score})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]


def svg_dimensions(payload: bytes) -> tuple[int | None, int | None]:
    text = payload[:4096].decode("utf-8", errors="ignore")
    width = None
    height = None
    width_match = re.search(r'\bwidth=["\']?([0-9.]+)', text)
    height_match = re.search(r'\bheight=["\']?([0-9.]+)', text)
    if width_match:
        width = int(float(width_match.group(1)))
    if height_match:
        height = int(float(height_match.group(1)))
    viewbox_match = re.search(r'\bviewBox=["\']([^"\']+)["\']', text)
    if viewbox_match and (width is None or height is None):
        parts = re.split(r"[\s,]+", viewbox_match.group(1).strip())
        if len(parts) == 4:
            try:
                width = width or int(float(parts[2]))
                height = height or int(float(parts[3]))
            except Exception:
                pass
    return width, height


def validate_image(payload: bytes, url: str, content_type: str | None) -> dict[str, Any] | None:
    ext = infer_extension(url, content_type, payload)
    if ext == ".svg":
        lower = payload[:2048].lower()
        if b"<svg" not in lower:
            return None
        width, height = svg_dimensions(payload)
        return {
            "extension": ".svg",
            "mime": "image/svg+xml",
            "width": width,
            "height": height,
            "vector": True,
        }
    try:
        image = Image.open(io.BytesIO(payload))
        width, height = image.size
        if width < 48 or height < 32 or max(width, height) < 96:
            return None
        if width * height > 50_000_000:
            return None
        fmt = (image.format or "").lower()
        return {
            "extension": ".jpg" if fmt == "jpeg" else ext,
            "mime": content_type,
            "width": width,
            "height": height,
            "vector": False,
        }
    except Exception:
        return None


def image_score(base_score: int, metadata: dict[str, Any], url: str) -> int:
    score = base_score
    if metadata.get("vector"):
        score += 70
    width = metadata.get("width") or 0
    height = metadata.get("height") or 0
    if width and height:
        side_score = min(70, int((width * height) ** 0.5 / 8))
        score += side_score
        ratio = max(width / max(height, 1), height / max(width, 1))
        if ratio > 8:
            score -= 25
    lower = url.lower()
    if any(word in lower for word in ("favicon", "apple-touch-icon", "touch-icon")):
        score -= 90
    return score


def fetch_logo_for_conference(
    fetcher: Fetcher,
    *,
    record: dict[str, Any],
    output_dir: Path,
    overwrite: bool,
    candidate_limit: int,
) -> dict[str, Any]:
    title = str(record.get("title") or "").strip()
    latest = latest_conference_instance(record)
    if not latest:
        return {
            "title": title,
            "status": "missing_link",
            "ccf_rank": record.get("ccf_rank"),
            "source_path": record.get("source_path"),
            "error": "No conference link in CCFDDL record.",
        }
    page_url = str(latest.get("link"))
    conference_year = latest.get("year")
    aliases = aliases_for(record)
    result: dict[str, Any] = {
        "title": title,
        "description": record.get("description"),
        "ccf_rank": record.get("ccf_rank"),
        "sub": record.get("sub"),
        "dblp": record.get("dblp"),
        "source_path": record.get("source_path"),
        "conference_year": conference_year,
        "conference_id": latest.get("id"),
        "conference_date": latest.get("date"),
        "conference_place": latest.get("place"),
        "official_link": page_url,
    }
    try:
        html_text = fetcher.read_text(page_url)
    except Exception as exc:
        result.update(
            {
                "status": "page_error",
                "error": str(exc),
                "observed_years": collect_years(page_url, str(conference_year)),
            }
        )
        return result

    parser = ConferencePageParser()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    page_title = parser.page_title
    ranked = unique_candidates(parser.candidates, page_url, title, aliases, candidate_limit)
    result["page_title"] = page_title
    result["candidate_count"] = len(parser.candidates)
    result["ranked_candidate_count"] = len(ranked)
    result["observed_years"] = collect_years(
        page_url, page_title, html_text[:25_000], str(conference_year)
    )

    best: dict[str, Any] | None = None
    errors: list[str] = []
    for candidate in ranked:
        try:
            payload, content_type = fetcher.read_url(candidate["url"], max_bytes=8_000_000)
            metadata = validate_image(payload, candidate["url"], content_type)
            if not metadata:
                errors.append(f"rejected {candidate['url']}")
                continue
            scored = dict(candidate)
            scored.update(metadata)
            scored["payload"] = payload
            scored["content_type"] = content_type
            scored["score"] = image_score(candidate["score"], metadata, candidate["url"])
            if best is None or scored["score"] > best["score"]:
                best = scored
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            errors.append(f"{candidate['url']}: {exc}")

    if not best:
        result.update(
            {
                "status": "no_logo_candidate",
                "error": "; ".join(errors[:5]) or "No usable logo-like image candidates.",
                "candidate_urls": [item["url"] for item in ranked[:8]],
            }
        )
        return result

    ext = best["extension"]
    filename_stem = safe_stem(title)
    if record.get("duplicate_title") and record.get("sub"):
        filename_stem = f"{filename_stem}-{safe_stem(str(record.get('sub')))}"
    filename = f"{filename_stem}{ext}"
    target = output_dir / filename
    if target.exists() and not overwrite:
        digest = sha256_bytes(target.read_bytes())
        result.update(
            {
                "status": "existing_target",
                "logo_file": target.name,
                "sha256": digest,
                "source_url": best["url"],
                "source_kind": "official_site_candidate",
                "width": best.get("width"),
                "height": best.get("height"),
                "mime": best.get("mime"),
                "score": best.get("score"),
                "asset_years": collect_years(best["url"], target.name),
            }
        )
        return result

    payload = best.pop("payload")
    target.write_bytes(payload)
    result.update(
        {
            "status": "downloaded",
            "logo_file": target.name,
            "sha256": sha256_bytes(payload),
            "source_url": best["url"],
            "source_kind": "official_site_candidate",
            "width": best.get("width"),
            "height": best.get("height"),
            "mime": best.get("mime"),
            "score": best.get("score"),
            "asset_years": collect_years(best["url"], target.name),
        }
    )
    return result


def annual_update_reason(item: dict[str, Any]) -> str | None:
    if item.get("status") not in {"downloaded", "existing_target", "reused_existing"}:
        return None
    if not item.get("logo_file"):
        return None
    year = item.get("conference_year")
    try:
        year_int = int(year)
    except Exception:
        year_int = None
    source_values = [
        item.get("source_url"),
        item.get("official_link"),
        item.get("page_title"),
        item.get("logo_file"),
    ]
    years = set(collect_years(*[str(value) for value in source_values if value]))
    if year_int and year_int in years:
        return f"source contains latest conference year {year_int}"
    if years:
        return "source contains year marker " + ", ".join(str(value) for value in sorted(years))
    if item.get("status") == "reused_existing":
        link = str(item.get("official_link") or "")
        if re.search(r"(?:19|20)\d\d", link):
            return "existing local asset reused while latest official link is year-specific"
    if item.get("logo_file") and item.get("conference_place"):
        return "conference place/year metadata present"
    return None


def write_manifest(
    output_dir: Path,
    entries: list[dict[str, Any]],
    started_at: str,
    manifest_name: str = "manifest.json",
) -> None:
    summary: dict[str, int] = {}
    for item in entries:
        summary[item.get("status", "unknown")] = summary.get(item.get("status", "unknown"), 0) + 1
        reason = annual_update_reason(item)
        item["needs_annual_update"] = bool(reason)
        if reason:
            item["annual_update_reason"] = reason
    payload = {
        "generated_at": now_iso(),
        "started_at": started_at,
        "data_source": {
            "ccfddl_tree": CCFDDL_TREE_URL,
            "ccfddl_raw_base": RAW_BASE_URL,
        },
        "summary": summary,
        "entries": entries,
    }
    (output_dir / manifest_name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def markdown_table(headers: list[str], rows: list[list[Any]], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return "_None._\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def write_update_list(
    output_dir: Path, entries: list[dict[str, Any]], update_list_name: str = "update_list.md"
) -> None:
    annual = [
        item
        for item in entries
        if item.get("needs_annual_update")
        and item.get("status") in {"downloaded", "reused_existing", "existing_target"}
    ]
    missing = [
        item
        for item in entries
        if item.get("status")
        in {"page_error", "no_logo_candidate", "missing_link", "metadata_error"}
    ]
    stable = [
        item
        for item in entries
        if item.get("status") in {"downloaded", "reused_existing", "existing_target"}
        and not item.get("needs_annual_update")
    ]
    annual.sort(key=lambda item: (item.get("ccf_rank") or "Z", item.get("title") or ""))
    missing.sort(key=lambda item: (item.get("ccf_rank") or "Z", item.get("title") or ""))
    stable.sort(key=lambda item: (item.get("ccf_rank") or "Z", item.get("title") or ""))

    lines = [
        "# CCF Conference Logo Update List",
        "",
        f"Generated at: {now_iso()}",
        "",
        "Data source: CCFDDL conference YAML from https://github.com/ccfddl/ccf-deadlines",
        "",
        "## Need Annual Review",
        "",
        "These logos or their source pages include a year marker, so rerun the fetcher when the next edition is announced.",
        "",
        markdown_table(
            ["Conference", "CCF", "Year", "Logo", "Reason", "Official link"],
            [
                [
                    item.get("title"),
                    item.get("ccf_rank"),
                    item.get("conference_year"),
                    item.get("logo_file"),
                    item.get("annual_update_reason"),
                    item.get("official_link"),
                ]
                for item in annual
            ],
        ),
        "## Missing Or Needs Manual Check",
        "",
        "These entries did not produce a high-confidence logo candidate automatically.",
        "",
        markdown_table(
            ["Conference", "CCF", "Year", "Status", "Error", "Official link"],
            [
                [
                    item.get("title"),
                    item.get("ccf_rank"),
                    item.get("conference_year"),
                    item.get("status"),
                    item.get("error"),
                    item.get("official_link"),
                ]
                for item in missing
            ],
        ),
        "## Stable Or Low-Frequency Review",
        "",
        "These entries have an existing or downloaded logo with no year marker detected in the selected source.",
        "",
        markdown_table(
            ["Conference", "CCF", "Year", "Logo", "Status", "Source"],
            [
                [
                    item.get("title"),
                    item.get("ccf_rank"),
                    item.get("conference_year"),
                    item.get("logo_file"),
                    item.get("status"),
                    item.get("source_url") or item.get("source_kind"),
                ]
                for item in stable
            ],
        ),
    ]
    (output_dir / update_list_name).write_text("\n".join(lines), encoding="utf-8")


def merge_manifest_files(output_dir: Path, pattern: str) -> int:
    entries_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    started_at = now_iso()
    paths = sorted(glob.glob(pattern))
    if not paths:
        paths = sorted(str(path) for path in output_dir.glob(pattern))
    for manifest_path in paths:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        started_at = min(started_at, str(payload.get("started_at") or started_at))
        for entry in payload.get("entries", []):
            if not isinstance(entry, dict):
                continue
            key = (str(entry.get("source_path") or ""), str(entry.get("title") or ""))
            entries_by_key[key] = entry
    entries = sorted(
        entries_by_key.values(),
        key=lambda item: (
            item.get("source_path") or "",
            item.get("title") or "",
        ),
    )
    write_manifest(output_dir, entries, started_at)
    write_update_list(output_dir, entries)
    summary: dict[str, int] = {}
    for item in entries:
        summary[item.get("status", "unknown")] = summary.get(item.get("status", "unknown"), 0) + 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def process_conferences(args: argparse.Namespace) -> int:
    output_dir = Path(args.output).resolve()
    metadata_dir = Path(args.metadata_output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    if args.merge_manifest_glob:
        return merge_manifest_files(metadata_dir, args.merge_manifest_glob)
    started_at = now_iso()
    metadata_limit = 0
    fetcher = Fetcher(
        timeout=args.timeout,
        sleep=args.sleep,
        keep_proxy=args.keep_proxy,
        verbose=args.verbose,
    )
    if args.ccfddl_dir:
        conferences = load_local_ccfddl_conferences(
            Path(args.ccfddl_dir).expanduser().resolve(),
            include_non_ccf=args.include_non_ccf,
            limit=metadata_limit,
            verbose=args.verbose,
        )
    else:
        conferences = load_ccfddl_conferences(
            fetcher,
            include_non_ccf=args.include_non_ccf,
            limit=metadata_limit,
            verbose=args.verbose,
            cache_dir=Path(args.ccfddl_cache_dir).expanduser().resolve()
            if args.ccfddl_cache_dir
            else None,
            reuse_cache=args.reuse_ccfddl_cache,
        )
    title_counts: dict[str, int] = {}
    for record in conferences:
        title_key = normalize_key(str(record.get("title") or ""))
        if title_key:
            title_counts[title_key] = title_counts.get(title_key, 0) + 1
    for record in conferences:
        title_key = normalize_key(str(record.get("title") or ""))
        record["duplicate_title"] = bool(title_key and title_counts.get(title_key, 0) > 1)
    existing = existing_logo_index(output_dir)
    previous_manifest = previous_manifest_index(metadata_dir)
    previous_entries = previous_manifest_entry_index(metadata_dir)
    selected_keys: set[tuple[str, str]] | None = None
    if args.only_annual_update:
        selected_keys = {
            key
            for key, entry in previous_entries.items()
            if entry.get("needs_annual_update") and entry.get("logo_file")
        }
        if not selected_keys:
            print("No previous annual-update targets found; nothing to refresh.")
            entries = list(previous_entries.values())
            write_manifest(metadata_dir, entries, started_at, args.manifest_name)
            write_update_list(metadata_dir, entries, args.update_list_name)
            return 0
        conferences = [
            record
            for record in conferences
            if (str(record.get("source_path") or ""), str(record.get("title") or "").strip())
            in selected_keys
        ]
    if args.offset or args.limit:
        start = max(args.offset, 0)
        end = start + args.limit if args.limit else None
        conferences = conferences[start:end]
    previous_logo_counts: dict[str, int] = {}
    for previous_entry in previous_entries.values():
        logo = str(previous_entry.get("logo_file") or "").strip()
        if logo:
            previous_logo_counts[logo] = previous_logo_counts.get(logo, 0) + 1
    protected_logos = {
        logo for logo, count in previous_logo_counts.items() if count > 1
    }
    manual_overrides = load_manual_overrides(args.manual_overrides)
    false_positive_skips = load_false_positive_skips(args.false_positive_overrides)
    entries: list[dict[str, Any]] = []
    for index, record in enumerate(conferences, start=1):
        title = str(record.get("title") or "").strip()
        latest = latest_conference_instance(record)
        aliases = aliases_for(record)
        entry_key = (str(record.get("source_path") or ""), title)
        manual_override = manual_overrides.get(entry_key)
        if manual_override:
            entry = apply_manual_override(
                fetcher,
                record=record,
                override=manual_override,
                previous_entry=previous_entries.get(entry_key),
                output_dir=output_dir,
                protected_logos=protected_logos,
            )
            entries.append(entry)
            if args.verbose:
                print(
                    f"[{index}/{len(conferences)}] manual {title}: "
                    f"{manual_override.get('action')}"
                )
            continue

        false_positive_skip = false_positive_skips.get(entry_key)
        if false_positive_skip:
            entry = apply_false_positive_skip(
                record=record,
                false_positive=false_positive_skip,
                previous_entry=previous_entries.get(entry_key),
                output_dir=output_dir,
                protected_logos=protected_logos,
            )
            entries.append(entry)
            if args.verbose:
                print(f"[{index}/{len(conferences)}] skip false-positive {title}")
            continue

        existing_path = find_existing_logo(existing, title, aliases)
        if existing_path and not args.refresh_existing:
            existing_digest = sha256_bytes(existing_path.read_bytes())
            entry = {
                "title": title,
                "description": record.get("description"),
                "ccf_rank": record.get("ccf_rank"),
                "sub": record.get("sub"),
                "dblp": record.get("dblp"),
                "source_path": record.get("source_path"),
                "status": "reused_existing",
                "logo_file": existing_path.name,
                "source_kind": "local_existing",
                "sha256": existing_digest,
            }
            previous = previous_manifest.get((existing_path.name, existing_digest))
            if previous:
                for key in (
                    "source_url",
                    "width",
                    "height",
                    "mime",
                    "score",
                    "asset_years",
                    "page_title",
                    "candidate_count",
                    "ranked_candidate_count",
                ):
                    if previous.get(key) is not None:
                        entry[key] = previous[key]
                if previous.get("source_kind") != "local_existing":
                    entry["source_kind"] = previous.get("source_kind")
            if latest:
                entry.update(
                    {
                        "conference_year": latest.get("year"),
                        "conference_id": latest.get("id"),
                        "conference_date": latest.get("date"),
                        "conference_place": latest.get("place"),
                        "official_link": latest.get("link"),
                        "observed_years": collect_years(
                            str(latest.get("link") or ""), str(latest.get("year") or "")
                        ),
                    }
                )
            entries.append(entry)
            if args.verbose:
                print(f"[{index}/{len(conferences)}] reuse {title}: {existing_path.name}")
            continue

        if args.verbose:
            print(f"[{index}/{len(conferences)}] fetch {title}", flush=True)
        try:
            entry = fetch_logo_for_conference(
                fetcher,
                record=record,
                output_dir=output_dir,
                overwrite=args.overwrite,
                candidate_limit=args.candidate_limit,
            )
        except Exception as exc:
            entry = {
                "title": title,
                "ccf_rank": record.get("ccf_rank"),
                "source_path": record.get("source_path"),
                "status": "unexpected_error",
                "error": str(exc),
            }
        entries.append(entry)

    if args.only_annual_update:
        merged_entries_by_key = dict(previous_entries)
        for entry in entries:
            key = (str(entry.get("source_path") or ""), str(entry.get("title") or ""))
            if key[0] or key[1]:
                merged_entries_by_key[key] = entry
        ordered_entries: list[dict[str, Any]] = []
        for key in previous_entries:
            if key in merged_entries_by_key:
                ordered_entries.append(merged_entries_by_key.pop(key))
        ordered_entries.extend(merged_entries_by_key.values())
        entries = ordered_entries

    write_manifest(metadata_dir, entries, started_at, args.manifest_name)
    write_update_list(metadata_dir, entries, args.update_list_name)
    summary: dict[str, int] = {}
    for item in entries:
        summary[item.get("status", "unknown")] = summary.get(item.get("status", "unknown"), 0) + 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_output = Path(__file__).resolve().parents[1] / "assets" / "logos"
    default_metadata_output = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(default_output), help="logo output directory")
    parser.add_argument(
        "--metadata-output",
        default=str(default_metadata_output),
        help="directory for manifest.json, update_list.md, and batch manifests",
    )
    parser.add_argument(
        "--include-non-ccf",
        action="store_true",
        help="also process entries without CCF A/B/C rank",
    )
    parser.add_argument(
        "--refresh-existing",
        action="store_true",
        help="crawl even when a matching local logo already exists",
    )
    parser.add_argument(
        "--only-annual-update",
        action="store_true",
        help="refresh only previous manifest entries marked needs_annual_update, then merge with unchanged entries",
    )
    parser.add_argument("--overwrite", action="store_true", help="overwrite target logo files")
    parser.add_argument("--limit", type=int, default=0, help="debug limit for number of conferences")
    parser.add_argument("--offset", type=int, default=0, help="skip this many filtered conferences")
    parser.add_argument(
        "--ccfddl-dir",
        default="",
        help="local ccf-deadlines/conference directory; skips GitHub metadata downloads",
    )
    parser.add_argument(
        "--ccfddl-cache-dir",
        default="",
        help="write refreshed CCFDDL tree and YAML files to this cache directory",
    )
    parser.add_argument(
        "--reuse-ccfddl-cache",
        action="store_true",
        help="reuse existing CCFDDL metadata cache instead of fetching the latest upstream YAML",
    )
    parser.add_argument("--manifest-name", default="manifest.json", help="manifest file name")
    parser.add_argument("--update-list-name", default="update_list.md", help="update list file name")
    parser.add_argument(
        "--manual-overrides",
        default=str(default_metadata_output / "audit" / "manual_logo_overrides.json"),
        help="JSON file with exact-logo and manual-skip corrections",
    )
    parser.add_argument(
        "--false-positive-overrides",
        default=str(default_metadata_output / "audit" / "false_positive_overrides.json"),
        help="JSON file with confirmed false-positive logo mappings to skip",
    )
    parser.add_argument(
        "--merge-manifest-glob",
        default="",
        help="merge batch manifests matching this glob and exit",
    )
    parser.add_argument("--candidate-limit", type=int, default=14, help="image candidates per page")
    parser.add_argument("--timeout", type=float, default=18.0, help="HTTP timeout in seconds")
    parser.add_argument("--sleep", type=float, default=0.12, help="delay between HTTP requests")
    parser.add_argument(
        "--keep-proxy",
        action="store_true",
        help="keep inherited proxy environment variables",
    )
    parser.add_argument("--verbose", action="store_true", help="print per-conference progress")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return process_conferences(args)


if __name__ == "__main__":
    raise SystemExit(main())
