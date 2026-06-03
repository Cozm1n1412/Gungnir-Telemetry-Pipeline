import os
import json
import redis
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Gungnir Telemetry API", version="1.0.0")
REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except Exception as e:
    print(f"[Gungnir API] Failed to connect to Redis: {e}")

@app.get("/health")
async def health_check():
    return {"status": "online", "service": "gungnir-api"}

@app.get("/api/live")
async def get_live_metrics():
    try:
        raw_data = r.lindex("telemetry_stream", 0)
        if not raw_data:
            raise HTTPException(status_code=404, detail="No telemetry data available yet.")
        return json.loads(raw_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database memory read error: {e}")

@app.get("/api/history")
async def get_metric_history():
    try:
        raw_history = r.lrange("telemetry_stream", 0, 99)
        history = [json.loads(item) for item in raw_history]
        return {"count": len(history), "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")
