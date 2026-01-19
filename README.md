# AI Image Detection POC

A proof-of-concept application that detects AI-generated images, 3D renders, and distinguishes them from real photographs using Claude Vision API.

## Applications

### 1. Screen Monitor (screen_monitor.py)
A real-time floating monitor that analyzes your screen for AI-generated content while browsing social media.

**Features:**
- Real-time screen monitoring
- Floating control panel UI
- Red border overlay when AI content is detected
- Multi-threaded analysis for performance
- Image caching to avoid redundant API calls
- Session statistics tracking

**Usage:**
```bash
python screen_monitor.py
```

### 2. Image Detector GUI (image_ai_detector.py)
A standalone GUI application for analyzing individual images.

**Features:**
- User-friendly window interface
- Image upload and preview
- Detailed analysis results with confidence levels
- Identifies AI artifacts, 3D render indicators, and real photo characteristics

**Usage:**
```bash
python image_ai_detector.py
```

## Detection Capabilities

The system analyzes images for:

**AI-Generated Indicators:**
- Unnatural symmetry or repetitive patterns
- Weird hands, fingers, or facial features
- Inconsistent lighting and shadows
- Blurry or malformed text
- Background anomalies

**3D Render Indicators:**
- Perfectly clean surfaces
- Overly perfect geometry
- Unrealistic material properties
- Artificial lighting distribution

**Real Photo Indicators:**
- Natural imperfections and wear
- Realistic depth of field
- Lens artifacts and characteristics
- Organic randomness

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Requirements
- Python 3.8+
- Anthropic API key
- Windows OS (for screen monitor overlay features)
- See `requirements.txt` for package dependencies
