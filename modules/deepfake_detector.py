import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image


class DeepfakeDetector:
    """Deepfake detector using fine-tuned SigLIP model - 94.44% accuracy"""

    def __init__(self, model_name="prithivMLmods/deepfake-detector-model-v1"):
        """
        Initialize the deepfake detector.

        Args:
            model_name: HuggingFace model identifier
        """
        print("Loading Deepfake Detection model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Load model and processor
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = SiglipForImageClassification.from_pretrained(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()

        # Label mapping: 0 = fake, 1 = real
        self.id2label = {0: "fake", 1: "real"}

        print("Deepfake Detection model loaded successfully!")

    def analyze_image(self, image):
        """
        Analyze an image to determine if it's AI-generated/fake.

        Args:
            image: PIL Image object

        Returns:
            dict: {
                'is_ai': bool,
                'confidence': float (0-1),
                'verdict': str,
                'full_analysis': str
            }
        """
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Process image
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=1).squeeze()

        # Get probabilities
        fake_prob = probs[0].item()
        real_prob = probs[1].item()

        # Determine verdict
        if fake_prob > 0.6:
            verdict = 'Likely AI'
            is_ai = True
            confidence = fake_prob
        elif real_prob > 0.6:
            verdict = 'Likely Real'
            is_ai = False
            confidence = real_prob
        else:
            verdict = 'Uncertain'
            is_ai = False
            confidence = max(fake_prob, real_prob)

        analysis = f"Fake: {fake_prob*100:.1f}%, Real: {real_prob*100:.1f}%"

        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'verdict': verdict,
            'full_analysis': analysis,
            'fake_probability': fake_prob,
            'real_probability': real_prob
        }

    def get_stats(self):
        """Get model statistics (for compatibility)"""
        return {
            'model': 'SigLIP Deepfake Detector',
            'accuracy': '94.44%',
            'real_count': 0,
            'ai_count': 0,
            'total': 0
        }

    def load_database(self, filepath):
        """Compatibility method - no database needed for this model"""
        print("Using pre-trained deepfake detection model (no database needed)")
        return True
