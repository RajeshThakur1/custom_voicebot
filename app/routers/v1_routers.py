from fastapi.responses import FileResponse

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from typing import Union, List
import traceback
import sys
import json
import shutil
from app.middlewares.auth_apikey import get_api_key

from app.utilities.bia_logger import get_logger
logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", tags=["Health"])
async def health_check():
    """Check the health of services
    author: rajeshthakur@kronosx.ai
    Returns:
        [json]: json object with a status code 200 if everything is working fine else 400.
    """
    logger.debug("Health check requested")
    return {"message": "Status = Healthy"}
