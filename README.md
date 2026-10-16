\# UI Aesthetic Quality Scorer



\*\*Live demo:\*\* https://ui-aesthetic-quality-scoring-xmcqy4jweak6gyxmtacrdv.streamlit.app



\## Project Objective

A computer vision + ML system that classifies webpage screenshots as \*\*Good / Average / Poor\*\* UI aesthetic quality and gives rule-based design feedback.



Built during a summer internship (academic mentor: Unmesh Shukla, University of Delhi Faculty of Technology).



\## Dataset

\- \*\*979 webpage screenshots\*\* (Good 319, Average 393, Poor 267), \~1900x968 browser viewport, above-the-fold only

\- Sources: original 200 manually captured screenshots + 779 screenshots captured with Playwright from sampled websites (Tranco list, plus curated Indian/brand sites)

\- Capture pipeline: cookie-banner removal, blank-page retry, English-language check, near-duplicate removal (perceptual hash)

\- \*\*All labels are manual\*\* (no AI labelling) using a 10-factor rubric: Simplicity, Colorfulness, Craftsmanship, Diversity, Visual Hierarchy, Spacing, Alignment, Typography, Contrast, Layout Balance. Score 1-9: Good = 7-9, Average = 4-6, Poor = 1-3

\- Skipped while labelling: NSFW, gambling, error/parked pages, login walls, blank pages, large popups, non-English sites

\- Split (label-stratified, no overlap): train 685 / val 147 / test 147

\- Datasets and most model weights are not included in this repo (size)



\## Methodology

1\. Dataset capture and manual labelling

2\. Handcrafted features (visual, layout via OpenCV contours, OCR) - 22 features

3\. Classical ML baselines (Logistic Regression, Random Forest, SVM)

4\. CNN from scratch

5\. ResNet18 transfer learning: frozen backbone + fc, and layer4 fine-tuned

6\. 6. Rule-based design feedback: simple hints (contrast, brightness, empty space, edges, saturation, text density) compared against the 15th/85th percentile of the training screenshots (`feedback\_rules.py`, `feedback\_thresholds.json`, built by `make\_thresholds.py`). The same module is used by the app and notebook 07.

7\. Streamlit web app (uses the layer4 fine-tuned ResNet18)



\## Results (test set, n = 147, each model evaluated once on test)

| Model                        | Test Accuracy | Test Macro F1 |

|------------------------------|---------------|---------------|

| Random Forest (22 features)  | 36.05%        | 35.97%        |

| CNN from scratch             | 38.10%        | 37.72%        |

| SVM (22 features)            | 40.14%        | 39.80%        |

| Logistic Regression (22 f.)  | 45.58%        | 45.22%        |

| ResNet18 frozen + fc         | 52.38%        | 52.65%        |

| ResNet18 layer4 fine-tuned   | 53.06%        | 53.20%        |



\- Chance level is 33%. The 95% confidence interval on accuracy is about +/- 8 points (n = 147).

\- Only the two ResNet18 models are clearly above chance. ResNet18 vs Logistic Regression is not statistically clear.

\- Most errors are Average vs Good/Poor. Extreme Good <-> Poor mistakes are only 13 of 147.

\- \*\*Note on the earlier 67.5% result:\*\* it came from the 200-image version, where the test loader was also used for validation and checkpoint selection (leakage). It is not comparable to the numbers above, which use a fixed, separate test set.



\## How to Run the App

1\. Install dependencies: `pip install -r requirements.txt`

2\. Run: `streamlit run app.py`

3\. Upload a webpage screenshot and view the prediction, class probabilities and design feedback



`requirements-dev.txt` has the extra packages needed for the notebooks and capture scripts.



\## Limitations

\- Single annotator, subjective labels, no inter-annotator agreement check

\- Small test set (147 images), so results have a wide confidence interval

\- Original 200 screenshots were captured manually, the rest with Playwright (capture differences)

\- Sampling bias from filtering (non-English, NSFW, error pages, blank pages)

\- Above-the-fold screenshots only, not full pages

\- Model shortcuts: a large hero photo tends to be predicted Good and dense text Poor

\- Probabilities are overconfident (the model can show 99% confidence while being wrong)

\- Rule-based feedback uses simple heuristics and can disagree with the model prediction

\- Rule-based feedback is weakly related to the labels (some rules fire on Good, Average and Poor pages at similar rates), so treat it as hints, not a quality score. It is separate from the model prediction and can disagree with it



\## Future Work

\- Second annotator / agreement check, and a larger, more balanced test set

\- Regression on the 1-9 score

\- Grad-CAM for visual explainability

\- Full-page and mobile screenshots

\- UIED for UI element detection

