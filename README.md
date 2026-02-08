# AI Image Detector

Real-time screen monitoring tool that detects AI-generated and deepfake images using a specialized SigLIP-based neural network with 94.44% accuracy.

## Features

- **Real-time screen monitoring** - Analyzes your screen while browsing
- **Visual alerts** with sound:
  - **Red X** - Likely AI/Fake
  - **Yellow ?** - Uncertain
  - **Green checkmark** - Likely Real
- **SigLIP Deepfake Detection** - Uses fine-tuned vision model for high accuracy
- **No training required** - Pre-trained model works out of the box

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the monitor
python screen_monitor_clip.py
```

## Detection Output

| Symbol | Verdict | Meaning |
|--------|---------|---------|
| Red X | Likely AI | High confidence AI-generated/deepfake |
| Yellow ? | Uncertain | Cannot determine reliably |
| Green checkmark | Likely Real | High confidence real photo |

## Project Structure

```
├── screen_monitor_clip.py    # Main application
├── modules/
│   ├── deepfake_detector.py  # SigLIP-based deepfake detection (primary)
│   ├── clip_detector.py      # CLIP-based detection (legacy)
│   ├── screen_capture.py     # Screen capture utility
│   ├── image_cache.py        # Image caching with perceptual hash
│   ├── overlay_window.py     # Visual alert overlay
│   └── floating_ui.py        # Control panel UI
└── reference_images/         # Optional reference images
```

## Requirements

- Python 3.8+
- Windows OS (for screen capture and overlay)
- CUDA-capable GPU (optional, for faster inference)

## How It Works

1. **Screen Capture** - Captures screen at regular intervals
2. **SigLIP Classification** - Pre-trained deepfake detector analyzes image
3. **Confidence Scoring** - Returns fake/real probability scores
4. **Visual Alert** - Displays overlay with verdict and confidence

## Model Details

Uses the [prithivMLmods/deepfake-detector-model-v1](https://huggingface.co/prithivMLmods/deepfake-detector-model-v1) model:
- **Architecture**: SigLIP (Sigmoid Loss for Language Image Pre-Training)
- **Accuracy**: 94.44% on deepfake detection benchmarks
- **Output**: Binary classification (fake/real) with probability scores

## Development History

### 2026-02-07: SigLIP Deepfake Detector Integration
- Migrated from CLIP+KNN to specialized SigLIP deepfake detector
- Added `modules/deepfake_detector.py` with pre-trained model
- Removed dependency on reference image database
- Fixed sound alert error (added SND_ASYNC flag)
- Added `transformers` to requirements

**Note on failed approach:** Before switching to SigLIP, we attempted zero-shot text classification with CLIP (comparing image embeddings against "AI generated image" vs "real photograph" text embeddings). This approach failed completely - all images returned ~50% confidence because CLIP wasn't trained for AI detection. The broken zero-shot code remains in `clip_detector.py` (unused) as a reference of what NOT to do. Lesson: use specialized models for specialized tasks.

### Previous: CLIP-based Detection
- Original implementation used CLIP embeddings with KNN classification
- Required building reference database from real/AI images
- Based on research paper [arXiv:2302.10174](https://arxiv.org/abs/2302.10174)
