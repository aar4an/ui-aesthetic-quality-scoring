## 1. Data Preparation

### 1.1 Image Collection

- **Dataset size:** 50 UI screenshots
- **Source type:** A mix of specific categories (e.g., e-commerce, social media platforms) and random websites/apps, to capture a variety of layout styles and design quality levels rather than a single narrow category.
- **Collection timeframe:** All 50 screenshots were collected within a short window of 1–2 days.
- **Format:** Screenshots were saved directly with their original names (e.g., `Screenshot 2026-06-23 132015.png`), rather than being renamed at the time of collection.

### 1.2 Labeling Process

- **Labels used:** Each image was manually assigned one of three quality categories — `good`, `average`, or `poor`.
- **Labeling criteria:** Labels were based on a combination of:
  - **Overall visual impression** — a general, holistic judgment of how polished or clean the UI looked at first glance.
  - **Specific design factors** — including layout balance, visual clutter, whitespace usage, and color harmony, which were considered alongside the overall impression rather than in isolation.
- **Labeling tool:** Labels were initially recorded using generic sequential filenames (`img001`, `img002`, ...) without preserving a link back to the actual screenshot filenames.

### 1.3 Issue Identified: Filename Mismatch

While building the merge step between the extracted feature CSV (`features.csv`) and the labels CSV (`labels.csv`), it was discovered that:

- `features.csv` used the original screenshot filenames (e.g., `Screenshot 2026-06-23 132015.png`)
- `labels.csv` used generic placeholder filenames (`img001.png`, `img002.png`, ...) that did not correspond to any actual file in the dataset folder.

Merging on `filename` produced **zero matching rows**, silently resulting in an empty dataset (0 rows) instead of an error — this was first noticed as unexpectedly empty `X`/`y` shapes during model training in notebook `03`.

**Root cause:** At the time of labeling, images were not reviewed in a fixed, reproducible order — labels were recorded against arbitrary sequence numbers with no saved mapping back to the source screenshots. This meant the original label-to-image mapping could not be reconstructed from the existing data.

### 1.4 Fix Applied

Since the original mapping was not recoverable, the dataset was **re-labeled from scratch**, this time recording labels directly against the actual screenshot filenames instead of generic placeholders. This ensures:

- A reliable, direct `filename` join between features and labels going forward
- No dependency on file listing order (which is not guaranteed to be stable across systems or re-runs)

This corrected `labels.csv` is now used consistently across all notebooks (`03` through `06`).

### 1.5 Class Distribution

After re-labeling, the final class distribution across the 50 images was reasonably balanced:

| Label   | Count |
|---------|-------|
| average | 20    |
| good    | 15    |
| poor    | 15    |

### 1.6 Known Dataset Limitations

- **Small sample size (50 images):** This limits model performance. Baseline ML models (Logistic Regression, Random Forest, SVM) achieved only ~20% test accuracy, and a from-scratch CNN showed clear overfitting (97.5% train accuracy vs. 10% test accuracy). A transfer-learning approach (frozen ResNet18 backbone with a retrained final layer) was used specifically to reduce this risk given the limited data.
- **Dataset size is expected to increase** in future iterations, per mentor guidance.

---

## 2. AI Tool Usage Disclosure

**Tool used:** Claude Sonnet 5 (Anthropic)

**Purpose of use:**
- Reviewing and debugging existing notebook code (path corrections, logic verification)
- Adding explanatory line-by-line comments (in Hindi/Hinglish) to existing notebooks for clarity
- Identifying data issues, including the filename mismatch described in Section 1.3
- General code review and flagging of design limitations (e.g., feature engineering issues, overfitting risk)

**Scope of use:** Claude was used as a code-review and documentation assistant on top of an existing, self-built pipeline (data collection, feature extraction logic, model architecture, and training approach were independently designed). Claude did not generate the original project design or dataset; its role was limited to reviewing, debugging, and documenting code that was already written.
