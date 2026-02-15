"""FastAPI server for AI Image Detector."""

import base64
import io
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image

from api.config import get_settings
from api.rate_limiter import TokenBucketRateLimiter
from modules.deepfake_detector import DeepfakeDetector
from modules.image_cache import ImageCache
from modules.json_logger import JSONLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_detector")

# Global instances
detector: Optional[DeepfakeDetector] = None
cache: Optional[ImageCache] = None
json_logger: Optional[JSONLogger] = None
rate_limiter: Optional[TokenBucketRateLimiter] = None

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global detector, cache, json_logger, rate_limiter

    settings = get_settings()

    # Initialize components
    logger.info("Initializing AI Image Detector API...")

    json_logger = JSONLogger(
        log_dir=settings.log_dir,
        retention_days=settings.log_retention_days
    )

    cache = ImageCache(
        max_size=settings.cache_max_size,
        ttl=settings.cache_ttl_seconds
    )

    rate_limiter = TokenBucketRateLimiter(
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds
    )

    detector = DeepfakeDetector(model_name=settings.model_name)

    logger.info("API initialization complete!")

    yield

    # Cleanup
    logger.info("Shutting down API...")


app = FastAPI(
    title="AI Image Detector API",
    description="Detect AI-generated images using SigLIP deepfake detection",
    version=VERSION,
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalyzeRequest(BaseModel):
    """Request model for image analysis."""
    image_base64: str = Field(..., description="Base64-encoded image data")
    source_url: str = Field(..., description="URL of the page containing the image")
    image_url: Optional[str] = Field(None, description="URL of the image itself")


class AnalyzeResponse(BaseModel):
    """Response model for image analysis."""
    request_id: str
    is_ai: bool
    confidence: float
    verdict: str
    fake_probability: float
    real_probability: float
    image_hash: str
    processing_time_ms: float
    cached: bool


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    device: str
    version: str


class StatsResponse(BaseModel):
    """Response model for statistics."""
    total_analyses: int
    ai_detections: int
    cache_hits: int
    cache_hit_rate: float


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(request: Request, body: AnalyzeRequest):
    """
    Analyze an image for AI-generation detection.

    Returns detection results including confidence scores and verdict.
    """
    global detector, cache, json_logger, rate_limiter

    if not detector or not cache or not json_logger or not rate_limiter:
        raise HTTPException(status_code=503, detail="Service not ready")

    # Rate limiting
    client_ip = get_client_ip(request)
    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining(client_ip)
        reset_time = rate_limiter.get_reset_time(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {reset_time:.0f} seconds.",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(reset_time))
            }
        )

    # Generate request ID
    request_id = str(uuid.uuid4())

    try:
        # Decode base64 image
        image_data = base64.b64decode(body.image_base64)
        image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        logger.error(f"Failed to decode image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image data")

    # Check cache
    cached_result = cache.get(image)
    cache_hit = cached_result is not None

    if cache_hit:
        result = cached_result
        image_hash = cache.get_image_hash(image)
        processing_time_ms = 0.0
    else:
        # Analyze image
        result = detector.analyze_image(image)
        processing_time_ms = result.get("processing_time_ms", 0.0)

        # Cache result
        image_hash = cache.set(image, result)

    # Log analysis
    json_logger.log_analysis(
        request_id=request_id,
        image_hash=image_hash,
        source_url=body.source_url,
        result=result,
        processing_time_ms=processing_time_ms,
        model_info=detector.get_model_info(),
        cache_hit=cache_hit,
        image_url=body.image_url
    )

    return AnalyzeResponse(
        request_id=request_id,
        is_ai=result["is_ai"],
        confidence=result["confidence"],
        verdict=result["verdict"],
        fake_probability=result["fake_probability"],
        real_probability=result["real_probability"],
        image_hash=image_hash,
        processing_time_ms=processing_time_ms,
        cached=cache_hit
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status."""
    global detector

    model_loaded = detector is not None
    device = detector.device if detector else "unknown"

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        device=device,
        version=VERSION
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get API statistics."""
    global json_logger, cache

    if not json_logger:
        raise HTTPException(status_code=503, detail="Service not ready")

    log_stats = json_logger.get_stats()
    cache_stats = cache.get_stats() if cache else {}

    return StatsResponse(
        total_analyses=log_stats.get("total_analyses", 0),
        ai_detections=log_stats.get("ai_detections", 0),
        cache_hits=cache_stats.get("hits", 0),
        cache_hit_rate=cache_stats.get("hit_rate", 0.0)
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
