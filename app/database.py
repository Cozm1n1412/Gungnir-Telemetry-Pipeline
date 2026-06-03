import os
import time
import psycopg2

DB_HOST = os.getenv("POSTGRES_HOST", "postgres_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "trialbyfire")
DB_NAME = "gungnir_telemetry"

def get_db_connection():
    """Connecting to data base from container..."""
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def init_db():
    """Initialize temporal series table if it doesn't exist."""
    
    for i in range(5):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
        
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp BIGINT NOT NULL,
                    cpu_usage REAL NOT NULL,
                    ram_usage REAL NOT NULL
                );
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            print("[Gungnir DB] PostgreSQL tables initialized successfully.")
            return
        except Exception as e:
            print(f"[Gungnir DB] Connection attempt {i+1}/5 failed. Retrying in 3s... Error: {e}")
            time.sleep(3)
            
    print("[Gungnir DB] Critical: Could not connect to PostgreSQL container.")
    exit(1)

if __name__ == "__main__":
    
    init_db()
