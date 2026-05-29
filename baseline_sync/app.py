from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

@app.get("/api/v1/crawl")
async def sync_crawl():
    # Ee synchronous blocking call baa babu! Yahi system ko choke karega.
    time.sleep(2) # Simulating heavy web scraping time
    return {"status": "success", "data": "Raw Data Fetched", "latency": "High"}
