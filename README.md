# AI Image Detector

Real-time screen monitoring tool that detects AI-generated images using CLIP neural network with nearest neighbor classification.

## Features

- **Real-time screen monitoring** - Analyzes your screen while browsing
- **Visual alerts** with sound:
  - **Red X** → Likely AI
  - **Yellow ?** → Uncertain
  - **Green ✓** → Likely Real
- **CLIP-based detection** - Uses vision-language model for accuracy
- **Trainable** - Add your own reference images to improve detection

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Build the database (first time only)
python build_database.py

# Run the monitor
python screen_monitor_clip.py
```

## Training the Detector

1. Add reference images:
```
reference_images/real/   ← Add 10-20 real photos
reference_images/ai/     ← Add 10-20 AI-generated images
```

2. Rebuild the database:
```bash
python build_database.py
```

## Detection Output

| Symbol | Verdict | Meaning |
|--------|---------|---------|
| Red X | Likely AI | High confidence AI-generated |
| Yellow ? | Uncertain | Cannot determine reliably |
| Green ✓ | Likely Real | High confidence real photo |

## Project Structure

```
├── screen_monitor_clip.py    # Main application
├── build_database.py         # Build CLIP reference database
├── modules/
│   ├── clip_detector.py      # CLIP-based detection logic
│   ├── screen_capture.py     # Screen capture utility
│   ├── image_cache.py        # Image caching
│   ├── overlay_window.py     # Visual alert overlay (X, ?, ✓)
│   └── floating_ui.py        # Control panel UI
├── reference_images/
│   ├── real/                 # Real photo references
│   └── ai/                   # AI image references
└── clip_database.pkl         # Trained CLIP database
```

## Requirements

- Python 3.8+
- Windows OS (for screen capture and overlay)

## How It Works

1. **CLIP Feature Extraction** - Extracts visual features using OpenAI's CLIP model
2. **Nearest Neighbor Classification** - Compares against database of known real/AI images
3. **Confidence Scoring** - Returns verdict based on similarity to reference images

Based on research paper [arXiv:2302.10174](https://arxiv.org/abs/2302.10174) - generalizes better across different AI generators than traditional classifiers.
