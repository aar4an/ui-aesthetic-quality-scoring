# Feedback Rules

## Overview
The generate_feedback() function takes extracted image features
and predicted class as input, and returns 3-5 actionable design
feedback points based on rule-based thresholds.

## Rules

### Rule 1: Edge Density
- If edge_density > 15:
  "The webpage appears visually cluttered due to high edge density."
- If edge_density < 5:
  "The webpage has a clean and minimal layout with low visual complexity."

### Rule 2: Contrast
- If contrast < 30:
  "The page may have readability issues due to low contrast between elements."
- If contrast > 70:
  "The page has strong contrast, making elements easy to distinguish."

### Rule 3: Brightness
- If brightness > 200:
  "The page is very bright. Consider adding visual accents to guide the eye."
- If brightness < 80:
  "The page uses a dark theme. Ensure text contrast remains accessible."

### Rule 4: Whitespace Ratio
- If whitespace_ratio < 20:
  "The layout feels cramped. Consider adding more whitespace between elements."
- If whitespace_ratio > 60:
  "The page has good whitespace, giving a clean and breathable feel."

### Rule 5: Dominant Color Count
- If dominant_color_count >= 5:
  "The page uses too many dominant colors, which may reduce visual harmony."

### Rule 6: Saturation
- If saturation_mean > 150:
  "Colors are very vivid. High saturation may feel visually overwhelming."
- If saturation_mean < 50:
  "Colors appear muted. Consider adding accent colors for visual interest."

### Rule 7: Left-Right Balance
- If lr_balance > 0.5:
  "Visual elements are unevenly distributed left to right across the page."

### Rule 8: Top-Bottom Balance
- If tb_balance > 0.5:
  "Visual elements are unevenly distributed top to bottom across the page."

### Rule 9: Layout Clutter Score
- If clutter_score_layout > 30:
  "The overall layout appears cluttered with too many visual blocks."
- If clutter_score_layout < 10:
  "The layout is clean and well-organized with minimal visual blocks."

### Rule 10: Text Dense Regions
- If text_like_regions > 10:
  "Too many text-dense regions detected. Consider breaking content into sections."