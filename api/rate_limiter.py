"""Token bucket rate limiter for API requests."""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.

    Each client gets a bucket that fills with tokens over time.
    Requests consume tokens; when empty, requests are rejected.
    """

    def __init__(self, requests_per_window: int = 30, window_seconds: int = 60):
        """
        Initialize the rate limiter.

        Args:
            requests_per_window: Maximum requests allowed per window
            window_seconds: Window duration in seconds
        """
        self.max_tokens = requests_per_window
        self.refill_rate = requests_per_window / window_seconds  # tokens per second
        self._buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (float(self.max_tokens), time.time())
        )
        self._lock = Lock()

    def _get_tokens(self, client_id: str) -> Tuple[float, float]:
        """Get current token count and last update time for a client."""
        return self._buckets[client_id]

    def _refill(self, client_id: str) -> float:
        """Refill tokens based on elapsed time and return current count."""
        tokens, last_update = self._get_tokens(client_id)
        now = time.time()
        elapsed = now - last_update

        # Add tokens based on elapsed time
        new_tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)
        self._buckets[client_id] = (new_tokens, now)

        return new_tokens

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if a request is allowed for the given client.

        Args:
            client_id: Unique client identifier (e.g., IP address)

        Returns:
            bool: True if request is allowed, False if rate limited
        """
        with self._lock:
            tokens = self._refill(client_id)

            if tokens >= 1.0:
                # Consume one token
                self._buckets[client_id] = (tokens - 1.0, time.time())
                return True

            return False

    def get_remaining(self, client_id: str) -> int:
        """
        Get remaining requests for a client.

        Args:
            client_id: Unique client identifier

        Returns:
            int: Number of remaining requests
        """
        with self._lock:
            tokens = self._refill(client_id)
            return int(tokens)

    def get_reset_time(self, client_id: str) -> float:
        """
        Get seconds until bucket is fully refilled.

        Args:
            client_id: Unique client identifier

        Returns:
            float: Seconds until full refill
        """
        with self._lock:
            tokens = self._refill(client_id)
            tokens_needed = self.max_tokens - tokens
            return tokens_needed / self.refill_rate if self.refill_rate > 0 else 0
