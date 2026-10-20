"""
Unit tests for the timeline and task scheduling engine.
"""
import unittest
from datetime import date, timedelta
from services.timeline_engine import generate_default_timeline, evaluate_task_status

class TestTimelineEngine(unittest.TestCase):
    def test_tasks_generated_with_valid_dates(self):
        today = date.today()
        event_date_str = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        tasks = generate_default_timeline("wedding", event_date_str, base_date=today)
        self.assertTrue(len(tasks) >= 5)
        for t in tasks:
            self.assertTrue(t["due_date"] >= today.strftime("%Y-%m-%d"))
            self.assertTrue(t["due_date"] <= event_date_str)

    def test_short_notice_event_scaling(self):
        # Event is only 5 days away
        today = date.today()
        event_date_str = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        tasks = generate_default_timeline("birthday", event_date_str, base_date=today)
        self.assertTrue(len(tasks) > 0)
        for t in tasks:
            # Must be within [today, event_date]
            self.assertTrue(t["due_date"] >= today.strftime("%Y-%m-%d"))
            self.assertTrue(t["due_date"] <= event_date_str)

    def test_overdue_task_detection(self):
        today = date.today()
        overdue_task = {
            "title": "Book Venue",
            "due_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "is_completed": 0
        }
        evaluated = evaluate_task_status(overdue_task, current_date=today)
        self.assertTrue(evaluated["is_overdue"])
        self.assertEqual(evaluated["days_until_due"], -2)

    def test_completed_task_not_flagged_overdue(self):
        today = date.today()
        completed_task = {
            "title": "Book Venue",
            "due_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "is_completed": 1
        }
        evaluated = evaluate_task_status(completed_task, current_date=today)
        self.assertFalse(evaluated["is_overdue"])

if __name__ == "__main__":
    unittest.main()
