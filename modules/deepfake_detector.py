import time
import logging
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
from typing import Dict, Any

logger = logging.getLogger("ai_detector")


class DeepfakeDetector:
    """Deepfake detector using fine-tuned SigLIP model - 94.44% accuracy"""

    def __init__(self, model_name: str = "prithivMLmods/deepfake-detector-model-v1"):
        """
        Initialize the deepfake detector.

        Args:
            model_name: HuggingFace model identifier
        """
        logger.info("Loading Deepfake Detection model...")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Load model and processor
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = SiglipForImageClassification.from_pretrained(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()

        # Label mapping: 0 = fake, 1 = real
        self.id2label = {0: "fake", 1: "real"}

        # Track statistics
        self._total_analyses = 0
        self._ai_detections = 0

        logger.info("Deepfake Detection model loaded successfully!")

    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze an image to determine if it's AI-generated/fake.

        Args:
            image: PIL Image object

        Returns:
            dict: {
                'is_ai': bool,
                'confidence': float (0-1),
                'verdict': str,
                'full_analysis': str,
                'fake_probability': float,
                'real_probability': float,
                'processing_time_ms': float
            }
        """
        start_time = time.perf_counter()

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

        # Calculate processing time
        processing_time_ms = (time.perf_counter() - start_time) * 1000

        # Update statistics
        self._total_analyses += 1
        if is_ai:
            self._ai_detections += 1

        analysis = f"Fake: {fake_prob*100:.1f}%, Real: {real_prob*100:.1f}%"

        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'verdict': verdict,
            'full_analysis': analysis,
            'fake_probability': fake_prob,
            'real_probability': real_prob,
            'processing_time_ms': processing_time_ms
        }

    def get_model_info(self) -> Dict[str, str]:
        """
        Get model information.

        Returns:
            dict: Model name, device, and accuracy info
        """
        return {
            'name': self.model_name,
            'device': self.device,
            'accuracy': '94.44%'
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'model': 'SigLIP Deepfake Detector',
            'accuracy': '94.44%',
            'total': self._total_analyses,
            'ai_count': self._ai_detections,
            'real_count': self._total_analyses - self._ai_detections
        }

    def load_database(self, filepath: str) -> bool:
        """Compatibility method - no database needed for this model"""
        logger.info("Using pre-trained deepfake detection model (no database needed)")
        return True
