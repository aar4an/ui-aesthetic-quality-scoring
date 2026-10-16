import streamlit as st
import cv2
import copy
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

# Checkpoint ka path (repo me ye file honi chahiye)
CKPT_PATH = "model/resnet18_layer4_ft_v2_best.pth"

# Class order training jaisa: 0=good, 1=average, 2=poor
LABELS = ['Good', 'Average', 'Poor']
LABEL_COLORS = {'Good': 'green', 'Average': 'orange', 'Poor': 'red'}


# ─── Model Definition (v2: ResNet18 layer4 fine-tuned) ─
class FineTuneHead(nn.Module):
    """layer4 + pooling + dropout + fc. Input = layer3 ka output (256 x 14 x 14)."""
    def __init__(self, layer4):
        super().__init__()
        self.layer4 = layer4
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.drop = nn.Dropout(0.5)
        self.fc = nn.Linear(512, 3)

    def forward(self, x):
        x = self.layer4(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.drop(x)
        return self.fc(x)


@st.cache_resource  # model sirf ek baar load hoga, har upload pe nahi
def load_model():
    # Pretrained ResNet18 (ImageNet) - front part checkpoint me nahi hai, torchvision se aata hai
    base = models.resnet18(weights="IMAGENET1K_V1")

    # Front = conv1 se layer3 tak (frozen, eval mode)
    front = nn.Sequential(
        base.conv1, base.bn1, base.relu, base.maxpool,
        base.layer1, base.layer2, base.layer3
    )
    front.eval()

    # Head = layer4 + fc (checkpoint se weights aayenge)
    head = FineTuneHead(copy.deepcopy(base.layer4))
    state = torch.load(CKPT_PATH, map_location=torch.device('cpu'))

    # Agar checkpoint me fc Sequential(Dropout, Linear) ke roop me saved ho (keys: fc.1.weight)
    if any(k.startswith("fc.1.") for k in state.keys()):
        head.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(512, 3))
        head.drop = nn.Identity()

    head.load_state_dict(state)
    head.eval()  # dropout off
    return front, head


# ─── Feature Extraction (rule-based feedback ke liye) ──
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
        'clutter_score_layout': clutter_score,
        'lr_balance': lr_balance,
        'text_like_regions': text_like
    }


# ─── Feedback Generation (rule-based) ──────────────────
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
# Training jaisa preprocessing: RGB -> 224x224 BILINEAR (squash) -> /255 -> ImageNet normalize
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BILINEAR),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def predict(pil_image, model_parts):
    front, head = model_parts
    tensor = TRANSFORM(pil_image).unsqueeze(0)
    with torch.no_grad():
        feats = front(tensor)          # layer3 output: 256 x 14 x 14
        output = head(feats)           # layer4 + fc
        probs = torch.softmax(output, dim=1)[0]
        pred_idx = torch.argmax(probs).item()

    pred_label = LABELS[pred_idx]
    confidence = round(probs[pred_idx].item() * 100, 2)
    return pred_label, confidence, probs.numpy()


# ─── Main App ──────────────────────────────────────────
st.title("UI Aesthetic Quality Scorer")
st.markdown("Upload a webpage screenshot to get an aesthetic quality score and design feedback.")
st.caption(
    "Model: ResNet18 (layer4 fine-tuned), trained on 979 labelled screenshots. "
    "Test accuracy ~53% (3 classes, chance = 33%). Labels are subjective and from a single annotator, "
    "so treat the result as a rough guide, not a verdict."
)

uploaded_file = st.file_uploader("Upload Webpage Screenshot", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(image)

    st.image(image, caption="Uploaded Screenshot", use_container_width=True)

    with st.spinner("Analyzing..."):
        model_parts = load_model()
        pred_label, confidence, probs = predict(image, model_parts)
        features = extract_features(img_array)
        feedback = generate_feedback(features)

    # Prediction
    st.markdown("---")
    st.subheader("Prediction")
    color = LABEL_COLORS[pred_label]
    st.markdown(f"### :{color}[{pred_label}]")
    st.metric("Confidence Score", f"{confidence}%")

    # Confidence breakdown
    st.subheader("Class Probabilities")
    for label, prob in zip(LABELS, probs):
        st.progress(float(prob), text=f"{label}: {round(float(prob) * 100, 2)}%")

    # Design Feedback
    st.markdown("---")
    st.subheader("Design Feedback")
    if feedback:
        for i, point in enumerate(feedback, 1):
            st.write(f"{i}. {point}")
    else:
        st.write("No specific issues detected by the rule-based checks.")

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
        st.metric("L-R Balance", features['lr_balance'])