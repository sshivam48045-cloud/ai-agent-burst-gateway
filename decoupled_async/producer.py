from fastapi import FastAPI, HTTPException, Request
from confluent_kafka import Producer
import redis
import uuid
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, db=0)

# Kafka configuration with BACKPRESSURE buffer 
conf = {
    'bootstrap.servers': 'localhost:29092',
    'queue.buffering.max.messages': 100000, # Backpressure limit!
    'queue.buffering.max.ms': 50
}
producer = Producer(conf)

RATE_LIMIT = 5000 # Max 5000 requests per second allowed

@app.post("/api/v1/crawl_async")
async def async_crawl(request: Request):
    client_ip = request.client.host
    
    # 1. RATE LIMITING (Token Bucket using Redis)
    requests_today = r.incr(f"rate_limit:{client_ip}")
    if requests_today == 1:
        r.expire(f"rate_limit:{client_ip}", 1) # Reset every 1 second
    
    if requests_today > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate Limit Exceeded. Too Many Requests!")

    task_id = str(uuid.uuid4())
    payload = {"task_id": task_id, "source": "agent_request", "trust": 85, "freshness": 90, "popularity": 70, "content_score": 88}
    
    # 2. KAFKA BACKPRESSURE HANDLING
    try:
        # Pushing to Kafka 'crustdata-burst-stream'
        producer.produce('crustdata-burst-stream', value=json.dumps(payload).encode('utf-8'))
        producer.poll(0) # Non-blocking poll
    except BufferError:
        # Buffer full ho gaya babu! System bacha liya humne 503 bhej ke.
        raise HTTPException(status_code=503, detail="Server heavily loaded (Kafka Buffer Full). Applying Backpressure.")

    return {"status": "202 Accepted", "task_id": task_id, "message": "Queued for async processing"}
