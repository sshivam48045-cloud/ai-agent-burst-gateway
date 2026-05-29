from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(1)
    def test_baseline_sync(self):
        # Ee fail hoga under load
        self.client.get("http://localhost:8001/api/v1/crawl", name="GET /baseline")

    @task(3)
    def test_decoupled_async(self):
        # Ee rocket liyan udega!
        self.client.post("http://localhost:8000/api/v1/crawl_async", name="POST /decoupled")
