from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv

from .auth import verify_api_key
from .browser import check_nik_bansos

load_dotenv()

app = FastAPI(
    title="Cek Bansos API",
    description="API service to check NIK status on Kemensos Cek Bansos website",
    version="1.0.0"
)

class NIKRequest(BaseModel):
    nik: str = Field(..., min_length=16, max_length=16, pattern=r"^\d{16}$")

class NIKResponse(BaseModel):
    status: str
    nik: str
    data: dict

@app.get("/")
async def root():
    return {
        "service": "Cek Bansos API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/check-nik", response_model=NIKResponse)
async def check_nik(
    request: NIKRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        result = check_nik_bansos(request.nik)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking NIK: {str(e)}")
