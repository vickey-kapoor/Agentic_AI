# Agentic AI Projects

This repository contains AI-powered applications built with Claude API.

## Projects

### 1. Savings Agent (application.py)
An AI agent that recommends the best bank account savings rate based on your deposit amount.

**Features:**
- Analyzes multiple bank options
- Provides personalized recommendations
- Considers minimum deposit requirements
- Calculates potential earnings

**Usage:**
```bash
python application.py
```

### 2. AI Image Detection Tool (image_ai_detector.py)
A GUI application that classifies whether images are AI-generated or real photographs.

**Features:**
- User-friendly window interface
- Image upload and preview
- AI-powered analysis using Claude Vision API
- Detailed detection results with confidence levels
- Identifies AI artifacts and inconsistencies

**Usage:**
```bash
python image_ai_detector.py
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Requirements
- Python 3.7+
- Anthropic API key
- See `requirements.txt` for package dependencies
