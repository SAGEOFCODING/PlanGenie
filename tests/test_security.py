"""
Security test suite for PlanGenie.
Verifies security headers, Content Security Policy (CSP), IDOR protection,
safe error handling, and input validation bounds.
"""
import os
import tempfile
import unittest
from datetime import date, timedelta
from app import app, rate_limiter
from database import Database

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = Database(self.temp_db_path)
        app.config["DATABASE_PATH"] = self.temp_db_path
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Patch the global db instance in app
        import app as app_module
        app_module.db = self.db

        self.future_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_security_headers_present_on_html(self):
        """Verifies that all required defensive HTTP security headers are set."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        headers = res.headers
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertEqual(headers.get("Cross-Origin-Opener-Policy"), "same-origin")
        self.assertIn("camera=()", headers.get("Permissions-Policy", ""))
        self.assertIn("default-src 'self'", headers.get("Content-Security-Policy", ""))
        self.assertIn("frame-ancestors 'none'", headers.get("Content-Security-Policy", ""))

    def test_security_headers_present_on_api(self):
        """Verifies security and no-store headers on API responses."""
        res = self.client.get("/api/events")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

    def test_api_404_safe_json(self):
        """Verifies 404 on API endpoints returns non-leaking JSON without stack traces."""
        res = self.client.get("/api/events/9999999")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertIn("not found", data.get("error", "").lower())

    def test_api_405_method_not_allowed(self):
        """Verifies 405 Method Not Allowed returns structured JSON."""
        res = self.client.delete("/api/events")
        self.assertEqual(res.status_code, 405)
        data = res.get_json()
        self.assertFalse(data.get("success"))

    def test_idor_protection_tasks(self):
        """Verifies that a task belonging to Event A cannot be manipulated via Event B's endpoint."""
        ev_a = self.db.create_event({"name": "Event A", "category": "wedding", "event_date": self.future_date, "location": "City A", "guests": 50, "budget": 100000})
        ev_b = self.db.create_event({"name": "Event B", "category": "birthday", "event_date": self.future_date, "location": "City B", "guests": 20, "budget": 20000})

        task_a_id = self.db.add_task(ev_a, "Task A", "Description", self.future_date, "high", "General")

        # Attempt to patch Event A's task through Event B's route
        patch_res = self.client.patch(f"/api/events/{ev_b}/tasks/{task_a_id}", json={"is_completed": True})
        self.assertEqual(patch_res.status_code, 404)

        # Attempt to delete Event A's task through Event B's route
        del_res = self.client.delete(f"/api/events/{ev_b}/tasks/{task_a_id}")
        self.assertEqual(del_res.status_code, 404)

        # Confirm Task A was NOT modified or deleted
        tasks_a = self.db.get_tasks(ev_a)
        self.assertEqual(len(tasks_a), 1)
        self.assertEqual(tasks_a[0]["is_completed"], 0)

    def test_idor_protection_budget(self):
        """Verifies that a budget item belonging to Event A cannot be manipulated via Event B's endpoint."""
        ev_a = self.db.create_event({"name": "Event A", "category": "wedding", "event_date": self.future_date, "location": "City A", "guests": 50, "budget": 100000})
        ev_b = self.db.create_event({"name": "Event B", "category": "birthday", "event_date": self.future_date, "location": "City B", "guests": 20, "budget": 20000})

        b_item_a = self.db.add_budget_item(ev_a, "Venue", 50000, 0, "essential", "")

        # Attempt to patch through Event B's route
        patch_res = self.client.patch(f"/api/events/{ev_b}/budget/{b_item_a}", json={"actual_amount": 45000})
        self.assertEqual(patch_res.status_code, 404)

        # Attempt to delete through Event B's route
        del_res = self.client.delete(f"/api/events/{ev_b}/budget/{b_item_a}")
        self.assertEqual(del_res.status_code, 404)

        # Confirm item was NOT modified
        items_a = self.db.get_budget_items(ev_a)
        self.assertEqual(len(items_a), 1)
        self.assertEqual(items_a[0]["actual_amount"], 0)

    def test_idor_protection_vendors(self):
        """Verifies that a vendor item belonging to Event A cannot be manipulated via Event B's endpoint."""
        ev_a = self.db.create_event({"name": "Event A", "category": "wedding", "event_date": self.future_date, "location": "City A", "guests": 50, "budget": 100000})
        ev_b = self.db.create_event({"name": "Event B", "category": "birthday", "event_date": self.future_date, "location": "City B", "guests": 20, "budget": 20000})

        vendor_a = self.db.add_vendor_item(ev_a, "Photo", "Studio X", "Photography", "not_contacted", "", 25000)

        # Attempt to patch through Event B's route
        patch_res = self.client.patch(f"/api/events/{ev_b}/vendors/{vendor_a}", json={"status": "hired"})
        self.assertEqual(patch_res.status_code, 404)

        # Attempt to delete through Event B's route
        del_res = self.client.delete(f"/api/events/{ev_b}/vendors/{vendor_a}")
        self.assertEqual(del_res.status_code, 404)

        # Confirm item was NOT modified
        vendors_a = self.db.get_vendor_items(ev_a)
        self.assertEqual(len(vendors_a), 1)
        self.assertEqual(vendors_a[0]["status"], "not_contacted")

    def test_input_validation_invalid_task_date(self):
        """Verifies that invalid date format is rejected on task creation."""
        ev = self.db.create_event({"name": "Test Event", "category": "wedding", "event_date": self.future_date, "location": "City", "guests": 20, "budget": 50000})
        res = self.client.post(f"/api/events/{ev}/tasks", json={
            "title": "Send Invites",
            "due_date": "not-a-real-date"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid date format", res.get_json()["error"])

    def test_non_json_payload_rejected(self):
        """Verifies that non-JSON request body to API POST/PATCH routes is safely rejected."""
        res = self.client.post("/api/events", data="invalid plain text", content_type="text/plain")
        self.assertEqual(res.status_code, 400)
        self.assertIn("JSON payload required", res.get_json()["error"])

    def test_in_memory_rate_limiter(self):
        """Directly tests sliding-window rate limiter logic."""
        test_key = "test_user_ip_123"
        # Allow 3 requests in a 10-second window
        self.assertTrue(rate_limiter.is_allowed(test_key, max_requests=3, window_seconds=10))
        self.assertTrue(rate_limiter.is_allowed(test_key, max_requests=3, window_seconds=10))
        self.assertTrue(rate_limiter.is_allowed(test_key, max_requests=3, window_seconds=10))
        # 4th request should be blocked
        self.assertFalse(rate_limiter.is_allowed(test_key, max_requests=3, window_seconds=10))

if __name__ == "__main__":
    unittest.main()
