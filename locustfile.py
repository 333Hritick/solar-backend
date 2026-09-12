from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # seconds between requests

    @task
    def homepage(self):
        self.client.get("/")   # test homepage

    @task
    def login(self):
        self.client.post("/api/login/", json={
            "email": "test@example.com",
            "password": "password123"
        })
