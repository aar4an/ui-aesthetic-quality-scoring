<!-- historical-note -->
> **Historical note (October 2026):** this file describes an earlier version of the project (50-image or 200-image dataset). The numbers here are outdated and, for the old ResNet18 result, affected by test-set leakage. Current results (979 images, fixed train/val/test split) are in the project `README.md` and `docs/results_comparison_v2.csv`. Data preparation details are in `docs/data_preparation_and_tool_usage.md`.

# Transfer Learning Results - ResNet18

## 1. Training Results
| Epoch | Train Accuracy | Val Accuracy |
|-------|---------------|--------------|
| 1     | 35.0%         | 20.0%        |
| 5     | 77.5%         | 50.0%        |
| 10    | 92.5%         | 40.0%        |
| 15    | 97.5%         | 50.0%        |

Best Validation Accuracy: 50.0%

## 2. Final Evaluation
- Test Accuracy  : 50.0%
- Macro F1 Score : 50.37%

## 3. Classification Report
| Class   | Precision | Recall | F1  |
|---------|-----------|--------|-----|
| Good    | 0.67      | 0.67   | 0.67|
| Average | 0.40      | 0.50   | 0.44|
| Poor    | 0.50      | 0.33   | 0.40|

## 4. Confusion Matrix
[[2 1 0]
 [1 2 1]
 [0 2 1]]

## 5. Comparison with Previous Models
| Model               | Accuracy | Macro F1 |
|---------------------|----------|----------|
| Logistic Regression | 33.33%   | 31.67%   |
| Random Forest       | 26.67%   | 26.20%   |
| SVM                 | 40.00%   | 38.89%   |
| CNN from Scratch    | 10.00%   | ~8%      |
| ResNet18 (Transfer) | 50.00%   | 50.37%   |

ResNet18 clearly outperforms all previous models.

## 6. Observations
- Transfer learning significantly improved accuracy from
  10% (CNN scratch) to 50% (ResNet18)
- Good class was easiest to predict (F1: 0.67)
- Poor class was hardest to predict (F1: 0.40)
- Gap between train (97.5%) and val (50%) shows overfitting
  due to small dataset size (50 images)
- With more data (500+ images per class), transfer learning
  would perform significantly better
- best_model.pth saved at epoch 5 with 50% val accuracy