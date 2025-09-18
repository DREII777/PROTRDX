"""Simple password-based authentication middleware."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .config import get_settings


async def require_admin_password(x_admin_password: str = Header(..., alias="x-admin-password")) -> None:
    """Validate admin password header."""

    settings = get_settings()
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")


def optional_admin_header(password: str | None = Header(None, alias="x-admin-password")) -> None:
    """Optional dependency to apply to read endpoints."""

    if password is None:
        return
    settings = get_settings()
    if password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")


def admin_required_dependency() -> Depends:
    """Return dependency requiring admin password."""

    return Depends(require_admin_password)
