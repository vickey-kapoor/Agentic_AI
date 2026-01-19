import os
import sys
import base64
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path):
    """Analyze the image using Claude Vision API"""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file")
        return

    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return

    print(f"Analyzing image: {image_path}")
    print("Please wait...\n")

    try:
        # Get image format
        image_extension = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }
        media_type = media_type_map.get(image_extension, 'image/jpeg')

        # Encode image
        image_data = encode_image(image_path)

        # Prepare the prompt
        prompt = """You are an expert at detecting AI-generated images. Analyze this image very carefully for signs of AI generation.

Look for these common AI artifacts:
- Unrealistic hands, fingers, or facial features
- Inconsistent lighting or shadows
- Blurry or distorted text/letters
- Repetitive or unnatural patterns in backgrounds
- Asymmetrical features that should be symmetrical
- Unnatural textures or materials
- Impossible perspectives or physics
- Watermark-like artifacts or noise patterns

Provide your analysis in this format:

**CONCLUSION:** [AI-Generated OR Real Photograph]

**CONFIDENCE:** [X%]

**KEY INDICATORS:**
- [List specific features you observed]

**DETAILED ANALYSIS:**
[Explain your reasoning in 2-3 sentences]

Be specific and reference exact elements you see in the image."""

        # Make API call
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1024,
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
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )

        if response.status_code == 200:
            data = response.json()
            result_text = data['content'][0]['text']

            print("=" * 80)
            print("ANALYSIS RESULTS")
            print("=" * 80)
            print(result_text)
            print("=" * 80)
        else:
            print(f"API Error: Status {response.status_code}")
            print(response.text[:200])

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_detector.py <path_to_image>")
        print("\nExample:")
        print("  python test_detector.py my_image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    analyze_image(image_path)
