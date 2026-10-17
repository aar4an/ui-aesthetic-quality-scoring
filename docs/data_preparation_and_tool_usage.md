# Data Preparation and Tool Usage

This document records how the dataset was built and labelled, which problems were found and fixed, and how AI tools were used.
It has two phases: Phase 1 (the original small dataset, kept for history) and Phase 2 (the expanded 979-image dataset used for all current results).

---

## Phase 2: Expanded dataset (979 images, October 2026)

### 2.1 Goal

The first dataset was too small (50, later 200 images) for reliable evaluation. The goal was at least 1000 images, balanced classes, a proper stratified train/val/test split without leakage, and the same screenshot format as the original images (browser viewport about 1900x968, above the fold only).

### 2.2 Final dataset

| Item | Value |
|------|-------|
| Total images | 979 |
| Good / Average / Poor | 319 / 393 / 267 |
| Sources | old (manual) 200, batch 1: 132, batch 2: 310, batch 3: 337 |
| Format | PNG, about 1900x968, above-the-fold viewport screenshots |
| Split (label-stratified, seed 42) | train 685 / val 147 / test 147, overlap 0 |

The dataset folder (`dataset_final`) and the capture folders are not included in the GitHub repo (size, and screenshots of third-party sites).

### 2.3 URL sampling

- Source list: Tranco top-1M ranking (`get_tranco.py`).
- Batch 1: random sample of 1300 sites across rank bands (1k-10k, 10k-100k, 100k-500k, 500k-1M) plus extra `.in` sites (`make_urls.py`, seed 42). Only about 350 were captured before the run was stopped, because too many sites were non-English or junk; 132 became usable.
- Batch 2 (`make_urls2.py`, seed 7, 678 URLs): English-focused. 78 curated brand sites, 260 Indian domains (.in, .co.in, .org.in, .ac.in) and 340 English-TLD global sites.
- Batch 3 (`make_urls3.py`, seed 11, 1731 URLs, a subset was used): source buckets global, small business, India, government (capped at 100 so the model cannot learn "government = poor"), e-commerce, small e-commerce and curated design-forward sites. The `provisional_label` column in that file only stores the source bucket, not a quality label.
- Always excluded: the sites used in the first 50 images, infrastructure/CDN domains, and adult, gambling, piracy keywords. The keyword filter is not perfect, so adult sites were also skipped manually during labelling.

### 2.4 Automated capture (`capture.py`)

- Playwright with Chromium, viewport 1900x968, normal Chrome user agent, wait before the screenshot.
- Blank-page check: if the grayscale standard deviation is below 4 the capture is retried with a longer wait, and the image is marked `blank` if it is still empty.
- Cookie banners: the script clicks "accept" buttons in many languages and hides common banner containers with CSS before the screenshot (the first run produced dimmed screenshots because of banners, so that data was discarded and recaptured).
- English check: non-English pages get status `non_english` (the OCR features use English Tesseract).
- Each URL gets a status in `manifest.csv`: ok, blank, fail or non_english.
- About 80% of captures were ok technically, but only about 50-60% of ok screenshots were usable after labelling rules.

### 2.5 Labelling (manual only)

- Rubric: 10 factors - Simplicity, Colorfulness, Craftsmanship, Diversity, Visual Hierarchy, Spacing, Alignment, Typography, Contrast, Layout Balance.
- Score 1-9 per image. Good = 7-9, Average = 4-6, Poor = 1-3. The class is derived from the score.
- Tool: `label_tool.py` (Streamlit). Keys 1-9 give the score, `s` skips, `u` undoes. Saved after every click, resumable.
- **All labels were assigned manually by one person (the author). No AI was used to label images**, so labels stay consistent with the original 200 images.
- Skip rules: NSFW content, casino/betting/gambling, 404 or error pages, server default pages, domain-for-sale/parked pages, login or access-denied walls, blank pages, large cookie/popup overlays, non-English sites. Crypto exchange and news sites were labelled normally. Small cookie bars at the screen edge were ignored.
- Skipped images (including every NSFW image) were deleted from disk and are not part of the dataset, the repo or any report.

### 2.6 Duplicate check and split

- Perceptual-hash check (`phash_check.py`): 4 near-duplicates were removed. None matched the original 200 images.
- The merged dataset has labels rebuilt from real filenames (`labels.csv` has filename, label, score, source, orig_filename).
- Stratified 70/15/15 split saved as `train.csv`, `val.csv`, `test.csv`, with a leakage check (no filename appears in two splits).
- Each model was evaluated once on the test set (n = 147). Test numbers are reported in the README.

### 2.7 Problems found and fixed

| Problem | Fix |
|---------|-----|
| Cookie banners dimmed early screenshots | Banner accept/hide logic in `capture.py`, data recaptured |
| Many non-English and junk sites in batch 1 | English-focused batch 2 and 3, language check in capture |
| Old ResNet18 result (67.5%) used the test loader for validation and checkpoint selection (leakage) | Separate train/val/test CSVs, test used once; old number is not comparable |
| `dominant_color_count` was always 5 (fixed K-Means) and `whitespace_ratio` / `light_area_ratio` were near duplicates | Notebook 02 v2 counts clusters above 5% share; the always-5 rule was removed from feedback |
| Feedback rules (notebook 07 and app) assumed edge density and whitespace in percent, but the CSV stores fractions (0-1), so almost every image got the same feedback. The app also computed features at 224x224 while the dataset uses 1900x968 | Shared `feedback_rules.py` (same extraction as notebooks 02/06) and `feedback_thresholds.json` (15th/85th percentile of the train split). Rules that did not separate classes (left-right balance, top-bottom balance, layout clutter) were dropped |

### 2.8 Known limitations of the dataset

- Single annotator, subjective labels, no inter-annotator agreement check (an optional second pass was not done).
- Small test set (147 images), so accuracy has about +/- 8 points confidence interval.
- The original 200 screenshots were captured manually, the rest with Playwright, so capture style differs between sources.
- Sampling bias from filtering (non-English, NSFW, error pages, blank pages, popups).
- Above-the-fold screenshots only, not full pages. Some screenshots contain chat widgets or popups.
- The model tends to take shortcuts such as "large hero photo = Good" and "dense text = Poor".

---

## Phase 1: Original small dataset (historical)

This section describes the first 50-image version and is kept for history. Its numbers are outdated; the dataset later grew to 200 images and then to the 979 images of Phase 2.

### 1.1 Image collection

- **Dataset size:** 50 UI screenshots.
- **Source type:** a mix of specific categories (for example e-commerce, social media platforms) and random websites/apps, to capture different layout styles and quality levels.
- **Collection timeframe:** all 50 screenshots were collected within 1-2 days.
- **Format:** saved with original names (for example `Screenshot 2026-06-23 132015.png`), not renamed at collection time.

### 1.2 Labelling process

- **Labels:** each image was manually assigned `good`, `average` or `poor`.
- **Criteria:** overall visual impression plus specific design factors (layout balance, clutter, whitespace, color harmony).
- **Tool:** labels were first recorded against generic sequential names (`img001`, `img002`, ...), without a saved link to the real screenshot filenames.

### 1.3 Issue identified: filename mismatch

While merging `features.csv` with `labels.csv`:

- `features.csv` used the original screenshot filenames.
- `labels.csv` used placeholder names (`img001.png`, ...) that matched no file.

Merging on `filename` gave **zero matching rows**, which silently produced an empty dataset (first noticed as empty `X`/`y` shapes in notebook `03`).

**Root cause:** images were not reviewed in a fixed, reproducible order, and the mapping from labels to screenshots was not saved, so it could not be rebuilt.

### 1.4 Fix applied

The dataset was **re-labelled from scratch**, recording labels directly against the real filenames. This gives a reliable join between features and labels and does not depend on file listing order. In Phase 2 the labels are also rebuilt from actual filenames.

### 1.5 Class distribution (50-image version)

| Label   | Count |
|---------|-------|
| average | 20    |
| good    | 15    |
| poor    | 15    |

### 1.6 Limitations seen in Phase 1

- With only 50 images the baseline models reached about 20% test accuracy and the CNN from scratch overfitted (97.5% train vs 10% test accuracy). Transfer learning with ResNet18 was used to reduce this risk.
- The dataset was expected to grow, per mentor guidance (done in Phase 2).

---

## AI Tool Usage Disclosure

**Tool used:** Claude (Anthropic), in chat sessions. Model versions varied across sessions.

**Phase 1 use:**
- Reviewing and debugging existing notebook code (path corrections, logic checks).
- Adding explanatory line-by-line comments (Hindi/Hinglish) to notebooks.
- Finding data issues such as the filename mismatch in Section 1.3.
- General code review and flagging design limitations (feature engineering issues, overfitting risk).

**Phase 2 use (expansion to 979 images):** Claude was used in chat as a coding and debugging assistant. It helped write and debug the capture, sampling, labelling-tool, duplicate-check, split, notebook, feedback-rule and Streamlit app code, and helped find problems such as cookie-banner screenshots, test-set leakage in the old ResNet result and a feature-scale mismatch in the feedback rules. Claude was not used to label any image: all 979 labels were assigned manually by the author.

**Author's role in Phase 2:** The author defined the project goals, the 10-factor rubric and score ranges, the dataset size and skip rules, and chose manual-only labelling. The author labelled every image, ran all code locally, checked the outputs, decided which results to report, and deployed the app. AI-written code was run and verified before being used for results.
