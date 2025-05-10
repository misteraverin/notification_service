from db.config import settings
from db.errors import (
    PhoneCodeError,
    PhoneError,
    TimezoneError,
    WrongDatetimeError,
)
from db.sample_data import add_sample_data
from db.sessions import engine
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess
from routers import (
    customers,
    mailouts,
    messages,
    phone_codes,
    tags,
    timezones,
    users,
    web,
)
from sqlmodel import SQLModel
from starlette import status
from starlette.responses import JSONResponse
from utils.logging import log_request_info

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    openapi_prefix=settings.openapi_prefix,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
)

app.include_router(users.router, tags=["Authentication"])

routers = (
    (phone_codes.router, "Phone Codes"),
    (timezones.router, "Timezones"),
    (tags.router, "Tags"),
    (customers.router, "Customers"),
    (mailouts.router, "Mailouts"),
    (messages.router, "Messages"),
    (web.router, "Web"),
)

for router, tags in routers:
    app.include_router(
        router,
        prefix=settings.api_prefix,
        tags=[tags],
        dependencies=[Depends(log_request_info)],
    )

origins = [
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def init_tables():
    # Disable function if Celery launched
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    add_sample_data()


@app.exception_handler(PhoneCodeError)
async def phone_code_exception_handler(request: Request, exc: PhoneCodeError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Phone code is not a string of 3 digits"},
    )


@app.exception_handler(PhoneError)
async def phone_exception_handler(request: Request, exc: PhoneError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Phone is not a string of 7 digits"},
    )


@app.exception_handler(TimezoneError)
async def timezone_exception_handler(request: Request, exc: TimezoneError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Timezone is not in the list of timezones"},
    )


@app.exception_handler(WrongDatetimeError)
async def datetime_exception_handler(request: Request, exc: WrongDatetimeError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Finish time before start time"},
    )


@app.get("/")
async def root():
    return {"Say": "Hello!"}


def make_metrics_app():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


metrics_app = make_metrics_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    init_tables()
