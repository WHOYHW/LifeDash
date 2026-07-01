import os
import asyncio
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import httpx

from database import get_db
from models import User, UserCity
from routers.auth import get_current_user
from services.weather_service import get_weather

load_dotenv()

router = APIRouter(prefix="/api/weather", tags=["天气"])

SENIVERSE_KEY = os.getenv("SENIVERSE_API_KEY", "")
SENIVERSE_BASE = "https://api.seniverse.com/v3"


@router.get("/now")
async def get_now_weather(
    location: str = Query("beijing", description="城市名或ID，如 beijing、北京"),
):
    if not SENIVERSE_KEY:
        raise HTTPException(status_code=500, detail="SENIVERSE_API_KEY 未配置")

    try:
        data = await get_weather(location)
        return {
            "code": 200,
            "message": "success",
            "data": data.get("now", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/forecast")
async def get_forecast(
    location: str = Query("beijing", description="城市名或ID"),
    days: int = Query(3, ge=1, le=15, description="预报天数，最多15天"),
):
    if not SENIVERSE_KEY:
        raise HTTPException(status_code=500, detail="SENIVERSE_API_KEY 未配置")

    try:
        data = await get_weather(location)
        forecast_data = data.get("forecast", [])
        if days < len(forecast_data):
            forecast_data = forecast_data[:days]
        return {"code": 200, "message": "success", "data": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/city")
async def search_city(
    keyword: str = Query(..., min_length=1, description="城市名称，如北京"),
):
    if not SENIVERSE_KEY:
        raise HTTPException(status_code=500, detail="SENIVERSE_API_KEY 未配置")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{SENIVERSE_BASE}/weather/now.json",
                params={
                    "key": SENIVERSE_KEY,
                    "location": keyword,
                    "language": "zh-Hans",
                },
            )
            data = resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"城市搜索失败: {str(e)}")

    if "results" not in data:
        error = data.get("status", "未找到城市")
        raise HTTPException(status_code=404, detail=error)

    result = data["results"][0]
    loc = result.get("location", {})

    return {
        "code": 200,
        "message": "success",
        "data": {
            "code": loc.get("id", ""),
            "name": loc.get("name", ""),
            "path": loc.get("path", ""),
            "timezone": loc.get("timezone", ""),
        },
    }


@router.post("/city")
async def save_user_city(
    city_code: str = Query(..., description="城市ID"),
    city_name: str = Query(..., description="城市名称"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not hasattr(User, 'city_code'):
        raise HTTPException(status_code=500, detail="用户表缺少city_code字段，请先执行数据库迁移")

    setattr(current_user, 'city_code', city_code)
    setattr(current_user, 'city_name', city_name)
    db.commit()
    db.refresh(current_user)

    return {
        "code": 200,
        "message": "保存成功",
        "data": {"city_code": city_code, "city_name": city_name},
    }


@router.get("/cities")
async def get_user_cities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cities = db.query(UserCity).filter(
        UserCity.user_id == current_user.id
    ).order_by(UserCity.is_default.desc(), UserCity.sort_order.asc()).all()

    result = []
    for city in cities:
        result.append({
            "id": city.id,
            "city_code": city.city_code,
            "city_name": city.city_name,
            "is_default": city.is_default,
        })

    return {"code": 200, "message": "success", "data": result}


@router.post("/cities")
async def add_user_city(
    city_code: str = Query(..., description="城市代码"),
    city_name: str = Query(..., description="城市名称"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exists = db.query(UserCity).filter(
        UserCity.user_id == current_user.id,
        UserCity.city_code == city_code
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="该城市已在收藏列表中")

    city = UserCity(
        user_id=current_user.id,
        city_code=city_code,
        city_name=city_name,
        is_default=False,
        sort_order=0,
    )
    db.add(city)
    db.commit()
    db.refresh(city)

    return {
        "code": 200,
        "message": "收藏成功",
        "data": {
            "id": city.id,
            "city_code": city.city_code,
            "city_name": city.city_name,
            "is_default": city.is_default,
        },
    }


@router.delete("/cities/{city_code}")
async def delete_user_city(
    city_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    city = db.query(UserCity).filter(
        UserCity.user_id == current_user.id,
        UserCity.city_code == city_code
    ).first()

    if not city:
        raise HTTPException(status_code=404, detail="收藏的城市不存在")

    was_default = city.is_default
    db.delete(city)

    if was_default:
        next_city = db.query(UserCity).filter(
            UserCity.user_id == current_user.id
        ).order_by(UserCity.sort_order.asc()).first()
        if next_city:
            next_city.is_default = True

    db.commit()

    return {"code": 200, "message": "删除成功"}


@router.put("/cities/{city_code}/default")
async def set_default_city(
    city_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cities = db.query(UserCity).filter(
        UserCity.user_id == current_user.id
    ).all()

    target = None
    for city in cities:
        if city.city_code == city_code:
            target = city
            city.is_default = True
        else:
            city.is_default = False

    if not target:
        raise HTTPException(status_code=404, detail="收藏的城市不存在")

    db.commit()

    return {
        "code": 200,
        "message": "设置成功",
        "data": {
            "city_code": target.city_code,
            "city_name": target.city_name,
        },
    }