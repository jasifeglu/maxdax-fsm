# maxdax-fsm (production refactor)

This repository has been refactored into a production-ready FastAPI service with:

- **Caching**: request-level response caching with TTL and cache metrics.
- **API validation**: strict request schema validation via Pydantic models.
- **Error handling**: centralized, consistent JSON error handling.
- **Performance optimization**: ORJSON responses, gzip compression, and computed-path benchmarking.
- **Security hardening**: strict CORS policy and hardened response headers.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health`
- `GET /metrics/cache`
- `POST /v1/score`
