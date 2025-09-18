"""Serve generated charts."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api", tags=["charts"])


@router.get("/charts/{filename}")
def get_chart(filename: str) -> FileResponse:
    path = Path("charts") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(path)
