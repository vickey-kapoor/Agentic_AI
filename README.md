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

> **Note:** CLIP zero-shot classification has limited accuracy (~50%) for AI image detection since CLIP was not specifically trained for this task.

---

## Quick Start

### Option 1: Browser Extension

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

## How It Works

CLIP compares images against text descriptions using cosine similarity. The detector classifies images by comparing them to:

**AI prompts:** "an AI-generated image", "a synthetic image created by artificial intelligence", "a deepfake or AI-generated face", etc.

**Real prompts:** "a real photograph taken by a camera", "an authentic photograph of a real scene", "a natural photo with real lighting", etc.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze an image (base64 encoded) |
| `/health` | GET | Check API status |
| `/stats` | GET | Get analysis statistics |

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "source_url": "https://example.com"}'
```

---

## Project Structure

```
├── api/
│   ├── server.py             # FastAPI backend
│   ├── config.py             # Settings
│   └── rate_limiter.py       # Rate limiting
│
├── extension/                # Chrome MV3 extension
│   ├── manifest.json
│   ├── background/
│   ├── content/
│   ├── popup/
│   ├── options/
│   └── utils/
│
├── modules/
│   ├── clip_detector.py      # CLIP zero-shot detection
│   ├── image_cache.py        # LRU cache
│   ├── json_logger.py        # JSON logging
│   ├── screen_capture.py     # Screen capture
│   ├── overlay_window.py     # Visual alerts
│   └── floating_ui.py        # Control panel
│
├── screen_monitor_clip.py    # Desktop app entry point
└── requirements.txt
```

---

## Configuration

### Backend (`.env`)
```bash
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=*
RATE_LIMIT_REQUESTS=30
CLIP_MODEL_NAME=ViT-B-32
CLIP_PRETRAINED=openai
```

---

## Requirements

- Python 3.8+
- CUDA GPU (optional, for faster inference)
- Chrome browser (for extension)

---

## License

MIT
