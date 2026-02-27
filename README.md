# AI Image Detector

Detect AI-generated images using CLIP zero-shot classification. Available as both a **desktop screen monitor** and a **browser extension**.

## Features

- **CLIP Zero-Shot Detection** - Uses text-image similarity to classify images
- **Two Modes of Operation**:
  - **Desktop Monitor** - Real-time screen capture and analysis
  - **Browser Extension** - Analyze images directly on web pages
- **Visual Indicators**:
  - **Red X** - Likely AI/Fake
  - **Yellow ?** - Uncertain
  - **Green checkmark** - Likely Real
- **No training required** - Pre-trained CLIP model works out of the box

> **Note:** CLIP zero-shot classification has limited accuracy (~50%) for AI image detection since CLIP was not specifically trained for this task. For production use cases requiring high accuracy, consider using a specialized deepfake detection model.

---

## Architecture

```
+-------------------------------------------------------------------+
|                        AI Image Detector                           |
+-----------------------------+-------------------------------------+
|     Desktop Monitor         |       Browser Extension             |
|   (screen_monitor_clip.py)  |         (extension/)                |
|            |                |              |                      |
|     Screen Capture          |       Content Script                |
|            |                |       (auto-scan images)            |
|            v                |              |                      |
|     +-------------+         |              v                      |
|     |    CLIP     |         |     +-----------------+             |
|     |  Detector   |<--------+-----|   FastAPI       |             |
|     | (Zero-Shot) |         |     |   Backend       |             |
|     +-------------+         |     |   (api/)        |             |
|            |                |     +--------+--------+             |
|     Overlay Window          |              |                      |
|                             |       JSON Logging                  |
|                             |       (logs/*.jsonl)                |
+-----------------------------+-------------------------------------+
```

---

## How It Works

CLIP (Contrastive Language-Image Pre-training) compares images against text descriptions to determine similarity. This detector uses zero-shot classification by comparing images to prompts like:

**AI prompts:**
- "an AI-generated image"
- "a synthetic image created by artificial intelligence"
- "a deepfake or AI-generated face"

**Real prompts:**
- "a real photograph taken by a camera"
- "an authentic photograph of a real scene"
- "a natural photo with real lighting and imperfections"

The image is classified based on which set of prompts it matches more closely.

---

## Quick Start

### Option 1: Browser Extension (Recommended)

**1. Start the backend API:**
```bash
pip install -r requirements.txt
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
```

**2. Load the extension in Chrome:**
- Go to `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked"
- Select the `extension/` folder

**3. Browse the web** - Images are automatically analyzed with visual overlays.

### Option 2: Desktop Screen Monitor

```bash
pip install -r requirements.txt
python screen_monitor_clip.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze an image (base64 encoded) |
| `/health` | GET | Check API status and model info |
| `/stats` | GET | Get analysis statistics |

### Example: Analyze an Image

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "source_url": "https://example.com"}'
```

**Response:**
```json
{
  "request_id": "uuid",
  "is_ai": true,
  "confidence": 0.55,
  "verdict": "Likely AI",
  "fake_probability": 0.55,
  "real_probability": 0.45,
  "processing_time_ms": 150.3,
  "cached": false
}
```

---

## Project Structure

```
├── api/                      # FastAPI backend
│   ├── server.py             # Main API with /analyze, /health, /stats
│   ├── config.py             # Pydantic settings (env-based config)
│   └── rate_limiter.py       # Token bucket rate limiter
│
├── extension/                # Chrome MV3 browser extension
│   ├── manifest.json
│   ├── background/           # Service worker
│   ├── content/              # Content script + overlays
│   ├── popup/                # Extension popup UI
│   ├── options/              # Settings page
│   └── icons/
│
├── modules/
│   ├── clip_detector.py      # CLIP zero-shot detection
│   ├── deepfake_detector.py  # SigLIP-based detection (alternative)
│   ├── json_logger.py        # Structured JSON logging
│   ├── image_cache.py        # LRU cache with perceptual hashing
│   ├── screen_capture.py     # Screen capture (desktop mode)
│   ├── overlay_window.py     # Visual alerts (desktop mode)
│   └── floating_ui.py        # Control panel (desktop mode)
│
├── logs/                     # JSON log files (auto-created)
├── screen_monitor_clip.py    # Desktop monitor entry point
└── requirements.txt
```

---

## Configuration

### Backend (`.env`)
```bash
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=*
RATE_LIMIT_REQUESTS=30        # requests per minute
LOG_DIR=./logs
LOG_RETENTION_DAYS=30
CLIP_MODEL_NAME=ViT-B-32      # CLIP model variant
CLIP_PRETRAINED=openai        # pretrained weights
```

### Extension (Options Page)
- Backend URL
- Auto-scan toggle
- Minimum image size filter
- Show/hide overlays

---

## JSON Logging

All analyses are logged to `logs/ai_detector_YYYY-MM-DD.jsonl`:

```json
{
  "timestamp": "2026-02-27T14:30:00.123Z",
  "request_id": "uuid",
  "image_hash": "a1b2c3d4...",
  "source_url": "https://example.com/page",
  "result": {
    "is_ai": true,
    "confidence": 0.55,
    "verdict": "Likely AI"
  },
  "processing_time_ms": 150.3,
  "model_info": {"name": "CLIP ViT-B-32", "device": "cuda"},
  "cache_hit": false
}
```

---

## Requirements

- Python 3.8+
- CUDA-capable GPU (optional, improves performance)
- Chrome/Chromium browser (for extension)

---

## Model Details

Uses OpenAI's CLIP model via [open-clip-torch](https://github.com/mlfoundations/open_clip):
- **Architecture**: ViT-B-32 (Vision Transformer)
- **Approach**: Zero-shot text-image similarity
- **Accuracy**: ~50% (not trained for AI detection)
- **Output**: Confidence scores based on text prompt similarity

### Limitations

CLIP was trained for general image-text matching, not specifically for detecting AI-generated images. The zero-shot approach compares images to text descriptions, which is inherently limited for this task because:

1. AI-generated images don't have consistent visual "tells" that map to text descriptions
2. The model lacks training data specifically labeled for AI vs real classification
3. Confidence scores tend to cluster around 50% (uncertain)

For higher accuracy, consider using the alternative SigLIP-based detector (`deepfake_detector.py`) which achieves 94.44% accuracy.

---

## Development History

### 2026-02-27: Switched to CLIP Zero-Shot Detection
- Reverted to CLIP-based zero-shot classification approach
- Using text-image similarity for AI image detection
- Updated API and desktop monitor to use `CLIPDetector`

### 2026-02-15: Browser Extension Architecture
- Added FastAPI backend (`api/`) with REST endpoints
- Created Chrome MV3 extension with:
  - Auto-scan images on page load
  - Visual overlays (red X, yellow ?, green checkmark)
  - Context menu "Analyze this image"
  - Popup with stats and recent detections
  - Options page for configuration
- Added structured JSON logging with daily rotation
- Added token bucket rate limiting (30 req/min)
- Added image caching with hit/miss statistics

### 2026-02-07: SigLIP Deepfake Detector Integration
- Integrated specialized SigLIP deepfake detector
- Added `modules/deepfake_detector.py` with pre-trained model
- Achieved 94.44% accuracy out of the box

### Previous: CLIP-based Detection
- Original implementation used CLIP embeddings with KNN classification
- Required building reference database from real/AI images
- Based on research paper [arXiv:2302.10174](https://arxiv.org/abs/2302.10174)

---

## License

MIT
