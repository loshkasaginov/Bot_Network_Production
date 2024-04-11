from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import sentry_sdk

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis
from app.api.api_router import api_router, auth_router
from app.core.config import get_settings

sentry_sdk.init(
    dsn=get_settings().sentry.dsn.get_secret_value(),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI(
    title="minimal fastapi postgres template",
    version="6.0.0",
    description="https://github.com/rafsaf/minimal-fastapi-postgres-template",
    openapi_url="/openapi.json",
    docs_url="/",
)

app.include_router(auth_router)
app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(origin) for origin in get_settings().security.backend_cors_origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guards against HTTP Host Header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=get_settings().security.allowed_hosts,
)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(get_settings().redis.url.get_secret_value())
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
#addopts = "-vv -n auto --cov --cov-report xml --cov-report term-missing --cov-fail-under=100"