import logging
import redis
from app.bot import new
from app.config import settings
from app.services import EmailService
from app.templates import HOME, PRIVACY_POLICY, TERMS_OF_SERVICE, render_page
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from http import HTTPStatus
from telegram import Update


logger = logging.getLogger(__name__)
botapp = new()


def setup_cache():
    """Setup the cache."""
    cache = redis.Redis.from_url(settings.redis_url)
    logger.info(f"Reading client config from {settings.google_application_credentials}")
    with open(settings.google_application_credentials, "r") as f:
        success = cache.set("client_config", f.read())
        logger.info(f"Status: {success}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan event handler."""
    if settings.google_application_credentials:
        setup_cache()
    else:
        logger.warning("Google Application Credentials not set, skipping cache setup")

    async with botapp:
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"OpenAI API URL: {settings.openai_api_url}")
        if settings.telegram_webhook_url:
            logger.info(f"Telegram Webhook URL: {settings.telegram_webhook_url}")
            await botapp.bot.setWebhook(
                settings.telegram_webhook_url,
                secret_token=settings.telegram_webhook_secret,
            )
        else:
            logger.info("Telegram Webhook URL not set, running polling")
            await botapp.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            await botapp.start()
        yield
        logger.info(f"Shutting down {settings.app_name}")
        if settings.telegram_webhook_url:
            logger.info(f"Telegram Webhook URL: {settings.telegram_webhook_url}")
        else:
            await botapp.updater.stop()
            await botapp.stop()


app = FastAPI(
    description="Your Personal AI Email Agent for Gmail",
    docs_url="/docs",
    lifespan=lifespan,
    redoc_url="/redoc",
    version=settings.app_version,
    title=settings.app_name,
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(
        content={"message": exc.detail},
        headers=exc.headers,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    details = {}
    for error in exc.errors():
        field = ".".join(map(str, error["loc"][1:]))
        details[field] = error["msg"]

    return JSONResponse(
        content={"message": "Invalid request parameters", "details": details},
        headers=exc.headers,
        status_code=exc.status_code,
    )


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page"""
    return HTMLResponse(render_page("Home", "🏠", "Kenzy Mail AI", HOME, "home"))


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    """Privacy policy page"""
    return HTMLResponse(
        render_page("Privacy Policy", "🔒", "Privacy Policy", PRIVACY_POLICY, "privacy")
    )


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    """Terms of service page"""
    return HTMLResponse(
        render_page(
            "Terms of Service", "📜", "Terms of Service", TERMS_OF_SERVICE, "terms"
        )
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    status = "running" if redis.Redis.from_url(settings.redis_url).ping() else "down"
    return {
        "name": settings.app_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
    }


@app.get("/callback")
async def callback(code: str, state: str):
    ids = state.split(":")
    if len(ids) != 2 or not code:
        return HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid Code or State",
        )

    success = EmailService(int(ids[0])).end_auth(code)
    if not success:
        return HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate with Google",
        )

    await botapp.bot.send_message(
        chat_id=int(ids[1]),
        text="Successfully authenticated with Google!",
    )
    return {"message": "Authentication successful! You can return to Telegram."}


@app.post("/webhook")
async def webhook(req: Request):
    if (
        req.headers.get("X-Telegram-Bot-Api-Secret-Token")
        != settings.telegram_webhook_secret
    ):
        return Response(status_code=HTTPStatus.FORBIDDEN)

    data = await req.json()
    await botapp.process_update(Update.de_json(data, botapp.bot))
    return Response(status_code=HTTPStatus.OK)
