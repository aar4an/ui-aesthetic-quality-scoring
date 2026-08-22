# Layout Feature Notes

## 1. How Layout Features Were Calculated

### Visual Block Detection
Images ko 224x224 resize kiya, phir grayscale convert kiya.
Binary thresholding (threshold=180) se dark regions detect kiye.
Morphological dilation (3x3 kernel) se nearby regions merge kiye.
OpenCV findContours se visual blocks detect kiye.
100 pixel area se chote contours noise maanke filter kar diye.

### Features:
- num_blocks: Valid contours ki total count
- avg_block_size: Har block ka average area (pixels)
- block_density: Total block area / image area * 100
- lr_balance: Left aur right half mein blocks ka difference ratio
- tb_balance: Top aur bottom half mein blocks ka difference ratio
- text_like_regions: 500 pixels se chote blocks (text jaisi regions)
- image_like_regions: 5000 pixels se bade blocks (image jaisi regions)
- clutter_score: block_density + text_like_regions ka weighted sum

## 2. Where the Method Fails
- White background pe light colored elements detect nahi hote
- Dark themed websites (CodeHelp) mein zyada blocks detect hote
  hain kyunki dark background hi ek bada block ban jaata hai
- Text aur images ko accurately alag nahi kar sakta
- Navigation bars aur buttons alag detect nahi hote
- Overlapping elements ek single block mein merge ho jaate hain
- Threshold value (180) sab images ke liye optimal nahi hai

## 3. How It Can Be Improved
- UIED (UI Element Detection) tool use karke accurate UI elements
  detect kar sakte hain (buttons, text, images separately)
- Object detection models (YOLO, Faster RCNN) train karke
  specific UI components detect kar sakte hain
- Adaptive thresholding use karke different brightness wali
  images pe better results aa sakte hain
- OCR (Tesseract) se actual text regions detect kar sakte hain
- Semantic segmentation se har pixel ko UI element type assign
  kar sakte hain