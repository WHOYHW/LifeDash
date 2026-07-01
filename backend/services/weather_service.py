import os
import json
import time
import asyncio
import httpx
from typing import Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

SENIVERSE_KEY = os.getenv("SENIVERSE_API_KEY", "")
SENIVERSE_BASE = "https://api.seniverse.com/v3"

CACHE_EXPIRE = 600

redis_client = None
try:
    import redis
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )
    redis_client.ping()
    print("[缓存] Redis 连接成功")
except Exception as e:
    print(f"[缓存] Redis 连接失败，降级为内存缓存: {str(e)}")
    redis_client = None

memory_cache: Dict[str, Dict[str, Any]] = {}

def get_cache_key(city_code: str) -> str:
    return f"weather:{city_code}"

async def fetch_weather_from_api(city_code: str) -> Dict[str, Any]:
    if not SENIVERSE_KEY:
        raise Exception("SENIVERSE_API_KEY 未配置")

    async with httpx.AsyncClient(timeout=10.0) as client:
        now_resp, daily_resp = await asyncio.gather(
            client.get(
                f"{SENIVERSE_BASE}/weather/now.json",
                params={
                    "key": SENIVERSE_KEY,
                    "location": city_code,
                    "language": "zh-Hans",
                    "unit": "c",
                },
            ),
            client.get(
                f"{SENIVERSE_BASE}/weather/daily.json",
                params={
                    "key": SENIVERSE_KEY,
                    "location": city_code,
                    "language": "zh-Hans",
                    "unit": "c",
                    "start": 0,
                    "days": 3,
                },
            ),
        )
        now_data = now_resp.json()
        daily_data = daily_resp.json()

    if "results" not in now_data:
        error = now_data.get("status", "未知错误")
        raise Exception(f"天气API错误: {error}")

    result = now_data["results"][0]
    now = result.get("now", {})
    loc = result.get("location", {})

    humidity = 0
    wind_dir = ""
    wind_scale = 0
    forecast = []
    if "results" in daily_data and daily_data["results"]:
        daily_list = daily_data["results"][0].get("daily", [])
        for day in daily_list:
            forecast.append({
                "date": day.get("date", "")[:10],
                "text_day": day.get("text_day", ""),
                "text_night": day.get("text_night", ""),
                "temp_max": int(day.get("high", 0)),
                "temp_min": int(day.get("low", 0)),
            })
        if daily_list:
            today = daily_list[0]
            humidity = int(today.get("humidity", 0)) if today.get("humidity") else 0
            wind_dir = today.get("wind_direction", "")
            wind_scale = int(today.get("wind_scale", 0)) if today.get("wind_scale") else 0

    return {
        "now": {
            "city_code": loc.get("id", ""),
            "city_name": loc.get("name", ""),
            "temp": int(now.get("temperature", 0)),
            "text": now.get("text", ""),
            "wind_dir": wind_dir,
            "wind_scale": wind_scale,
            "humidity": humidity,
            "obs_time": result.get("last_update", ""),
        },
        "forecast": forecast,
    }

async def get_weather(city_code: str) -> Dict[str, Any]:
    cached_data = get_cached_weather(city_code)
    if cached_data:
        print(f"[缓存命中] {city_code}")
        return cached_data

    print(f"[API调用] {city_code}")
    data = await fetch_weather_from_api(city_code)
    cache_weather(city_code, data)
    return data

def get_cached_weather(city_code: str) -> Optional[Dict[str, Any]]:
    if redis_client:
        try:
            key = get_cache_key(city_code)
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"[缓存] Redis 获取失败: {str(e)}")

    cache = memory_cache.get(city_code)
    if not cache:
        return None

    now = time.time()
    if now - cache["timestamp"] > cache["expire"]:
        del memory_cache[city_code]
        return None

    return cache["data"]

def cache_weather(city_code: str, data: Dict[str, Any]):
    if redis_client:
        try:
            key = get_cache_key(city_code)
            redis_client.setex(key, CACHE_EXPIRE, json.dumps(data, ensure_ascii=False))
            return
        except Exception as e:
            print(f"[缓存] Redis 设置失败: {str(e)}")

    memory_cache[city_code] = {
        "data": data,
        "timestamp": time.time(),
        "expire": CACHE_EXPIRE,
    }

def get_all_cached_city_codes() -> list:
    if redis_client:
        try:
            keys = redis_client.keys("weather:*")
            return [k.replace("weather:", "") for k in keys]
        except Exception as e:
            print(f"[缓存] Redis 获取所有键失败: {str(e)}")
            return []

    return list(memory_cache.keys())

async def update_all_cached_weather():
    city_codes = get_all_cached_city_codes()
    if not city_codes:
        return

    print(f"[定时更新] 开始更新 {len(city_codes)} 个城市的天气缓存")
    tasks = [fetch_and_cache(city_code) for city_code in city_codes]
    await asyncio.gather(*tasks)

async def fetch_and_cache(city_code: str):
    try:
        data = await fetch_weather_from_api(city_code)
        cache_weather(city_code, data)
        print(f"[定时更新] 成功: {city_code}")
    except Exception as e:
        print(f"[定时更新] 失败 {city_code}: {str(e)}")

async def start_weather_cache_task():
    while True:
        try:
            await update_all_cached_weather()
        except Exception as e:
            print(f"[定时任务] 执行失败: {str(e)}")
        await asyncio.sleep(CACHE_EXPIRE)