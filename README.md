# Gungnir - Minimalist Systems Telemetry Pipeline

Named after Odin's spear because the request-response cycle is designed to hit the target and return to the operator without dropping packages. 

This is a containerized, bare-bones telemetry pipeline built to stream host metrics (CPU, RAM, system load) and handle high-frequency write loads without choking the disk I/O.

## The Architecture Problem

Dumping real-time, per-second metrics directly into a relational database like PostgreSQL causes heavy disk serialization bottlenecks. Under stress, the database chokes on I/O operations.

Gungnir fixes this by splitting the data path into an in-memory write buffer and a persistent time-series store.

## Flow

Host Metrics (psutil) -> Python Ingestion Worker -> Redis (RAM Write-Buffer)
                                                         │
                                                         ▼ (Aggregation / Flush)
Client Request -> Nginx (Port 80) -> FastAPI Backend -> PostgreSQL (Persistent Storage)

## Technical Specifications

* **Ingestion:** A Python script runs an infinite loop inside an isolated container, using `psutil` to extract kernel metrics from the Arch Linux host. It streams data directly to Redis.
* **Buffer Layer:** Redis takes the high-frequency metrics in memory. This eliminates direct disk overhead during traffic spikes.
* **Persistence:** A background routine aggregates the raw metrics from Redis, compresses them into time-stamped series, and commits them to PostgreSQL.
* **API & Proxy:** Nginx acts as a reverse proxy on port 80, forwarding traffic to a FastAPI instance. 
* **Caching Strategy:** FastAPI reads live data directly from Redis RAM for low latency. Long-term analytical queries fallback to interogating PostgreSQL.

## Stack

* Host OS: Arch Linux
* Core: Docker / Docker Compose
* Proxy: Nginx
* Backend: Python 3 / FastAPI / Uvicorn / Psutil
* Data: Redis & PostgreSQL

## Deployment

To spin up the entire infrastructure with persistent volumes and isolated bridge networks:

```bash
docker compose up -d --build
