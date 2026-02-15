# AI Image Detector

Detect AI-generated and deepfake images using a specialized SigLIP-based neural network with 94.44% accuracy. Available as both a **desktop screen monitor** and a **browser extension**.

## Features

- **SigLIP Deepfake Detection** - Fine-tuned vision model for high accuracy (94.44%)
- **Two Modes of Operation**:
  - **Desktop Monitor** - Real-time screen capture and analysis
  - **Browser Extension** - Analyze images directly on web pages
- **Visual Indicators**:
  - **Red X** - Likely AI/Fake
  - **Yellow ?** - Uncertain
  - **Green checkmark** - Likely Real
- **No training required** - Pre-trained model works out of the box

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Image Detector                         │
├─────────────────────────────┬───────────────────────────────────┤
│     Desktop Monitor         │       Browser Extension           │
│   (screen_monitor_clip.py)  │         (extension/)              │
│            │                │              │                    │
│     Screen Capture          │       Content Script              │
│            │                │       (auto-scan images)          │
│            ▼                │              │                    │
│     ┌─────────────┐         │              ▼                    │
│     │  Deepfake   │         │     ┌─────────────────┐           │
│     │  Detector   │◄────────┼─────│   FastAPI       │           │
│     │  (SigLIP)   │         │     │   Backend       │           │
│     └─────────────┘         │     │   (api/)        │           │
│            │                │     └────────┬────────┘           │
│     Overlay Window          │              │                    │
│                             │       JSON Logging                │
│                             │       (logs/*.jsonl)              │
└─────────────────────────────┴───────────────────────────────────┘
```

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
  "confidence": 0.87,
  "verdict": "Likely AI",
  "fake_probability": 0.87,
  "real_probability": 0.13,
  "processing_time_ms": 245.3,
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
│   ├── deepfake_detector.py  # SigLIP-based detection
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
  "timestamp": "2026-02-15T14:30:00.123Z",
  "request_id": "uuid",
  "image_hash": "a1b2c3d4...",
  "source_url": "https://example.com/page",
  "result": {
    "is_ai": true,
    "confidence": 0.87,
    "verdict": "Likely AI"
  },
  "processing_time_ms": 245.3,
  "model_info": {"name": "...", "device": "cuda"},
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

Uses [prithivMLmods/deepfake-detector-model-v1](https://huggingface.co/prithivMLmods/deepfake-detector-model-v1):
- **Architecture**: SigLIP (Sigmoid Loss for Language Image Pre-Training)
- **Accuracy**: 94.44% on deepfake detection benchmarks
- **Output**: Binary classification (fake/real) with probability scores

---

## Development History

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
- Updated `deepfake_detector.py` with timing and model info

### 2026-02-07: SigLIP Deepfake Detector Integration
- Migrated from CLIP+KNN to specialized SigLIP deepfake detector
- Added `modules/deepfake_detector.py` with pre-trained model
- Removed dependency on reference image database
- 94.44% accuracy out of the box

**Note on failed approach:** Before SigLIP, we attempted zero-shot CLIP classification (comparing against "AI generated image" vs "real photograph" text). This failed completely (~50% confidence on everything) because CLIP wasn't trained for AI detection. The broken code remains in `clip_detector.py` as a reference. Lesson: use specialized models for specialized tasks.

### Previous: CLIP-based Detection
- Original implementation used CLIP embeddings with KNN classification
- Required building reference database from real/AI images
- Based on research paper [arXiv:2302.10174](https://arxiv.org/abs/2302.10174)

---

## License

MIT
