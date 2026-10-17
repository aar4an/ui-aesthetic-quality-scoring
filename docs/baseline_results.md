<!-- historical-note -->
> **Historical note (October 2026):** this file describes an earlier version of the project (50-image or 200-image dataset). The numbers here are outdated and, for the old ResNet18 result, affected by test-set leakage. Current results (979 images, fixed train/val/test split) are in the project `README.md` and `docs/results_comparison_v2.csv`. Data preparation details are in `docs/data_preparation_and_tool_usage.md`.

# Baseline ML Classifier Results

## 1. Model Performance Summary

| Model               | Accuracy | Macro F1 |
|---------------------|----------|----------|
| Logistic Regression | 33.33%   | 31.67%   |
| Random Forest       | 26.67%   | 26.20%   |
| SVM                 | 40.00%   | 38.89%   |

## 2. Best Performing Model
SVM (Support Vector Machine) performed best with 40% accuracy
and 38.89% Macro F1 score. SVM works well on small datasets
with clear boundaries between classes, which explains its
better performance compared to the other two models.

## 3. Easiest Class to Predict
Average class was easiest to predict — it had the highest
precision and recall across all three models. This is likely
because Average is the largest class (20 images) giving
models more examples to learn from.

## 4. Hardest Class to Predict
Good class was hardest to predict — consistently lowest
F1 score across all models. Good UI design is subjective
and visually similar to Average in many handcrafted features
like brightness and contrast.

## 5. Possible Reasons for Mistakes
- Dataset is very small (50 images) — not enough data for
  models to learn strong patterns
- Labels were manually assigned and may be inconsistent
- Handcrafted features alone are not sufficient to capture
  all visual aesthetic qualities
- Good and Average classes are visually similar in many
  numerical features, causing confusion
- No data augmentation was performed