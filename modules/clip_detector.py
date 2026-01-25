import torch
import open_clip
from PIL import Image
import numpy as np
from sklearn.neighbors import NearestNeighbors
import os
import pickle


class CLIPDetector:
    """CLIP-based AI image detector using nearest neighbor classification"""

    def __init__(self, model_name='ViT-B-32', pretrained='openai'):
        """
        Initialize CLIP detector.

        Args:
            model_name: CLIP model variant
            pretrained: Pretrained weights to use
        """
        print("Loading CLIP model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Load CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.model = self.model.to(self.device)
        self.model.eval()

        # Reference embeddings
        self.real_embeddings = []
        self.ai_embeddings = []
        self.nn_model = None
        self.labels = []  # 0 = real, 1 = AI

        print("CLIP model loaded successfully!")

    def extract_features(self, image):
        """
        Extract CLIP features from an image.

        Args:
            image: PIL Image object

        Returns:
            numpy array of features
        """
        with torch.no_grad():
            # Preprocess image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

            # Extract features
            features = self.model.encode_image(image_tensor)

            # Normalize
            features = features / features.norm(dim=-1, keepdim=True)

            return features.cpu().numpy().flatten()

    def add_reference_image(self, image, is_ai):
        """
        Add a reference image to the database.

        Args:
            image: PIL Image object
            is_ai: True if AI-generated, False if real
        """
        features = self.extract_features(image)

        if is_ai:
            self.ai_embeddings.append(features)
        else:
            self.real_embeddings.append(features)

        self.labels.append(1 if is_ai else 0)

        # Rebuild NN model
        self._rebuild_nn_model()

    def add_reference_folder(self, folder_path, is_ai):
        """
        Add all images from a folder as reference.

        Args:
            folder_path: Path to folder containing images
            is_ai: True if AI-generated, False if real
        """
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

        for filename in os.listdir(folder_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                try:
                    img_path = os.path.join(folder_path, filename)
                    image = Image.open(img_path).convert('RGB')
                    self.add_reference_image(image, is_ai)
                    print(f"Added: {filename} ({'AI' if is_ai else 'Real'})")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def _rebuild_nn_model(self):
        """Rebuild the nearest neighbor model with current embeddings"""
        all_embeddings = self.real_embeddings + self.ai_embeddings

        if len(all_embeddings) < 2:
            self.nn_model = None
            return

        X = np.array(all_embeddings)
        self.nn_model = NearestNeighbors(n_neighbors=min(5, len(all_embeddings)), metric='cosine')
        self.nn_model.fit(X)

    def analyze_image(self, image):
        """
        Analyze an image to determine if it's AI-generated.

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
        if self.nn_model is None or len(self.labels) < 2:
            return {
                'is_ai': False,
                'confidence': 0.5,
                'verdict': 'Uncertain',
                'full_analysis': 'Not enough reference images. Add more samples.'
            }

        # Extract features from test image
        features = self.extract_features(image)

        # Find nearest neighbors
        distances, indices = self.nn_model.kneighbors([features])

        # Vote based on neighbors
        neighbor_labels = [self.labels[i] for i in indices[0]]
        ai_votes = sum(neighbor_labels)
        real_votes = len(neighbor_labels) - ai_votes

        # Calculate confidence based on vote ratio and distance
        total_votes = len(neighbor_labels)

        # Adjust confidence based on distance (closer = more confident)
        avg_distance = np.mean(distances[0])
        distance_factor = max(0, 1 - avg_distance)  # Lower distance = higher confidence

        # Calculate AI score (0 = definitely real, 1 = definitely AI)
        ai_ratio = ai_votes / total_votes
        ai_score = ai_ratio * (0.5 + 0.5 * distance_factor)

        # Determine verdict based on score thresholds
        if ai_score >= 0.65:
            verdict = 'Likely AI'
            is_ai = True
            confidence = ai_score
        elif ai_score <= 0.35:
            verdict = 'Likely Real'
            is_ai = False
            confidence = 1 - ai_score
        else:
            verdict = 'Uncertain'
            is_ai = False  # Default to not flagging as AI when uncertain
            confidence = 0.5

        analysis = f"Nearest neighbors: {real_votes} real, {ai_votes} AI. Avg distance: {avg_distance:.3f}. AI score: {ai_score:.2f}"

        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'verdict': verdict,
            'full_analysis': analysis
        }

    def save_database(self, filepath):
        """Save the reference database to disk"""
        data = {
            'real_embeddings': self.real_embeddings,
            'ai_embeddings': self.ai_embeddings,
            'labels': self.labels
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Database saved to {filepath}")

    def load_database(self, filepath):
        """Load a reference database from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            self.real_embeddings = data['real_embeddings']
            self.ai_embeddings = data['ai_embeddings']
            self.labels = data['labels']
            self._rebuild_nn_model()
            print(f"Loaded {len(self.real_embeddings)} real and {len(self.ai_embeddings)} AI reference images")
            return True
        return False

    def get_stats(self):
        """Get database statistics"""
        return {
            'real_count': len(self.real_embeddings),
            'ai_count': len(self.ai_embeddings),
            'total': len(self.labels)
        }
