import logging
from http import HTTPStatus
from app.bot import new
from app.config import settings
from app.services import EmailService
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from telegram import Update

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
botapp = new()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan event handler."""
    await botapp.bot.setWebhook(settings.telegram_webhook_url)
    async with botapp:
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"OpenAI API URL: {settings.openai_api_url}")
        logger.info(f"Telegram Webhook URL: {settings.telegram_webhook_url}")
        await botapp.start()
        yield
        logger.info(f"Shutting down {settings.app_name}")
        await botapp.stop()


app = FastAPI(
    description="AI-powered test automation assistant for QA engineers",
    docs_url="/docs",
    lifespan=lifespan,
    redoc_url="/redoc",
    version=settings.app_version,
    title=settings.app_name,
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/callback")
async def callback(code: str, state: str):
    ids = state.split(":")
    if len(ids) != 2 or not code:
        return HTTPException(status_code=422, detail="Invalid Code or State")

    success = EmailService(int(ids[0])).end_auth(code)
    if not success:
        return HTTPException(
            status_code=500, detail="Failed to authenticate with Google"
        )

    await botapp.bot.send_message(
        chat_id=int(ids[1]), text="Successfully authenticated with Google!"
    )
    return {"message": "Authentication successful! You can return to Telegram."}


@app.post("/webhook")
async def webhook(request: Request):
    req = await request.json()
    update = Update.de_json(req, botapp.bot)
    await botapp.process_update(update)
    return Response(status_code=HTTPStatus.OK)
