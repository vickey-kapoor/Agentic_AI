import os
import base64
import requests
import re
from PIL import Image
import io


class AIDetectorCore:
    """Core AI detection logic using Claude Vision API"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.model = "claude-3-5-haiku-latest"
        self.max_tokens = 2048
        self.api_url = "https://api.anthropic.com/v1/messages"

        # Excellent forensic prompt from original implementation
        self.prompt = """You are an expert at detecting AI-generated images, 3D renders, and distinguishing them from real photographs. Analyze this image in extreme detail.

Look for these SPECIFIC indicators:

**AI-Generated Image Artifacts:**
- Unnatural symmetry or repetitive patterns
- Weird hands, fingers, or facial features
- Inconsistent lighting sources or shadow directions
- Blurry or malformed text
- Impossible reflections or perspectives
- Unnatural skin texture or hair strands
- Background elements that don't make logical sense
- Objects merging unnaturally into each other
- Unusual color gradients or saturation

**3D Render Indicators:**
- Perfectly clean surfaces with no dust, wear, or imperfections
- Overly perfect geometry and straight lines
- Unrealistic material properties (too glossy, too matte, too perfect)
- Artificial lighting that's too evenly distributed
- Lack of natural randomness (everything looks placed intentionally)
- No lens artifacts like chromatic aberration or subtle blur
- Perfectly placed objects with no natural chaos
- Materials that look "CG-like" rather than real-world weathered

**Real Photograph Indicators:**
- Natural imperfections, dust, scratches, wear and tear
- Realistic depth of field and lens characteristics
- Natural lighting with complex interactions
- Random elements and organic chaos
- Realistic material aging and weathering
- Natural color variations and noise
- Authentic shadows with proper penumbra
- Lens artifacts (slight distortion, vignetting)

**Your Analysis Must Include:**
1. **CONCLUSION**: State clearly: "AI-Generated", "3D Render", "Real Photograph", or "Uncertain"
2. **CONFIDENCE**: Give percentage (0-100%)
3. **EVIDENCE**: List 5-7 specific visual elements you observed
4. **KEY INDICATORS**: What were the strongest tells?
5. **REASONING**: Explain your logic step by step

Be brutally honest and detailed. If something looks even slightly artificial, call it out specifically."""

    def encode_image(self, image_source):
        """
        Encode image to base64.

        Args:
            image_source: Either a PIL Image object or file path string

        Returns:
            str: Base64 encoded image data
        """
        if isinstance(image_source, str):
            # File path provided
            with open(image_source, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif isinstance(image_source, Image.Image):
            # PIL Image object
            buffered = io.BytesIO()
            # Save as PNG to avoid compression artifacts
            image_source.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            raise ValueError("image_source must be a file path or PIL Image")

    def get_media_type(self, image_source):
        """Determine media type for API request"""
        if isinstance(image_source, str):
            # File path - determine from extension
            ext = os.path.splitext(image_source)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }
            return media_type_map.get(ext, 'image/png')
        else:
            # PIL Image - default to PNG
            return 'image/png'

    def analyze_image(self, image_source):
        """
        Analyze image for AI-generated content.

        Args:
            image_source: Either a PIL Image object or file path string

        Returns:
            dict: {
                'is_ai': bool,
                'confidence': float (0-1),
                'verdict': str ('AI-Generated', '3D Render', 'Real Photograph', 'Uncertain'),
                'full_analysis': str (complete Claude response)
            }
        """
        try:
            # Encode image
            image_data = self.encode_image(image_source)
            media_type = self.get_media_type(image_source)

            # Make API call
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": self.prompt
                                }
                            ]
                        }
                    ]
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                full_text = data['content'][0]['text']

                # Parse the result
                result = self.parse_result(full_text)
                result['full_analysis'] = full_text

                return result
            else:
                # API error
                return {
                    'is_ai': False,
                    'confidence': 0.0,
                    'verdict': 'Error',
                    'full_analysis': f"API Error: {response.status_code} - {response.text[:200]}"
                }

        except Exception as e:
            return {
                'is_ai': False,
                'confidence': 0.0,
                'verdict': 'Error',
                'full_analysis': f"Exception: {str(e)}"
            }

    def parse_result(self, claude_response):
        """
        Parse Claude's response to extract structured data.

        Args:
            claude_response: str - Raw text response from Claude

        Returns:
            dict: {'is_ai': bool, 'confidence': float, 'verdict': str}
        """
        # Extract verdict
        verdict = 'Uncertain'
        if 'AI-Generated' in claude_response or 'AI-generated' in claude_response:
            verdict = 'AI-Generated'
        elif '3D Render' in claude_response:
            verdict = '3D Render'
        elif 'Real Photograph' in claude_response:
            verdict = 'Real Photograph'

        # Extract confidence percentage
        confidence = 0.5  # Default

        # Look for patterns like "95%", "CONFIDENCE: 85%", etc.
        confidence_patterns = [
            r'CONFIDENCE[:\s]+(\d+)%',
            r'confidence[:\s]+(\d+)%',
            r'(\d+)%\s+confidence',
            r'\((\d+)%\)',
        ]

        for pattern in confidence_patterns:
            match = re.search(pattern, claude_response, re.IGNORECASE)
            if match:
                confidence = float(match.group(1)) / 100.0
                break

        # Determine if AI-generated (including 3D renders)
        is_ai = verdict in ['AI-Generated', '3D Render']

        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'verdict': verdict
        }
