# Feature Explanation

## 1. brightness
Average pixel intensity of the grayscale image (0-255).
High brightness indicates a light/white background theme.
Low brightness indicates a dark background theme.

## 2. contrast
Standard deviation of pixel intensities in grayscale.
High contrast means strong visual separation between elements.
Low contrast means elements are hard to distinguish from each other.

## 3. edge_density
Percentage of edge pixels detected using Canny edge detection.
High edge density indicates a visually complex or cluttered layout.
Low edge density indicates a clean and minimal layout.

## 4. dominant_color_count
Number of dominant colors found using K-means clustering (k=5).
More dominant colors may indicate visual noise or inconsistent palette.
Fewer dominant colors suggest a cohesive and intentional color scheme.

## 5. whitespace_ratio
Percentage of pixels with intensity greater than 200 (near-white).
High whitespace ratio indicates a clean, breathable layout with good spacing.
Low whitespace ratio indicates a cramped or cluttered layout.

## 6. sharpness
Variance of the Laplacian operator applied to the grayscale image.
High sharpness indicates crisp, clear design elements.
Low sharpness may indicate a blurry or low quality screenshot.

## 7. saturation_mean
Average saturation value from the HSV color space (0-255).
High saturation means vivid, colorful design.
Low saturation means muted or near-grayscale design.

## 8. dark_area_ratio
Percentage of pixels with intensity less than 50 (near-black).
High dark area ratio indicates heavy use of dark elements or dark theme.
Low dark area ratio indicates a mostly light-colored page.

## 9. light_area_ratio
Percentage of pixels with intensity greater than 200 (near-white).
High light area ratio indicates a light/white themed webpage.
Low light area ratio indicates a darker or more colorful webpage.

## 10. clutter_score
A combined score calculated from edge density and dominant color count.
High clutter score indicates a visually overwhelming and busy layout.
Low clutter score indicates a clean and simple visual design.