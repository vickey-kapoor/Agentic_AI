# AI Image Detector

Detect AI-generated images using a ViT-based classifier with **94.2% accuracy**. Available as both a **desktop screen monitor** and a **browser extension**.

## Features

- **High Accuracy Detection** - ViT classifier trained on AI vs human-created images
- **Two Modes of Operation**:
  - **Desktop Monitor** - Real-time screen capture and analysis
  - **Browser Extension** - Analyze images directly on web pages
- **Visual Indicators**:
  - **Red X** - Likely AI-generated
  - **Yellow ?** - Uncertain
  - **Green checkmark** - Likely human-created
- **No training required** - Pre-trained model works out of the box

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

**Response:**
```json
{
  "is_ai": false,
  "confidence": 0.95,
  "verdict": "Likely Real",
  "fake_probability": 0.05,
  "real_probability": 0.95,
  "processing_time_ms": 150
}
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
│   ├── ai_detector.py        # ViT-based AI image detector
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

## Model Details

Uses [umm-maybe/AI-image-detector](https://huggingface.co/umm-maybe/AI-image-detector):
- **Architecture**: Vision Transformer (ViT/Swin)
- **Accuracy**: 94.2%
- **Labels**: `artificial` (AI-generated) / `human` (real)
- **Training**: Trained on AI-generated artistic images

### Limitations

- Optimized for artistic images (paintings, illustrations, AI art)
- May not perform as well on deepfake photos
- Training data predates Midjourney v5, SDXL, DALL-E 3

---

## Configuration

### Backend (`.env`)
```bash
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=*
RATE_LIMIT_REQUESTS=30
```

---

## Requirements

- Python 3.8+
- CUDA GPU (optional, for faster inference)
- Chrome browser (for extension)

---

## License

MIT
