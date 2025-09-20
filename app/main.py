"""This is the main module to start the service
This module defines below usecases:
1) Configures logger
4) Creates multiple middlewares
5) Api versioning
6) Including routers
"""

__version__ = "v1.0"
__author__ = "rajeshthakur@kronosx.ai"

import time, os
import uvicorn
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.middlewares.contextmiddleware import RequestContextMiddleware
from app.routers import v1_routers
from app.utilities import bia_logger


logger = bia_logger.BIALogger(bia_logger.get_logger(__name__), {"custom_voicebot-be": "v1"})

logger.info("#####  Starting the App  ########")

app = FastAPI()


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("Process Time: " + str(process_time))
    return response





@app.get("/")
async def healthcheck():
    return {"status": "alive"}



# Include the router directly in the main app with prefix
app.include_router(v1_routers.router, prefix="/v1/custom_voicebot-be")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5003)