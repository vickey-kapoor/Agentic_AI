import imagehash
from PIL import Image
import time
from collections import OrderedDict


class ImageCache:
    """Cache for analyzed images to avoid re-processing"""

    def __init__(self, max_size=100, ttl=300):
        """
        Initialize image cache.

        Args:
            max_size: Maximum number of entries in cache
            ttl: Time-to-live in seconds for cache entries
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()  # {hash: (result, timestamp)}

    def get_image_hash(self, image):
        """
        Compute perceptual hash of an image.

        Args:
            image: PIL Image object

        Returns:
            str: Perceptual hash string
        """
        # Use average hash for speed
        return str(imagehash.average_hash(image, hash_size=16))

    def get(self, image):
        """
        Check if image result is in cache.

        Args:
            image: PIL Image object

        Returns:
            dict or None: Cached result or None if not found/expired
        """
        img_hash = self.get_image_hash(image)

        if img_hash in self.cache:
            result, timestamp = self.cache[img_hash]

            # Check if expired
            if time.time() - timestamp < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(img_hash)
                return result
            else:
                # Expired, remove
                del self.cache[img_hash]

        return None

    def set(self, image, result):
        """
        Store result in cache.

        Args:
            image: PIL Image object
            result: Analysis result dict
        """
        img_hash = self.get_image_hash(image)

        # Remove oldest if at capacity
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[img_hash] = (result, time.time())

    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()

    def is_similar(self, image1, image2, threshold=5):
        """
        Check if two images are similar.

        Args:
            image1, image2: PIL Image objects
            threshold: Hamming distance threshold

        Returns:
            bool: True if similar
        """
        hash1 = imagehash.average_hash(image1, hash_size=16)
        hash2 = imagehash.average_hash(image2, hash_size=16)
        return hash1 - hash2 < threshold
