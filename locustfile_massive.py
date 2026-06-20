from locust import HttpUser, task, between
import random

class HomeBuyer(HttpUser):
    wait_time = between(10, 30)
    weight = 50 
    @task
    def send_whatsapp_message(self):
        payload = {"messages": [{"from": f"91{random.randint(7000000000, 9999999999)}", "to": "919999999999", "from_name": "Mumbai Buyer", "type": "text", "text": {"body": f"Hi, looking for 2BHK. My salary is {random.randint(50, 300)}k and no EMI."}}]}
        self.client.post("/whatsapp/webhook", json=payload)

class Broker(HttpUser):
    wait_time = between(2, 5)
    weight = 20
    def on_start(self):
        self.client.headers = {"X-API-Key": "vyk_live_test_12345"}
    @task(3)
    def view_billing(self):
        self.client.get("/billing/usage")
    @task(2)
    def view_pipeline(self):
        self.client.get("/builder/analytics/cp-leaderboard")

class Builder(HttpUser):
    wait_time = between(5, 15)
    weight = 10
    def on_start(self):
        self.client.headers = {"X-API-Key": "vyk_live_test_12345"}
    @task
    def view_heatmap(self):
        self.client.get("/builder/analytics/transit-heatmap")

class ChannelPartner(HttpUser):
    wait_time = between(5, 10)
    weight = 15
    # FIX: Inject API Key so the 401 Unauthorized errors stop
    def on_start(self):
        self.client.headers = {"X-API-Key": "vyk_live_test_12345"}
    @task
    def check_commission(self):
        self.client.get("/deals/cp/ledger/Ramesh%20CP")

class LoanDSA(HttpUser):
    wait_time = between(3, 8)
    weight = 5
    def on_start(self):
        self.client.headers = {"X-API-Key": "vyk_live_test_12345"}
    @task(2)
    def browse_leads(self):
        self.client.get("/dsa/leads/available?dsa_phone=919000000001")
    @task(1)
    def bid_on_lead(self):
        lead_id = random.choice([2, 3, 4, 5])
        self.client.post(f"/dsa/leads/{lead_id}/unlock?dsa_phone=919000000001", json={"lead_id": lead_id, "max_bid": 1000.0})
