# Enterprise Transformation Plan: AI Image Detector

## Executive Summary

Transform the current POC into production-grade enterprise software through 8 phases over ~8 months.

---

## Current State vs Target

| Aspect | Current | Target |
|--------|---------|--------|
| Architecture | Monolithic Tkinter app | Microservices API |
| Processing | Synchronous, blocking | Async with job queue |
| Auth | None (raw API key in .env) | OAuth2 + API keys |
| Database | None | PostgreSQL |
| Caching | None | Redis |
| Logging | Print statements | Structured JSON (structlog) |
| Tests | None | Unit, Integration, E2E, Perf |
| Deployment | Manual | Docker + Kubernetes |

---

## Phase 1: Foundation (Weeks 1-4)
**Priority: Critical**

### 1.1 Project Restructuring
```
ai-image-detector/
├── src/ai_detector/
│   ├── core/           # Detection logic, models, prompts
│   ├── api/            # FastAPI app, routes, middleware
│   ├── services/       # Claude client, cache, storage, queue
│   ├── db/             # SQLModel models, repository
│   ├── config/         # Pydantic settings
│   └── utils/          # Logging, image utilities
├── tests/
├── docker/
├── k8s/
└── pyproject.toml
```

### 1.2 Configuration Management
- Replace `.env` with Pydantic Settings
- Environment-based config (dev/staging/prod)
- Secrets management via environment variables

### 1.3 Data Models (Pydantic)
- `DetectionRequest`, `DetectionResult`, `DetectionJob`
- Enum for verdicts: AI-Generated, Real Photograph, 3D Render, Uncertain

### 1.4 Structured Logging
- structlog with JSON output
- Request tracing with correlation IDs

### 1.5 Resilient Claude Client
- Async httpx client
- Retry with exponential backoff (tenacity)
- Circuit breaker pattern
- 30s timeout per request

---

## Phase 2: API Layer (Weeks 5-8)
**Priority: Critical**

### 2.1 FastAPI Application
- REST API with OpenAPI documentation
- CORS middleware
- Request/response logging

### 2.2 Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/detect` | POST | Sync detection |
| `/api/v1/detect/upload` | POST | File upload detection |
| `/api/v1/detect/async` | POST | Async job submission |
| `/api/v1/detect/job/{id}` | GET | Job status |
| `/api/health` | GET | Health check |
| `/api/health/ready` | GET | Readiness probe |

### 2.3 Authentication
- API Key authentication (X-API-Key header)
- JWT tokens for web UI
- Scoped permissions (detect:read, detect:write)

### 2.4 Rate Limiting
- Redis-based sliding window
- Configurable limits per org/plan
- Rate limit headers in response

---

## Phase 3: Data Layer (Weeks 9-12)
**Priority: High**

### 3.1 Database (PostgreSQL + SQLModel)
- Organizations, Users, API Keys tables
- DetectionRecord for history
- AuditLog for compliance

### 3.2 Repository Pattern
- Clean data access layer
- Query by image hash for deduplication
- Statistics aggregation

### 3.3 Redis Caching
- Cache detection results by image hash
- 5-minute TTL (configurable)
- Cache hit rate tracking

### 3.4 Image Storage
- S3 for production
- Local storage for development
- Store by content hash

---

## Phase 4: Background Processing (Weeks 13-16)
**Priority: High**

### 4.1 Celery Job Queue
- Async detection jobs
- 3 retries with backoff
- Job status tracking in Redis

### 4.2 Webhooks
- Callback URL support
- Retry failed webhooks
- Signature verification

---

## Phase 5: Observability (Weeks 17-20)
**Priority: High**

### 5.1 Prometheus Metrics
- `http_requests_total`
- `detection_duration_seconds`
- `claude_api_calls_total`
- `active_jobs` gauge

### 5.2 OpenTelemetry Tracing
- Distributed tracing
- Auto-instrument FastAPI, httpx, Redis

### 5.3 Health Checks
- Liveness probe (is process alive?)
- Readiness probe (can handle requests?)
- Dependency health (DB, Redis, Claude API)

---

## Phase 6: DevOps & Cloud Deployment (Weeks 21-24)
**Priority: High**

### 6.1 Docker
```dockerfile
FROM python:3.11-slim
# Multi-stage build, non-root user, health check
```

### 6.2 Docker Compose (Development)
- API + Worker + DB + Redis + Prometheus + Grafana

### 6.3 Kubernetes (Production)
- Deployment with 3 replicas
- HorizontalPodAutoscaler (2-10 pods)
- ConfigMap + Secrets
- Ingress with TLS

### 6.4 Cloud Options
| Provider | Services |
|----------|----------|
| **AWS** | EKS, RDS, ElastiCache, S3, CloudWatch |
| **Azure** | AKS, Azure DB, Redis Cache, Blob Storage |
| **GCP** | GKE, Cloud SQL, Memorystore, Cloud Storage |

### 6.5 CI/CD (GitHub Actions)
- Lint + Type check
- Unit + Integration tests
- Build Docker image
- Deploy to staging/production

---

## Phase 7: Testing (Weeks 25-28)
**Priority: High**

### 7.1 Unit Tests
- Detector logic
- Result parsing
- Confidence extraction

### 7.2 Integration Tests
- API endpoints
- Auth flows
- Rate limiting

### 7.3 E2E Tests
- Full detection flow
- Async job completion
- Webhook delivery

### 7.4 Performance Tests (Locust)
- Load testing (100+ concurrent users)
- Stress testing
- Identify bottlenecks

---

## Phase 8: Frontend (Weeks 29-32)
**Priority: Medium**

### Options:
1. **Web Dashboard (React)** - Statistics, history, API key management
2. **Browser Extension** - Right-click "Analyze for AI"
3. **Desktop App (Electron)** - Screen monitoring, system tray

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| API | FastAPI | Async, auto-docs, Pydantic |
| Queue | Celery + Redis | Mature, scalable |
| Database | PostgreSQL | ACID, JSON support |
| ORM | SQLModel | SQLAlchemy + Pydantic |
| Cache | Redis | Fast, pub/sub |
| Storage | S3 / MinIO | Industry standard |
| Auth | JWT + API Keys | Flexible, stateless |
| Logging | structlog | Structured JSON |
| Metrics | Prometheus | Industry standard |
| Tracing | OpenTelemetry | Vendor-agnostic |
| Container | Docker | Universal |
| Orchestration | Kubernetes | Production standard |
| CI/CD | GitHub Actions | Native integration |
| Frontend | React + TypeScript | Type safety, ecosystem |

---

## Effort Estimate

| Phase | Duration | Developers | Cloud Cost (Est.) |
|-------|----------|------------|-------------------|
| Foundation | 4 weeks | 1-2 | - |
| API Layer | 4 weeks | 2 | - |
| Data Layer | 4 weeks | 2 | $50-100/mo |
| Background | 4 weeks | 1-2 | $20-50/mo |
| Observability | 4 weeks | 1 | $30-50/mo |
| DevOps | 4 weeks | 1-2 | $100-300/mo |
| Testing | 4 weeks | 2 | - |
| Frontend | 4 weeks | 2-3 | $10-20/mo |
| **Total** | **32 weeks** | **2-3 avg** | **$200-500/mo** |

---

## Quick Start for Cloud Development

### Prerequisites
```bash
# Install tools
pip install poetry
brew install docker kubectl helm

# Clone and setup
git clone https://github.com/vickey-kapoor/AI-Image-Detector.git
cd AI-Image-Detector
poetry install
```

### Local Development
```bash
docker-compose up -d db redis
poetry run uvicorn ai_detector.api.app:create_app --reload
```

### Deploy to Cloud (AWS Example)
```bash
# Build and push image
docker build -t ai-detector:latest .
docker tag ai-detector:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/ai-detector:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/ai-detector:latest

# Deploy to EKS
kubectl apply -f k8s/
```

---

## Key Files to Preserve/Migrate

| Current File | Purpose | Migrate To |
|--------------|---------|------------|
| `modules/ai_detector_core.py` | Core detection & prompt | `src/ai_detector/core/detector.py` |
| `image_ai_detector.py` | GUI patterns | Web dashboard reference |
| `screen_monitor.py` | Modular architecture | Service design reference |

---

## Next Steps

1. Set up cloud environment (AWS/Azure/GCP)
2. Create new repo with enterprise structure
3. Migrate core detection logic
4. Build FastAPI endpoints
5. Add PostgreSQL + Redis
6. Containerize and deploy

---

*Plan created: January 2026*
*Repository: https://github.com/vickey-kapoor/AI-Image-Detector*
