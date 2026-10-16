# feedback_rules.py
# Shared module: feature extraction (notebook 02/06 jaisa) + percentile-based feedback rules
# App (app.py) aur notebook 07 dono isi file ko import karenge, taaki scale same rahe
import os
import json
import cv2
import numpy as np

# feedback_thresholds.json isi folder me hona chahiye (make_thresholds.py se bani thi)
_THRESH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback_thresholds.json")

# Thresholds (train split ke percentiles: p15 = low, p85 = high) load karta hai
with open(_THRESH_PATH, encoding="utf-8") as f:
    T = json.load(f)["thresholds"]


def extract_features(img_bgr):
    """Raw BGR image (cv2 format) se 6 feedback features nikalta hai.
    edge_density aur whitespace_ratio PERCENT (0-100) me return hote hain."""

    # --- Visual features: notebook 02 jaisa, 1900x968 pe ---
    img = cv2.resize(img_bgr, (1900, 968))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    total = gray.shape[0] * gray.shape[1]

    brightness = float(np.mean(gray))                                   # average brightness (0-255)
    contrast = float(np.std(gray))                                      # grayscale ka std
    edges = cv2.Canny(gray, 100, 200)                                   # notebook 02 ke Canny params
    edge_density = float(np.count_nonzero(edges) / total * 100)        # percent
    whitespace_ratio = float(np.count_nonzero(gray > 240) / total * 100)  # bahut light pixels, percent
    saturation_mean = float(np.mean(hsv[:, :, 1]))                      # HSV S channel ka average

    # --- Layout feature: notebook 06 jaisa, 224x224 pe (raw image se seedha resize) ---
    small = cv2.cvtColor(cv2.resize(img_bgr, (224, 224)), cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(small, 180, 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.dilate(thresh, np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid = [c for c in contours if cv2.contourArea(c) > 100]
    text_like_regions = sum(1 for c in valid if cv2.contourArea(c) < 500)  # chhote blocks

    return {
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "edge_density": round(edge_density, 2),
        "whitespace_ratio": round(whitespace_ratio, 2),
        "saturation_mean": round(saturation_mean, 2),
        "text_like_regions": int(text_like_regions),
    }


def generate_feedback(f, max_items=5):
    """Features dict se feedback list banata hai. Har rule dataset ke percentiles pe based hai
    (p85 se upar = 'high', p15 se neeche = 'low'), yaani dataset ki ~15% images pe fire hota hai."""
    fb = []

    # Edge density: zyada edges = detailed/busy, kam edges = clean
    if f["edge_density"] > T["edge_density"]["p85"]:
        fb.append("The page has a lot of fine detail and edges compared to typical pages, so it may feel busy.")
    elif f["edge_density"] < T["edge_density"]["p15"]:
        fb.append("The page has very few edges and a clean, low-complexity look.")

    # Contrast
    if f["contrast"] < T["contrast"]["p15"]:
        fb.append("Contrast is low, so text and elements may be harder to distinguish.")
    elif f["contrast"] > T["contrast"]["p85"]:
        fb.append("The page has strong contrast, so elements are easy to distinguish.")

    # Brightness
    if f["brightness"] > T["brightness"]["p85"]:
        fb.append("The page is very bright. Consider adding visual accents to guide the eye.")
    elif f["brightness"] < T["brightness"]["p15"]:
        fb.append("The page uses a dark theme. Make sure text contrast stays accessible.")

    # Whitespace (bahut light pixels ka share)
    if f["whitespace_ratio"] < T["whitespace_ratio"]["p15"]:
        fb.append("Very little light empty space. If the page is not a dark theme, consider more breathing room.")
    elif f["whitespace_ratio"] > T["whitespace_ratio"]["p85"]:
        fb.append("The page has generous empty space, giving a clean and breathable feel.")

    # Saturation
    if f["saturation_mean"] < T["saturation_mean"]["p15"]:
        fb.append("Colors are muted. Consider an accent color for visual interest.")
    elif f["saturation_mean"] > T["saturation_mean"]["p85"]:
        fb.append("Colors are very vivid. High saturation may feel overwhelming.")

    # Text-dense regions
    if f["text_like_regions"] > T["text_like_regions"]["p85"]:
        fb.append("Many small text-like regions. Consider grouping content into clearer sections.")

    return fb[:max_items]