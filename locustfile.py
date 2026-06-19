from locust import HttpUser, task, between
import logging

# Suppress excessive Locust info logs for cleaner output
logging.getLogger("locust").setLevel(logging.WARNING)

class EnterpriseBroker(HttpUser):
    # Simulate human behavior: wait 1 to 3 seconds between dashboard clicks
    wait_time = between(1, 3)
    
    def on_start(self):
        # Authenticate as the Enterprise Tenant (Ankit Realty)
        self.client.headers = {"X-API-Key": "vyk_live_test_12345"}

    @task(4)
    def view_cp_leaderboard(self):
        """
        Heavy SQL Aggregation: JOINs Deals, Leads, and Projects.
        This is the most likely endpoint to bottleneck the DB connection pool.
        """
        with self.client.get("/builder/analytics/cp-leaderboard", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with {response.status_code}")

    @task(3)
    def view_transit_heatmap(self):
        """Heavy SQL Aggregation: CASE statements and LEFT JOINs."""
        self.client.get("/builder/analytics/transit-heatmap")

    @task(2)
    def check_usage_billing(self):
        """Lightweight DB read: Usage log aggregation."""
        self.client.get("/billing/usage")
