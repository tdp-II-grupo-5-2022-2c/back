import uvicorn

import logging.config

from app.adapters import health_controller
from app.adapters import user_sticker_controller
from app.conf.config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.config.fileConfig('app/conf/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

settings = Settings()

app = FastAPI(version=settings.version, title=settings.title)

app.include_router(health_controller.router)
app.include_router(user_sticker_controller.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logging.info("startup")


@app.on_event("shutdown")
async def shutdown():
    logging.info("shutdown")


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=settings.port, reload=True)
