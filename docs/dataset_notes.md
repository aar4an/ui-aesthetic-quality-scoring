<!-- historical-note -->
> **Historical note (October 2026):** this file describes an earlier version of the project (50-image or 200-image dataset). The numbers here are outdated and, for the old ResNet18 result, affected by test-set leakage. Current results (979 images, fixed train/val/test split) are in the project `README.md` and `docs/results_comparison_v2.csv`. Data preparation details are in `docs/data_preparation_and_tool_usage.md`.

# Dataset Notes

## 1. Where Screenshots Were Collected From

### Good (15 images)
Stripe, Notion, Linear, Apple, Figma, BBC News, Glossier,
Blue Tokai, Stanza Living, MercuryAI, Jimmy Choo, MEA India,
Serotoninn, Foxtale, Untld

### Average (20 images)
W3Schools, NDTV, Reverb, Vyome, Unidays, Indian Express,
Amazon, Flipkart, Naukri, MakeMyTrip, Zomato, Paytm, IRCTC,
Myntra, IndiaMart, JustDial, BookMyShow, Commonfloor,
Shaadi.com, CarDekho

### Poor (15 images)
CBSE, PIB India, MyGov, EPFO, Indian Railways, Delhi District
Courts, DDA, UPBOCW, NVSP, edistrict Delhi, UGC, Nprocure,
Lingscar, Craigslist, Naaptol

## 2. How Labels Were Assigned
Labels assigned manually based on 10 UI aesthetic factors:
Simplicity, Colorfulness, Craftsmanship, Diversity,
Visual Hierarchy, Spacing, Alignment, Typography,
Contrast, Layout Balance.
- Good (score 7-9): Most factors strong
- Average (score 4-6): Mixed strengths and weaknesses
- Poor (score 1-3): Multiple factors failing

## 3. Image Count Per Class
- Good    : 15 images
- Average : 20 images
- Poor    : 15 images
- Total   : 50 images

## 4. Limitations
- Labels are manually assigned and subjective
- Small dataset (50 images) may not generalize well
- Screenshots taken at one point in time, websites change
- No inter-annotator agreement check performed