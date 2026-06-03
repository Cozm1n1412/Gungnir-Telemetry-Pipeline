import os
import time
import json
import redis
import psutil
from database import get_db_connection, init_db

init_db()

REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    print("[Gungnir Worker] Connected to Redis buffer.")
except Exception as e:
    print(f"[Gungnir Worker] Redis Connection Error: {e}")
    exit(1)

print("[Gungnir Worker] Ingestion & Persistence pipeline is live.")

counter = 0

while True:
    try:
        metrics = {
            "timestamp": int(time.time()),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "ram_usage": psutil.virtual_memory().percent
        }
        
        r.lpush("telemetry_stream", json.dumps(metrics))
        r.ltrim("telemetry_stream", 0, 3599)
        print(f"[Gungnir Worker] RAM Buffer Stream: {metrics}")
        
        counter += 1
        
        if counter % 10 == 0:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO system_metrics (timestamp, cpu_usage, ram_usage) VALUES (%s, %s, %s);",
                    (metrics["timestamp"], metrics["cpu_usage"], metrics["ram_usage"])
                )
                conn.commit()
                cur.close()
                conn.close()
                print(f"[Gungnir Worker] Persistent Storage Flush: Saved snapshot to PostgreSQL.")
            except Exception as db_err:
                print(f"[Gungnir Worker] PostgreSQL Flush Failed: {db_err}")

    except Exception as e:
        print(f"[Gungnir Worker] General execution loop failed: {e}")
        time.sleep(2)
