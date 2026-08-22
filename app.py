import streamlit as st
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models

# ─── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="UI Aesthetic Scorer",
    page_icon="🎨",
    layout="centered"
)

# ─── Model Definition ──────────────────────────────────
def load_model():
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, 3)
    model.load_state_dict(torch.load(
            "model/best_model.pth",
        map_location=torch.device('cpu')
    ))
    model.eval()
    return model

# ─── Feature Extraction ────────────────────────────────
def extract_features(img_array):
    img_resized = cv2.resize(img_array, (224, 224))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)

    brightness = round(float(np.mean(gray)), 2)
    contrast = round(float(np.std(gray)), 2)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = round(float(np.sum(edges > 0) / edges.size * 100), 2)
    whitespace_ratio = round(float(np.sum(gray > 200) / gray.size * 100), 2)
    saturation_mean = round(float(np.mean(hsv[:, :, 1])), 2)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = round(float(laplacian.var()), 2)

    pixels = img_resized.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, _ = cv2.kmeans(pixels, 5, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)
    dominant_color_count = len(np.unique(labels))

    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [c for c in contours if cv2.contourArea(c) > 100]
    num_blocks = len(valid_contours)
    text_like = sum(1 for c in valid_contours if cv2.contourArea(c) < 500)
    block_density = round(sum(cv2.contourArea(c) for c in valid_contours) / (224 * 224) * 100, 2)
    clutter_score = round((block_density * 0.5) + (text_like * 0.5), 2)

    h, w = gray.shape
    left_blocks = sum(1 for c in valid_contours if cv2.boundingRect(c)[0] < w // 2)
    right_blocks = num_blocks - left_blocks
    lr_balance = round(abs(left_blocks - right_blocks) / (num_blocks + 1e-5), 2)

    return {
        'brightness': brightness,
        'contrast': contrast,
        'edge_density': edge_density,
        'whitespace_ratio': whitespace_ratio,
        'saturation_mean': saturation_mean,
        'sharpness': sharpness,
        'dominant_color_count': dominant_color_count,
        'clutter_score_layout': clutter_score,
        'lr_balance': lr_balance,
        'text_like_regions': text_like
    }

# ─── Feedback Generation ───────────────────────────────
def generate_feedback(features):
    feedback = []

    if features['edge_density'] > 15:
        feedback.append("The webpage appears visually cluttered due to high edge density.")
    elif features['edge_density'] < 5:
        feedback.append("The webpage has a clean and minimal layout with low visual complexity.")

    if features['contrast'] < 30:
        feedback.append("The page may have readability issues due to low contrast between elements.")
    elif features['contrast'] > 70:
        feedback.append("The page has strong contrast, making elements easy to distinguish.")

    if features['brightness'] > 200:
        feedback.append("The page is very bright. Consider adding visual accents to guide the eye.")
    elif features['brightness'] < 80:
        feedback.append("The page uses a dark theme. Ensure text contrast remains accessible.")

    if features['whitespace_ratio'] < 20:
        feedback.append("The layout feels cramped. Consider adding more whitespace between elements.")
    elif features['whitespace_ratio'] > 60:
        feedback.append("The page has good whitespace, giving a clean and breathable feel.")

    if features['dominant_color_count'] >= 5:
        feedback.append("The page uses too many dominant colors, which may reduce visual harmony.")

    if features['saturation_mean'] < 50:
        feedback.append("Colors appear muted. Consider adding accent colors for visual interest.")
    elif features['saturation_mean'] > 150:
        feedback.append("Colors are very vivid. High saturation may feel visually overwhelming.")

    if features['lr_balance'] > 0.5:
        feedback.append("Visual elements are unevenly distributed left to right across the page.")

    if features['clutter_score_layout'] > 30:
        feedback.append("The overall layout appears cluttered with too many visual blocks.")

    if features['text_like_regions'] > 10:
        feedback.append("Too many text-dense regions. Consider breaking content into sections.")

    return feedback[:5]

# ─── Prediction ────────────────────────────────────────
def predict(img_array, model):
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    tensor = transform(img_array).unsqueeze(0)
    with torch.no_grad():
        output = model(tensor)
        probs = torch.softmax(output, dim=1)[0]
        pred_idx = torch.argmax(probs).item()

    labels = ['Good', 'Average', 'Poor']
    label_colors = {'Good': 'green', 'Average': 'orange', 'Poor': 'red'}
    pred_label = labels[pred_idx]
    confidence = round(probs[pred_idx].item() * 100, 2)

    return pred_label, confidence, probs.numpy(), labels, label_colors

# ─── Main App ──────────────────────────────────────────
st.title("UI Aesthetic Quality Scorer")
st.markdown("Upload a webpage screenshot to get an aesthetic quality score and design feedback.")

uploaded_file = st.file_uploader("Upload Webpage Screenshot", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image)

    st.image(image, caption="Uploaded Screenshot", use_container_width=True)

    with st.spinner("Analyzing..."):
        model = load_model()
        pred_label, confidence, probs, labels, label_colors = predict(img_array, model)
        features = extract_features(img_array)
        feedback = generate_feedback(features)

    # Prediction
    st.markdown("---")
    st.subheader("Prediction")
    color = label_colors[pred_label]
    st.markdown(f"### :{color}[{pred_label}]")
    st.metric("Confidence Score", f"{confidence}%")

    # Confidence breakdown
    st.subheader("Class Probabilities")
    for label, prob in zip(labels, probs):
        st.progress(float(prob), text=f"{label}: {round(prob*100, 2)}%")

    # Design Feedback
    st.markdown("---")
    st.subheader("Design Feedback")
    for i, point in enumerate(feedback, 1):
        st.write(f"{i}. {point}")

    # Feature Values
    st.markdown("---")
    st.subheader("Feature Values")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Brightness", features['brightness'])
        st.metric("Contrast", features['contrast'])
        st.metric("Edge Density", f"{features['edge_density']}%")
        st.metric("Whitespace Ratio", f"{features['whitespace_ratio']}%")
    with col2:
        st.metric("Saturation", features['saturation_mean'])
        st.metric("Sharpness", features['sharpness'])
        st.metric("Clutter Score", features['clutter_score_layout'])
        st.metric("Dominant Colors", features['dominant_color_count'])