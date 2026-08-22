\# UI Aesthetic Quality Scorer



\## Project Objective

An automated system that analyzes webpage screenshots and 

classifies them as Good, Average, or Poor based on visual 

aesthetic quality. The system also provides actionable 

design feedback to help designers improve their webpages.



\## Dataset Description

\- 50 webpage screenshots collected manually

\- 6 categories: Education, Portfolio, E-commerce, 

&#x20; News, Government, SaaS/Startup

\- Label distribution:

&#x20; - Good: 15 images

&#x20; - Average: 20 images

&#x20; - Poor: 15 images

\- Split: 70% train, 15% validation, 15% test



\## Methodology

1\. Manual screenshot collection and labeling

2\. Handcrafted feature extraction (brightness, contrast,

&#x20;  edge density, whitespace ratio, saturation, sharpness,

&#x20;  dominant colors, clutter score)

3\. Layout feature extraction using OpenCV contour detection

4\. Classical ML baseline (Logistic Regression, Random Forest, SVM)

5\. CNN from scratch (overfitting demonstrated)

6\. Transfer learning with ResNet18 (best performance: 50% accuracy)

7\. Rule-based design feedback generation

8\. Streamlit web app for interactive demo



\## How to Run the App

1\. Install dependencies:

&#x20;  pip install -r requirements.txt



2\. Run the app:

&#x20;  streamlit run app.py



3\. Upload a webpage screenshot in the browser

4\. View prediction, confidence score, and design feedback



\## Results

| Model               | Accuracy | Macro F1 |

|---------------------|----------|----------|

| Logistic Regression | 33.33%   | 31.67%   |

| Random Forest       | 26.67%   | 26.20%   |

| SVM                 | 40.00%   | 38.89%   |

| CNN from Scratch    | 10.00%   | \~8%      |

| ResNet18 Transfer   | 50.00%   | 50.37%   |



\## Limitations

\- Small dataset (50 images) limits model generalization

\- Labels are manually assigned and subjective

\- Handcrafted features cannot capture all aesthetic qualities

\- Model trained on limited website categories

\- Screenshots taken at one point in time



\## Future Work

\- Expand dataset to 500+ images per class

\- Use UIED for accurate UI element detection

\- Implement Grad-CAM for visual explainability

\- Fine-tune all ResNet18 layers with larger dataset

\- Add support for mobile screenshot analysis

\- Deploy app on Streamlit Cloud or Hugging Face Spaces

