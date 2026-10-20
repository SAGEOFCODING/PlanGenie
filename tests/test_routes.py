"""
Integration tests for Flask application HTTP routes and REST endpoints.
"""
import os
import tempfile
import unittest
import json
from datetime import date, timedelta
from app import app, db

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        app.config["DATABASE_PATH"] = self.temp_db_path
        app.config["TESTING"] = True
        self.client = app.test_client()
        
        # Re-initialize db with temporary file
        db.db_path = self.temp_db_path
        db.init_db()
        
        self.future_date = (date.today() + timedelta(days=40)).strftime("%Y-%m-%d")

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_config_endpoint(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("ai_available", data)
        self.assertIn("supported_currencies", data)

    def test_create_event_valid(self):
        payload = {
            "name": "Kavya's 25th Birthday",
            "category": "birthday",
            "event_date": self.future_date,
            "location": "Mumbai",
            "guests": 40,
            "budget": 60000,
            "currency": "INR",
            "theme": "Retro Disco 90s",
            "priorities": "Fun photo booth and custom chocolate truffle cake"
        }
        response = self.client.post("/api/events", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("event_id", data)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["event"]["name"], "Kavya's 25th Birthday")
        self.assertTrue(len(data["data"]["budget"]) > 0)
        self.assertTrue(len(data["data"]["tasks"]) > 0)

    def test_create_event_invalid_missing_fields(self):
        response = self.client.post("/api/events", json={"name": ""})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    def test_get_event(self):
        # Create event first
        payload = {
            "name": "Annual RWA Meet",
            "category": "community",
            "event_date": self.future_date,
            "location": "Community Center",
            "guests": 150,
            "budget": 80000,
            "currency": "INR"
        }
        create_res = self.client.post("/api/events", json=payload)
        event_id = create_res.get_json()["event_id"]

        get_res = self.client.get(f"/api/events/{event_id}")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["event"]["id"], event_id)

    def test_update_budget_actual_spending(self):
        payload = {
            "name": "Test Event",
            "category": "wedding",
            "event_date": self.future_date,
            "location": "Jaipur",
            "guests": 100,
            "budget": 500000
        }
        create_res = self.client.post("/api/events", json=payload)
        event_id = create_res.get_json()["event_id"]
        budget_items = create_res.get_json()["data"]["budget"]
        first_item_id = budget_items[0]["id"]

        # Log actual spend
        patch_res = self.client.patch(
            f"/api/events/{event_id}/budget/{first_item_id}",
            json={"actual_amount": 55000, "notes": "Advance paid"}
        )
        self.assertEqual(patch_res.status_code, 200)
        data = patch_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["budget_summary"]["total_actual"], 55000)

    def test_toggle_task_completion(self):
        payload = {
            "name": "Task Event",
            "category": "birthday",
            "event_date": self.future_date,
            "location": "Delhi",
            "guests": 25,
            "budget": 25000
        }
        create_res = self.client.post("/api/events", json=payload)
        event_id = create_res.get_json()["event_id"]
        task_id = create_res.get_json()["data"]["tasks"][0]["id"]

        # Mark completed
        patch_res = self.client.patch(f"/api/events/{event_id}/tasks/{task_id}", json={"is_completed": True})
        self.assertEqual(patch_res.status_code, 200)
        tasks = patch_res.get_json()["tasks"]
        target = next(t for t in tasks if t["id"] == task_id)
        self.assertEqual(target["is_completed"], 1)

    def test_update_vendor_status(self):
        payload = {
            "name": "Vendor Event",
            "category": "community",
            "event_date": self.future_date,
            "location": "Park",
            "guests": 200,
            "budget": 100000
        }
        create_res = self.client.post("/api/events", json=payload)
        event_id = create_res.get_json()["event_id"]
        vendor_id = create_res.get_json()["data"]["vendors"][0]["id"]

        patch_res = self.client.patch(
            f"/api/events/{event_id}/vendors/{vendor_id}",
            json={"status": "hired", "notes": "Agreement signed with 20% advance"}
        )
        self.assertEqual(patch_res.status_code, 200)
        vendors = patch_res.get_json()["vendors"]
        target = next(v for v in vendors if v["id"] == vendor_id)
        self.assertEqual(target["status"], "hired")

    def test_delete_event(self):
        payload = {
            "name": "To be deleted",
            "category": "birthday",
            "event_date": self.future_date,
            "location": "Pune",
            "guests": 15,
            "budget": 15000
        }
        create_res = self.client.post("/api/events", json=payload)
        event_id = create_res.get_json()["event_id"]

        del_res = self.client.delete(f"/api/events/{event_id}")
        self.assertEqual(del_res.status_code, 200)

        get_res = self.client.get(f"/api/events/{event_id}")
        self.assertEqual(get_res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
