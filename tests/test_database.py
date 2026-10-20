"""
Unit tests for SQLite database operations and persistence.
"""
import os
import unittest
import tempfile
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = Database(self.temp_db_path)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_create_and_get_event(self):
        event_data = {
            "name": "Sahil & Meera Wedding",
            "category": "wedding",
            "event_date": "2026-11-20",
            "location": "Udaipur",
            "guests": 200,
            "budget": 2000000,
            "currency": "INR",
            "theme": "Lake Palace Royale",
            "priorities": "Royal catering and traditional music",
            "venue_type": "outdoor",
            "ai_source": "fallback_planner",
            "plan_summary": "Initial wedding draft"
        }
        event_id = self.db.create_event(event_data)
        self.assertIsNotNone(event_id)

        retrieved = self.db.get_event(event_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Sahil & Meera Wedding")
        self.assertEqual(retrieved["budget"], 2000000)
        self.assertEqual(retrieved["currency"], "INR")

    def test_update_event(self):
        event_data = {
            "name": "Original Name",
            "category": "birthday",
            "event_date": "2026-12-15",
            "location": "Delhi",
            "guests": 30,
            "budget": 30000,
            "currency": "INR"
        }
        event_id = self.db.create_event(event_data)
        
        event_data["name"] = "Updated Name"
        event_data["budget"] = 40000
        updated = self.db.update_event(event_id, event_data)
        self.assertTrue(updated)

        retrieved = self.db.get_event(event_id)
        self.assertEqual(retrieved["name"], "Updated Name")
        self.assertEqual(retrieved["budget"], 40000)

    def test_cascade_delete_event(self):
        event_data = {
            "name": "Delete Me",
            "category": "community",
            "event_date": "2026-10-30",
            "location": "Mumbai",
            "guests": 100,
            "budget": 50000
        }
        event_id = self.db.create_event(event_data)
        self.db.set_budget_items(event_id, [{"category": "Venue", "estimated_amount": 20000}])
        self.db.set_tasks(event_id, [{"title": "Setup Stage", "due_date": "2026-10-29"}])
        self.db.set_vendor_items(event_id, [{"category": "Sound", "title": "Sound Guy"}])
        self.db.set_personalized_ideas(event_id, [{"category": "decor", "title": "Eco Decor", "description": "Plants"}])

        self.db.delete_event(event_id)
        self.assertIsNone(self.db.get_event(event_id))
        self.assertEqual(len(self.db.get_budget_items(event_id)), 0)
        self.assertEqual(len(self.db.get_tasks(event_id)), 0)
        self.assertEqual(len(self.db.get_vendor_items(event_id)), 0)
        self.assertEqual(len(self.db.get_personalized_ideas(event_id)), 0)

    def test_budget_item_crud(self):
        event_id = self.db.create_event({"name": "Test", "category": "wedding", "event_date": "2026-12-01", "location": "City", "guests": 50, "budget": 100000})
        item_id = self.db.add_budget_item(event_id, "Florals", estimated_amount=15000, actual_amount=0)
        self.assertIsNotNone(item_id)

        # Update actual spend
        self.db.update_budget_item(item_id, actual_amount=14500, notes="Under budget by 500")
        items = self.db.get_budget_items(event_id)
        self.assertEqual(items[0]["actual_amount"], 14500)
        self.assertEqual(items[0]["notes"], "Under budget by 500")

        # Delete item
        self.db.delete_budget_item(item_id)
        self.assertEqual(len(self.db.get_budget_items(event_id)), 0)

    def test_task_status_toggle(self):
        event_id = self.db.create_event({"name": "Test", "category": "birthday", "event_date": "2026-12-01", "location": "City", "guests": 20, "budget": 20000})
        task_id = self.db.add_task(event_id, "Order Balloons", "Get metallic colors", "2026-11-25", priority="medium")
        
        # Toggle to completed
        self.db.update_task_status(task_id, is_completed=True)
        tasks = self.db.get_tasks(event_id)
        self.assertEqual(tasks[0]["is_completed"], 1)

        # Toggle to incomplete
        self.db.update_task_status(task_id, is_completed=False)
        tasks = self.db.get_tasks(event_id)
        self.assertEqual(tasks[0]["is_completed"], 0)

    def test_list_events_with_summary(self):
        # Create two events
        ev1 = self.db.create_event({"name": "Summit 2026", "category": "corporate", "event_date": "2026-11-10", "location": "Bengaluru", "guests": 500, "budget": 500000})
        ev2 = self.db.create_event({"name": "Dinner Party", "category": "social", "event_date": "2026-11-12", "location": "Goa", "guests": 15, "budget": 40000})

        # Add budget and tasks to ev1
        self.db.add_budget_item(ev1, "Catering", 200000, 180000)
        self.db.add_budget_item(ev1, "Venue", 150000, 150000)
        t1 = self.db.add_task(ev1, "Sign NDA", "", "2026-11-01", priority="high")
        t2 = self.db.add_task(ev1, "Send Invites", "", "2026-11-02", priority="medium")
        self.db.update_task_status(t1, is_completed=True)

        summaries = self.db.list_events_with_summary()
        self.assertEqual(len(summaries), 2)

        # Map by id
        sum_map = {s["id"]: s for s in summaries}
        self.assertEqual(sum_map[ev1]["total_actual"], 330000)
        self.assertEqual(sum_map[ev1]["remaining_balance"], 170000)
        self.assertEqual(sum_map[ev1]["total_tasks"], 2)
        self.assertEqual(sum_map[ev1]["completed_tasks"], 1)

        self.assertEqual(sum_map[ev2]["total_actual"], 0)
        self.assertEqual(sum_map[ev2]["remaining_balance"], 40000)
        self.assertEqual(sum_map[ev2]["total_tasks"], 0)
        self.assertEqual(sum_map[ev2]["completed_tasks"], 0)

if __name__ == "__main__":
    unittest.main()

