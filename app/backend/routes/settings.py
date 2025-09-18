"""Settings endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..core.database import get_session
from ..core.security import admin_required_dependency
from ..models.setting import Setting
from ..schemas.setting import SettingRead, SettingUpdate

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings", response_model=SettingRead, dependencies=[admin_required_dependency()])
def get_settings(session: Session = Depends(get_session)) -> Setting:
    setting = session.get(Setting, 1)
    if not setting:
        setting = Setting()
        session.add(setting)
        session.commit()
        session.refresh(setting)
    return setting


@router.post("/settings", response_model=SettingRead, dependencies=[admin_required_dependency()])
def update_settings(payload: SettingUpdate, session: Session = Depends(get_session)) -> Setting:
    setting = session.get(Setting, 1)
    if not setting:
        setting = Setting(**payload.dict())
        session.add(setting)
    else:
        for key, value in payload.dict().items():
            setattr(setting, key, value)
        session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting
