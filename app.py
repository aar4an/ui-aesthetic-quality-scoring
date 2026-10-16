import streamlit as st
import cv2
import copy
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models

# Shared module: feature extraction + percentile-based feedback rules (notebook 02/06 jaisa)
import feedback_rules as fr

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
    "so treat the result as a rough guide, not a verdict. "
    "Best results with a desktop viewport screenshot (about 1900x968, above the fold)."
)

uploaded_file = st.file_uploader("Upload Webpage Screenshot", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')

    st.image(image, caption="Uploaded Screenshot", use_container_width=True)

    with st.spinner("Analyzing..."):
        model_parts = load_model()
        pred_label, confidence, probs = predict(image, model_parts)

        # PIL RGB -> OpenCV BGR (feedback_rules cv2 format expect karta hai)
        img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        features = fr.extract_features(img_bgr)
        feedback = fr.generate_feedback(features)

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
    st.caption(
        "Simple rule-based hints, compared against the typical range of the training screenshots. "
        "They are separate from the model prediction and can disagree with it."
    )
    if feedback:
        for i, point in enumerate(feedback, 1):
            st.write(f"{i}. {point}")
    else:
        st.write("Nothing unusual compared to typical pages in the training data.")

    # Feature Values
    st.markdown("---")
    st.subheader("Feature Values")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Brightness", features['brightness'])
        st.metric("Contrast", features['contrast'])
        st.metric("Edge Density", f"{features['edge_density']}%")
    with col2:
        st.metric("Saturation", features['saturation_mean'])
        st.metric("Light Empty Space", f"{features['whitespace_ratio']}%")
        st.metric("Text-like Regions", features['text_like_regions'])