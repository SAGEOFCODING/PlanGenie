"""
Unit tests for input validation module.
"""
import unittest
from datetime import date, timedelta
from validation import validate_event_input

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.future_date = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")

    def test_valid_wedding(self):
        data = {
            "name": "Aarav & Priya's Wedding",
            "category": "wedding",
            "event_date": self.future_date,
            "location": "Jaipur, Rajasthan",
            "guests": 250,
            "budget": 1500000,
            "currency": "INR",
            "theme": "Royal Rajasthani Heritage",
            "priorities": "Exquisite catering and royal floral ambiance",
            "venue_type": "hybrid",
            "dietary": "Pure vegetarian and Jain options",
            "accessibility": "Wheelchair access for grandparents"
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(sanitized["name"], "Aarav & Priya's Wedding")
        self.assertEqual(sanitized["category"], "wedding")
        self.assertEqual(sanitized["budget"], 1500000)
        self.assertEqual(sanitized["currency"], "INR")

    def test_valid_birthday(self):
        data = {
            "name": "Rohan's 10th Superhero Birthday",
            "category": "birthday",
            "event_date": self.future_date,
            "location": "Bengaluru",
            "guests": 35,
            "budget": 45000,
            "currency": "INR",
            "theme": "Avengers Superhero",
            "priorities": "Custom Iron Man cake and magic show"
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertTrue(is_valid)
        self.assertEqual(sanitized["category"], "birthday")
        self.assertEqual(sanitized["guests"], 35)

    def test_valid_community_event(self):
        data = {
            "name": "Indiranagar Clean Green Drive & Carnival",
            "category": "community",
            "event_date": self.future_date,
            "location": "Public Park, Indiranagar",
            "guests": 400,
            "budget": 120000,
            "currency": "INR"
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertTrue(is_valid)
        self.assertEqual(sanitized["category"], "community")

    def test_missing_required_fields(self):
        is_valid, sanitized, errors = validate_event_input({})
        self.assertFalse(is_valid)
        self.assertIn("name", errors)
        self.assertIn("category", errors)
        self.assertIn("event_date", errors)
        self.assertIn("location", errors)
        self.assertIn("guests", errors)
        self.assertIn("budget", errors)

    def test_past_event_date_rejected(self):
        past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")
        data = {
            "name": "Past Event",
            "category": "birthday",
            "event_date": past_date,
            "location": "Mumbai",
            "guests": 20,
            "budget": 20000
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertFalse(is_valid)
        self.assertIn("event_date", errors)

    def test_invalid_category_rejected(self):
        data = {
            "name": "Conference",
            "category": "corporate_expo",
            "event_date": self.future_date,
            "location": "Delhi",
            "guests": 50,
            "budget": 50000
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertFalse(is_valid)
        self.assertIn("category", errors)

    def test_negative_or_zero_budget_rejected(self):
        data = {
            "name": "Zero Budget Party",
            "category": "birthday",
            "event_date": self.future_date,
            "location": "Pune",
            "guests": 15,
            "budget": 0
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertFalse(is_valid)
        self.assertIn("budget", errors)

    def test_invalid_guest_count_rejected(self):
        data = {
            "name": "Negative Guest Event",
            "category": "community",
            "event_date": self.future_date,
            "location": "Kolkata",
            "guests": 0,
            "budget": 10000
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertFalse(is_valid)
        self.assertIn("guests", errors)

    def test_excessively_long_inputs_handled(self):
        long_name = "A" * 200
        data = {
            "name": long_name,
            "category": "wedding",
            "event_date": self.future_date,
            "location": "Goa",
            "guests": 100,
            "budget": 500000
        }
        is_valid, sanitized, errors = validate_event_input(data)
        self.assertFalse(is_valid)
        self.assertIn("name", errors)

if __name__ == "__main__":
    unittest.main()
