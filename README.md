# CCF Conference Logo Assets

This directory stores the maintenance workflow, metadata, and source copy of CCF conference logo assets used by Better-Poster-Skill.
The collection is maintained by `fetch_ccf_logos.py`, which uses CCFDDL metadata to avoid blindly crawling hundreds of independent conference websites.
The maintained image assets live in `assets/logos`. A copy can be synced to `../Better-Poster-Skill/assets/logos` for the poster skill.

## Current Snapshot

Generated on 2026-06-06.

- CCFDDL entries processed: 314 CCF A/B/C conference records.
- Local image files: 253 image files; no PDF logo assets.
- Manifest status summary: `reused_existing=246`, `downloaded=8`, `no_logo_candidate=46`, `page_error=14`.
- Annual review entries: 211.
- Manual-check entries: 60.

The high `reused_existing` count is expected: after the first crawl, reruns reuse local files instead of overwriting manually collected or previously downloaded assets.

## Files

- `scripts/fetch_ccf_logos.py`: reusable crawler and manifest generator.
- `manifest.json`: machine-readable manifest with CCFDDL source path, official link, conference year, local file, status, hash, and annual-update flags.
- `update_list.md`: human maintenance checklist, split into annual-review, missing/manual-check, and stable entries.
- `assets/logos/*`: maintained local logo assets.
- `../Better-Poster-Skill/assets/logos/*`: poster-skill copy of the same assets.

Intermediate batch files named `manifest.batch-*.json` and `update_list.batch-*.md` are temporary and should be deleted after a successful final merge.

## Data Sources

Primary metadata source:

- CCFDDL / ccf-deadlines GitHub repository: `https://github.com/ccfddl/ccf-deadlines`
- CCFDDL conference YAML tree: `conference/<sub>/<conference>.yml`

The crawler reads each CCFDDL YAML record and uses:

- `title` as the conference display name.
- `rank.ccf` to keep CCF A/B/C entries.
- `sub` to disambiguate duplicate titles such as FSE.
- the latest `confs[].year` and `confs[].link` as the official crawl target.

Logo candidates are extracted from official pages via image tags, Open Graph image metadata, icon links, image links, srcsets, and inline CSS URLs. The crawler prefers logo-like sources and filters obvious false positives such as sponsor logos, carousel photos, venue images, page cards, and UI icons.

## Standard Update

Run from the workspace root:

```bash
python conference-logo-maintainer/scripts/fetch_ccf_logos.py \
  --ccfddl-cache-dir /tmp/ccfddl-yaml-cache \
  --timeout 6 --sleep 0.02 --candidate-limit 8
```

This writes:

- `conference-logo-maintainer/manifest.json`
- `conference-logo-maintainer/update_list.md`
- any newly found logo files under `conference-logo-maintainer/assets/logos`

The script clears inherited proxy environment variables unless `--keep-proxy` is passed. Do not use a proxy by default for this workflow.

## Batch Update

Use batch mode when long direct-network runs are unstable:

```bash
rm -f conference-logo-maintainer/manifest.batch-*.json conference-logo-maintainer/update_list.batch-*.md

for off in 0 20 40 60 80 100 120 140 160 180 200 220 240 260 280 300; do
  name=$(printf '%03d' "$off")
  python conference-logo-maintainer/scripts/fetch_ccf_logos.py \
    --offset "$off" --limit 20 \
    --timeout 4 --sleep 0.02 --candidate-limit 6 \
    --ccfddl-cache-dir /tmp/ccfddl-yaml-cache \
    --manifest-name "manifest.batch-${name}.json" \
    --update-list-name "update_list.batch-${name}.md"
done

python conference-logo-maintainer/scripts/fetch_ccf_logos.py \
  --merge-manifest-glob 'conference-logo-maintainer/manifest.batch-*.json'

rm -f conference-logo-maintainer/manifest.batch-*.json conference-logo-maintainer/update_list.batch-*.md
```

Use smaller batches, for example `--limit 10`, if a specific range hangs.

To copy the maintained assets back into Better-Poster-Skill:

```bash
rsync -a --delete conference-logo-maintainer/assets/logos/ Better-Poster-Skill/assets/logos/
```

## Refreshing Source URLs

Normal reruns reuse local files. To recompute candidate source URLs for existing files, rerun a small affected batch with `--refresh-existing`. Do not use this blindly on the whole tree unless duplicate files are acceptable, because some hand-collected files have names that differ from the CCFDDL title.

Example:

```bash
python conference-logo-maintainer/scripts/fetch_ccf_logos.py \
  --offset 140 --limit 10 \
  --refresh-existing \
  --ccfddl-cache-dir /tmp/ccfddl-yaml-cache
```

## Validation

After each maintenance run:

```bash
python -m py_compile conference-logo-maintainer/scripts/fetch_ccf_logos.py
python - <<'PY'
from pathlib import Path
from PIL import Image

bad = []
svg_bad = []
for path in sorted(Path("conference-logo-maintainer/assets/logos").iterdir()):
    if not path.is_file() or path.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        continue
    if path.suffix.lower() == ".svg":
        if b"<svg" not in path.read_bytes()[:4096].lower():
            svg_bad.append(path.name)
    else:
        try:
            image = Image.open(path)
            image.verify()
        except Exception as exc:
            bad.append((path.name, str(exc)))
print("raster_bad", bad)
print("svg_bad", svg_bad)
PY
```

Also inspect `manifest.json` for obvious false-positive source terms:

```bash
python - <<'PY'
import json
from pathlib import Path

manifest = json.loads(Path("conference-logo-maintainer/manifest.json").read_text())
bad_words = ("sponsor", "partner", "exhibitor", "supporter", "slider", "carousel", "hero", "background", "venue", "card", "close.svg")
for entry in manifest["entries"]:
    url = (entry.get("source_url") or "").lower()
    if entry.get("status") in {"downloaded", "existing_target", "reused_existing"} and any(word in url for word in bad_words):
        print(entry.get("title"), entry.get("status"), entry.get("logo_file"), entry.get("source_url"))
PY
```

## Maintenance Policy

- Keep existing manually collected logos unless they are confirmed false positives.
- Prefer vectors and high-resolution transparent rasters.
- If the official page only exposes venue photos, page screenshots, sponsor marks, or UI icons, leave the entry as `no_logo_candidate` and handle it manually later.
- Treat any source or official link containing the latest year as annual-review material.
- When CCFDDL adds or removes conferences, rerun the crawler and compare the manifest entry count.
