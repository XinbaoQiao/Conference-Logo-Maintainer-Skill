---
name: conference-logo-maintainer
description: Maintain Better-Poster-Skill CCF conference logo assets. Use when asked to update, audit, repair, or document CCF conference logos under assets/logos, including CCFDDL-based crawling, annual logo refresh checks, manifest/update_list regeneration, and incremental maintenance of conference logo files.
---

# Conference Logo Maintainer

## Scope

Maintain CCF A/B/C conference logo assets in `conference-logo-maintainer/assets/logos`, and keep a copy available for Better-Poster-Skill in `Better-Poster-Skill/assets/logos` when the poster skill needs the assets.
Use the existing crawler at `conference-logo-maintainer/scripts/fetch_ccf_logos.py`; do not rewrite the crawler unless a source or quality issue requires it.

## Workflow

1. Check local instructions and current assets.
   - Run from the workspace root that contains both `conference-logo-maintainer` and `Better-Poster-Skill`.
   - Keep existing hand-collected logo files unless they are clearly false positives.
   - Treat `conference-logo-maintainer/assets/logos` as the maintained source copy.
   - Do not use proxies for CCFDDL, GitHub, or conference-site downloads unless direct access has failed and the user explicitly approves a proxy path.

2. Refresh CCFDDL metadata.
   - Prefer the resumable cache mode:

```bash
python conference-logo-maintainer/scripts/fetch_ccf_logos.py \
  --ccfddl-cache-dir /tmp/ccfddl-yaml-cache \
  --timeout 6 --sleep 0.02 --candidate-limit 8
```

   - To refresh the Better-Poster-Skill copy after a successful run:

```bash
rsync -a --delete conference-logo-maintainer/assets/logos/ Better-Poster-Skill/assets/logos/
```

   - If long runs are unstable, run in batches and then merge:

```bash
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
```

3. Audit results before reporting completion.
   - Verify `conference-logo-maintainer/manifest.json` has 314 CCF A/B/C entries unless CCFDDL changed.
   - Verify every raster in `conference-logo-maintainer/assets/logos` opens with Pillow and every SVG contains `<svg>`.
   - Search `source_url` for obvious false-positive terms: `sponsor`, `partner`, `exhibitor`, `slider`, `carousel`, `hero`, `background`, `venue`, `card`, `close.svg`.
   - Visually inspect any suspicious large raster or webpage screenshot.
   - Remove confirmed false positives and rerun the affected batch.

4. Maintain documents.
   - Keep `conference-logo-maintainer/update_list.md` generated from the manifest.
   - Update `conference-logo-maintainer/README.md` when the workflow, source, status summary, or validation commands change.
   - Remove `manifest.batch-*.json` and `update_list.batch-*.md` after a successful final merge unless debugging an interrupted run.

## Output Contracts

`conference-logo-maintainer/manifest.json` is the machine-readable source of truth. Each entry should include the conference title, CCF rank, CCFDDL YAML path, latest official link, conference year, local logo file if found, status, hash for local files, and annual update flags.

`conference-logo-maintainer/update_list.md` is the human maintenance checklist. Treat entries in "Need Annual Review" as yearly refresh candidates, and entries in "Missing Or Needs Manual Check" as manual search targets.

When finishing a maintenance run, report:

- Number of CCF entries processed.
- Number of local image files.
- Manifest status summary.
- Number of annual-review and missing/manual-check entries.
- Validation commands run.
