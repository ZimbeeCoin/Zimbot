# src/zimbot/main.py

import asyncio
import json
import logging
import traceback
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import redis.asyncio as redis_asyncio  # Updated import
import sentry_sdk
import uvicorn
from celery import Celery
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from jose import JWTError, jwt
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Import custom modules and routers
from zimbot.api import auth, consult, health, market, subscriptions
from zimbot.assistants import (  # Ensure proper router export in zimbot/assistants/__init__.py
    assistant,
)
from zimbot.bots import bot  # Ensure proper router export in zimbot/bots/__init__.py
from zimbot.core.config.secrets_config import SecretsConfig  # Ensure this module exists
from zimbot.core.config.settings import settings  # Corrected import
from zimbot.core.integrations.exceptions.exceptions import (
    AuthenticationError,
    DataFetchError,
    IntegrationError,
    RateLimitError,
    SomeTransientException,
)
from zimbot.core.integrations.openai.dependencies import (
    get_coinapi_market_client,
    get_crypto_clients,
    get_livecoinwatch_client,
    get_livekit_integration,
    get_openai_clients,
)
from zimbot.core.integrations.openai.metrics.metrics import (
    ACTIVE_CLIENTS,
    CLIENT_ERRORS,
    CLIENT_USAGE,
    ERROR_RATES,
    RETRY_COUNT,
)
from zimbot.core.integrations.openai.service_manager import OpenAIServiceManager
from zimbot.core.middleware.security import CSPMiddleware  # Import custom CSPMiddleware
from zimbot.core.utils.logger import get_logger
from zimbot.finance.internal.dependencies import get_finance_client  # Corrected import


# Placeholder for get_telegram_bot
# Replace with actual implementation or import
async def get_telegram_bot():
    # Placeholder implementation
    class TelegramBot:
        async def start_polling(self):
            pass

        async def stop(self):
            pass

        def is_running(self):
            return True

    return TelegramBot()


# Placeholder for FinanceClient and CryptoClient
# Replace with actual implementations or import
class FinanceClient:
    async def analyze_market_data(
        self, market_data: Dict[str, Any], analysis_type: str
    ):
        # Placeholder implementation
        return {"market_data": market_data, "analysis_type": analysis_type}


class CryptoClient:
    async def get_coin_price(self, symbol: str):
        # Placeholder implementation
        return {"symbol": symbol, "price": 100.0}

    async def get_exchange_rate(self, symbol: str, currency: str):
        # Placeholder implementation
        return {"symbol": symbol, "exchange_rate": 1.0}


# Initialize Sentry SDK
sentry_sdk.init(
    dsn="https://c2318bab5f8126461408074bcce78e49@o4508277914468352.ingest.us.sentry.io/4508277924102144",
    integrations=[AioHttpIntegration(), FastApiIntegration()],
    traces_sample_rate=1.0,  # Adjust based on desired sampling rate
    environment=settings.environment,
    release=settings.version,
)


# Configure logger
def setup_logger(name: str) -> logging.Logger:
    """
    Set up a structured JSON logger.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    log_level = (
        logging.DEBUG if settings.environment.lower() == "development" else logging.INFO
    )
    logger.setLevel(log_level)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    return logger


logger = setup_logger(__name__)

# Initialize Celery
celery_app = Celery(
    "tasks",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
)


# Initialize FastAPI with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # Startup
    logger.info("Starting up Zimbot application")

    # Initialize OpenAIServiceManager
    try:
        app.state.openai_manager = OpenAIServiceManager(
            settings.openai.service_accounts
        )
        await app.state.openai_manager.start()
        logger.info("OpenAIServiceManager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAIServiceManager: {e}")
        raise

    # Initialize Telegram Bot
    try:
        app.state.telegram_bot = await get_telegram_bot()
        await app.state.telegram_bot.start_polling()
        logger.info("Telegram bot initialized and polling started")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram Bot: {e}")
        raise

    # Initialize LiveKit Integration
    try:
        app.state.livekit = await get_livekit_integration()
        logger.info("LiveKit integration initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LiveKit integration: {e}")
        raise

    # Initialize Crypto Clients
    try:
        app.state.crypto_clients = await get_crypto_clients()
        logger.info("Crypto data clients initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Crypto Clients: {e}")
        raise

    # Initialize Prometheus Metrics
    try:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=settings.prometheus.exclude_paths,
            env_var_name="ENABLE_METRICS",
            inprogress_name="zimbot_http_requests_inprogress",
            inprogress_labels=True,
        )
        # Add custom labels if any
        if settings.prometheus.custom_labels:
            instrumentator.add(
                # If labels_factory is not recognized by the linter, ignore type
                # checking
                labels_factory=lambda: settings.prometheus.custom_labels  # type: ignore
            )
        instrumentator.instrument(app).expose(app, include_in_schema=False)
        logger.info("Prometheus metrics initialized and exposed")
    except Exception as e:
        logger.error(f"Failed to initialize Prometheus metrics: {e}")
        raise

    # Initialize Caching
    try:
        redis = redis_asyncio.from_url(
            settings.redis.url,
            encoding="utf8",
            decode_responses=True,
            max_connections=10,  # Adjust based on your load
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        app.state.redis = redis
        logger.info("Redis caching initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis caching: {e}")
        raise

    # Initialize OpenTelemetry Tracing
    try:
        tracer_provider = TracerProvider()
        trace.set_tracer_provider(tracer_provider)
        otlp_exporter = OTLPSpanExporter(
            endpoint=str(settings.opentelemetry_endpoint),  # Convert AnyHttpUrl to str
            insecure=settings.opentelemetry_insecure,  # Ensure secure transmission in production
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry tracing initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry tracing: {e}")
        raise

    # Validate Dependencies
    try:
        openai_manager = app.state.openai_manager
        if not openai_manager.is_healthy():
            raise IntegrationError("OpenAIServiceManager is not healthy")
        telegram_bot = app.state.telegram_bot
        if not telegram_bot.is_running():
            raise IntegrationError("Telegram Bot is not running")
        livekit = app.state.livekit
        if not livekit.is_healthy():
            raise IntegrationError("LiveKit integration is not healthy")
        logger.info("All critical dependencies are healthy")
    except Exception as e:
        logger.error(f"Dependency validation failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Zimbot application")
    try:
        # Stop Telegram Bot
        telegram_bot = getattr(app.state, "telegram_bot", None)
        if telegram_bot:
            await telegram_bot.stop()
            logger.info("Telegram bot stopped")

        # Shutdown OpenAIServiceManager
        openai_manager = getattr(app.state, "openai_manager", None)
        if openai_manager:
            await openai_manager.shutdown()
            logger.info("OpenAIServiceManager shutdown completed")

        # Shutdown LiveKit Integration
        livekit = getattr(app.state, "livekit", None)
        if livekit:
            await livekit.shutdown()
            logger.info("LiveKit integration shutdown completed")

        # Close Crypto Clients
        crypto_clients = getattr(app.state, "crypto_clients", {})
        for name, client in crypto_clients.items():
            await client.close()
            logger.info(f"Crypto client '{name}' shutdown completed")

        # Shutdown Redis
        redis = getattr(app.state, "redis", None)
        if redis:
            await redis.close()
            logger.info("Redis connection closed")

        # Shutdown OpenTelemetry
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, "shutdown"):
            tracer_provider.shutdown()
            logger.info("OpenTelemetry tracing shutdown completed")
        else:
            logger.warning("TracerProvider does not have a shutdown method.")

        # Ensure all pending tasks are completed
        await asyncio.sleep(1)  # Adjust as needed based on shutdown_timeout
        logger.info("All services have been gracefully shut down")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.service_name,
    description="A comprehensive AI agent application integrating LiveKit, OpenAI, and real-time cryptocurrency price feeds.",
    version=settings.version or "0.1.0",
    lifespan=lifespan,
    contact={
        "name": "Zimbot Support",
        "email": "support@zimbeecoin.com",
    },
    license_info={
        "name": "Apache License 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Middleware for Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts)
)  # Convert set to list

# Configure CORS with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(origin) for origin in settings.allowed_origins
    ],  # Convert AnyHttpUrl to str
    # Allow credentials only if structured logging is enabled
    allow_credentials=settings.logging.structured,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "X-API-Key", "Content-Type"],
    expose_headers=["X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add Content Security Policy (CSP) using Secweb or custom middleware

app.add_middleware(
    CSPMiddleware,
    directives={
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "img-src": ["'self'"],
        # Add more directives as needed
    },
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add additional security headers to responses.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Add HSTS Header
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


# Optionally, if Secweb handles HSTS, you can remove SecurityHeadersMiddleware
# If not, keep it as is
app.add_middleware(SecurityHeadersMiddleware)

# Middleware for HTTPS redirection
app.add_middleware(HTTPSRedirectMiddleware)


# Dependency: Verify API Key
async def verify_api_key(
    api_key: Optional[str] = Depends(APIKeyHeader(name="X-API-Key", auto_error=False))
):
    """
    Verify the API key provided in the request headers.

    Args:
        api_key (Optional[str]): API key from the request header.

    Raises:
        HTTPException: If the API key is invalid or missing.

    Returns:
        str: Validated API key.
    """
    api_key_header = api_key
    if not api_key_header or api_key_header not in settings.valid_api_keys:
        logger.warning(f"Invalid or missing API Key attempted: {api_key_header}")
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key_header


# Dependency: Get Current User via OAuth2
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode and validate JWT token to get the current user.

    Args:
        token (str): JWT token.

    Raises:
        HTTPException: If token is invalid or user is not found.

    Returns:
        str: User ID extracted from the token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key.get_secret_value(),
            algorithms=[settings.jwt.algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        # Optionally, fetch user from database
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# Include Routers with rate limits and API key verification where necessary
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    market.router,
    prefix="/market",
    tags=["Market Data"],
    dependencies=[
        Depends(limiter.limit(settings.rate_limit.market_rate_limit)),
        Depends(verify_api_key),
    ],
)
app.include_router(
    consult.router,
    prefix="/consult",
    tags=["Consultation Services"],
    dependencies=[
        Depends(limiter.limit(settings.rate_limit.consult_rate_limit)),
        Depends(verify_api_key),
    ],
)
app.include_router(
    assistant.router,
    prefix="/assistant",
    tags=["Assistants"],
    dependencies=[
        Depends(limiter.limit(settings.rate_limit.assistant_rate_limit)),
        Depends(verify_api_key),
    ],
)
app.include_router(
    bot.router,
    prefix="/bot",
    tags=["Bots"],
    dependencies=[
        Depends(limiter.limit(settings.rate_limit.bot_rate_limit)),
        Depends(verify_api_key),
    ],
)
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["Subscriptions"],
    dependencies=[
        Depends(limiter.limit(settings.rate_limit.subscriptions_rate_limit)),
        Depends(verify_api_key),
    ],
)


# Custom Exception Handlers
@app.exception_handler(DataFetchError)
async def data_fetch_exception_handler(request: Request, exc: DataFetchError):
    """
    Handle DataFetchError exceptions.

    Args:
        request (Request): Incoming request.
        exc (DataFetchError): Exception instance.

    Returns:
        JSONResponse: JSON response with error details.
    """
    trace_id = getattr(request.state, "trace_id", "N/A")
    logger.error(
        {
            "trace_id": trace_id,
            "error": "DataFetchError",
            "detail": str(exc),
            "path": request.url.path,
            "exception": traceback.format_exc(),
        }
    )
    ERROR_RATES.labels(model="N/A", error_type="DataFetchError").inc()
    response = JSONResponse(
        status_code=500,
        content={
            "error": "data_fetch_error",
            "detail": "An error occurred while fetching data",
            "trace_id": trace_id,
            "error_code": "500_INTERNAL",
        },
    )
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(IntegrationError)
async def integration_exception_handler(request: Request, exc: IntegrationError):
    """
    Handle IntegrationError exceptions.

    Args:
        request (Request): Incoming request.
        exc (IntegrationError): Exception instance.

    Returns:
        JSONResponse: JSON response with error details.
    """
    trace_id = getattr(request.state, "trace_id", "N/A")
    logger.error(
        {
            "trace_id": trace_id,
            "error": "IntegrationError",
            "detail": str(exc),
            "path": request.url.path,
            "exception": traceback.format_exc(),
        }
    )
    ERROR_RATES.labels(model="N/A", error_type="IntegrationError").inc()
    response = JSONResponse(
        status_code=500,
        content={
            "error": "integration_error",
            "detail": str(exc),
            "trace_id": trace_id,
            "error_code": "500_INTEGRATION",
        },
    )
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    """
    Handle AuthenticationError exceptions.

    Args:
        request (Request): Incoming request.
        exc (AuthenticationError): Exception instance.

    Returns:
        JSONResponse: JSON response with error details.
    """
    trace_id = getattr(request.state, "trace_id", "N/A")
    logger.error(
        {
            "trace_id": trace_id,
            "error": "AuthenticationError",
            "detail": str(exc),
            "path": request.url.path,
            "exception": traceback.format_exc(),
        }
    )
    ERROR_RATES.labels(model="N/A", error_type="AuthenticationError").inc()
    response = JSONResponse(
        status_code=401,
        content={
            "error": "authentication_error",
            "detail": str(exc),
            "trace_id": trace_id,
            "error_code": "401_AUTH",
        },
    )
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTPException instances.

    Args:
        request (Request): Incoming request.
        exc (HTTPException): Exception instance.

    Returns:
        JSONResponse: JSON response with error details.
    """
    trace_id = getattr(request.state, "trace_id", "N/A")
    logger.error(
        {
            "trace_id": trace_id,
            "error": "HTTPException",
            "detail": exc.detail,
            "path": request.url.path,
            "exception": traceback.format_exc(),
        }
    )
    ERROR_RATES.labels(model="N/A", error_type="HTTPException").inc()
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "detail": exc.detail,
            "trace_id": trace_id,
            "error_code": f"{exc.status_code}_HTTP",
        },
    )
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Args:
        request (Request): Incoming request.
        exc (Exception): Exception instance.

    Returns:
        JSONResponse: JSON response with error details.
    """
    trace_id = getattr(request.state, "trace_id", "N/A")
    logger.exception(
        {
            "trace_id": trace_id,
            "error": "UnhandledException",
            "detail": str(exc),
            "path": request.url.path,
            "exception": traceback.format_exc(),
        }
    )
    ERROR_RATES.labels(model="N/A", error_type="UnhandledException").inc()
    response = JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "detail": "An unexpected error occurred",
            "trace_id": trace_id,
            "error_code": "500_INTERNAL",
        },
    )
    response.headers["X-Trace-ID"] = trace_id
    return response


# Middleware for Trace ID and Detailed Logging
@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    """
    Middleware to generate a trace ID for each request and log request/response details.

    Args:
        request (Request): Incoming request.
        call_next (Callable): Next middleware or endpoint.

    Returns:
        Response: Response from the endpoint.
    """
    # Generate trace ID
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id

    # Start timer for request duration
    start_time = asyncio.get_event_loop().time()

    # Log incoming request
    logger.info(
        {
            "trace_id": trace_id,
            "event": "request_received",
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host,
        }
    )

    try:
        response = await call_next(request)
    except Exception as e:
        # Exception will be handled by exception handlers
        raise e

    # Calculate request duration
    process_time = asyncio.get_event_loop().time() - start_time

    # Add custom headers
    response.headers["X-Request-ID"] = trace_id
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"

    # Log response
    logger.info(
        {
            "trace_id": trace_id,
            "event": "response_sent",
            "status_code": response.status_code,
            "duration": f"{process_time:.3f}s",
        }
    )

    return response


# Dependency Injection: OpenAIServiceManager
async def get_openai_manager(app: FastAPI = Depends()) -> OpenAIServiceManager:
    """
    Dependency to get the OpenAIServiceManager instance from app state.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        OpenAIServiceManager: The OpenAI service manager.
    """
    return app.state.openai_manager


# Dependency Injection: Prometheus Custom Labels
def get_prometheus_custom_labels() -> Dict[str, Any]:
    """
    Retrieve custom labels for Prometheus metrics.

    Returns:
        Dict[str, Any]: Custom labels dictionary.
    """
    return settings.prometheus.custom_labels or {}


# Enhanced Health Check Endpoint is already included via `health.router`


# Enhanced Request Handler Example
@app.post(
    "/analyze-market",
    tags=["Market Analysis"],
    response_model=Dict[str, Any],
    dependencies=[
        Depends(limiter.limit("30/minute")),
        Depends(verify_api_key),
    ],
)
async def analyze_market(
    market_data: Dict[str, Any],
    analysis_type: str = "comprehensive",
    finance_client: FinanceClient = Depends(get_finance_client),
    crypto_clients: Dict[str, CryptoClient] = Depends(get_crypto_clients),
    openai_manager: OpenAIServiceManager = Depends(get_openai_manager),
):
    """
    Analyze market data using multiple data sources.

    Args:
        market_data (Dict[str, Any]): Dictionary containing market data.
        analysis_type (str, optional): Type of analysis to perform. Defaults to "comprehensive".
        finance_client (FinanceClient): Financial data client instance.
        crypto_clients (Dict[str, CryptoClient]): Dictionary of crypto client instances.
        openai_manager (OpenAIServiceManager): OpenAI service manager instance.

    Returns:
        Dict[str, Any]: Analysis results.
    """
    trace_id = str(uuid.uuid4())
    try:
        # Get data from finance client
        response = await finance_client.analyze_market_data(
            market_data=market_data, analysis_type=analysis_type
        )

        # Enrich with additional crypto data if available
        if "symbol" in market_data:
            symbol = market_data["symbol"]
            try:
                crypto_data = await crypto_clients["livecoinwatch"].get_coin_price(
                    symbol
                )
                response["crypto_metrics"] = crypto_data
            except IntegrationError:
                logger.warning(
                    "Failed to fetch crypto data from LiveCoinWatch. Attempting fallback to CoinAPI."
                )
                try:
                    crypto_data = await crypto_clients["coinapi"].get_exchange_rate(
                        symbol, "USD"
                    )
                    response["crypto_metrics"] = crypto_data
                except IntegrationError as e:
                    logger.error(f"Failed to fetch crypto data from CoinAPI: {e}")
                    response["crypto_metrics"] = {
                        "error": "Failed to fetch crypto data from all sources"
                    }

        # Optionally use OpenAI services
        # Example: Generate analysis summary
        try:
            prompt = f"Summarize the following market analysis: {json.dumps(response)}"
            summary = await openai_manager.create_completion(
                prompt=prompt, max_tokens=150
            )
            response["summary"] = summary.get("text", "")
        except Exception as e:
            logger.error(f"Failed to generate summary with OpenAI: {e}")
            response["summary"] = "Summary generation failed."

        return response
    except DataFetchError as e:
        logger.error(f"Data fetch error in market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in market analysis: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Celery Task Example
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_market_data_task(self, market_data: Dict[str, Any], analysis_type: str):
    """
    Celery task to process market data asynchronously.

    Args:
        self: Celery task instance.
        market_data (Dict[str, Any]): Market data to process.
        analysis_type (str): Type of analysis to perform.

    Raises:
        SomeTransientException: If a transient error occurs, triggering a retry.
    """
    try:
        # Long-running processing logic
        # This can be triggered asynchronously from your endpoints
        pass  # Replace with actual processing logic
    except SomeTransientException as e:
        logger.warning(f"Transient error occurred: {e}. Retrying task.")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"Unhandled exception in Celery task: {e}")
        raise IntegrationError(f"Unhandled exception: {e}") from e


# Debug Route for Sentry verification
@app.get("/debug-sentry")
async def trigger_error():
    """
    Debug route to trigger an error and verify Sentry integration.

    Returns:
        JSONResponse: Should never be reached, as an error is triggered.
    """
    division_by_zero = 1 / 0  # This will trigger an error captured by Sentry
    return {"message": "This should never be reached"}


# Run the application
if __name__ == "__main__":
    # Host and port handling with fallbacks
    host = (
        str(settings.api_base_url.host) if settings.api_base_url.host else "localhost"
    )
    port = int(settings.api_base_url.port) if settings.api_base_url.port else 8000

    uvicorn.run(
        "zimbot.main:app",
        host=host,
        port=port,
        reload=settings.environment.lower()
        == "development",  # Enable reload in development
        workers=settings.concurrency_limit,  # Number of worker processes
        log_level=settings.logging.log_level.lower(),  # Set log level based on config
    )
