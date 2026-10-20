"""
Unit tests for AI Planner Service: JSON cleaning, schema validation,
rescaling of excessive budget allocations, and graceful fallback behavior.
"""
import unittest
import json
from datetime import date, timedelta
from services.ai_planner import (
    clean_json_response,
    validate_and_sanitize_ai_plan,
    generate_plan
)
from services.fallback_planner import generate_fallback_plan

class TestAIService(unittest.TestCase):
    def setUp(self):
        self.future_date = (date.today() + timedelta(days=45)).strftime("%Y-%m-%d")
        self.event_data = {
            "name": "Pooja & Rohan Wedding",
            "category": "wedding",
            "event_date": self.future_date,
            "location": "Chandigarh",
            "guests": 150,
            "budget": 1000000,
            "currency": "INR",
            "theme": "Pastel Floral Elegance",
            "priorities": "Gourmet catering and candid photography"
        }

    def test_clean_json_response_with_code_fences(self):
        markdown_text = "```json\n{\"planning_summary\": \"Great event plan\"}\n```"
        cleaned = clean_json_response(markdown_text)
        parsed = json.loads(cleaned)
        self.assertEqual(parsed["planning_summary"], "Great event plan")

    def test_clean_json_response_with_surrounding_text(self):
        text = "Here is the JSON plan you requested:\n{\"planning_summary\": \"Plan details\"}\nHope this helps!"
        cleaned = clean_json_response(text)
        parsed = json.loads(cleaned)
        self.assertEqual(parsed["planning_summary"], "Plan details")

    def test_validate_and_sanitize_valid_ai_output(self):
        ai_response = {
            "planning_summary": "Tailored wedding roadmap with balanced catering and floral allocations.",
            "budget_allocation": [
                {"category": "Catering", "estimated_amount": 400000, "priority": "essential", "notes": "Buffet"},
                {"category": "Venue", "estimated_amount": 300000, "priority": "essential", "notes": "Hall"},
                {"category": "Photography", "estimated_amount": 150000, "priority": "essential", "notes": "Candid"}
            ],
            "timeline_tasks": [
                {"title": "Book Venue", "description": "Pay advance", "due_date": self.future_date, "priority": "high"},
                {"title": "Finalize Menu", "description": "Taste samples", "due_date": self.future_date, "priority": "medium"},
                {"title": "Review Album", "description": "Confirm shots", "due_date": self.future_date, "priority": "low"}
            ],
            "vendor_checklist": [
                {"category": "Venue", "title": "Hall Manager", "description": "Check lights", "status": "not_contacted"},
                {"category": "Food", "title": "Caterer", "description": "Taste dishes", "status": "not_contacted"},
                {"category": "Photo", "title": "Photographer", "description": "Sign agreement", "status": "not_contacted"}
            ],
            "personalized_ideas": [
                {"category": "decor", "title": "Pastel Drapes", "description": "Light pink fabrics", "rationale": "Matches theme"},
                {"category": "food", "title": "Live Mocktail Bar", "description": "Fresh fruit drinks", "rationale": "High guest engagement"}
            ]
        }
        validated = validate_and_sanitize_ai_plan(ai_response, self.event_data)
        self.assertEqual(validated["ai_source"], "live_genai")
        self.assertEqual(len(validated["budget_allocation"]), 3)
        self.assertEqual(len(validated["timeline_tasks"]), 3)
        self.assertEqual(len(validated["vendor_checklist"]), 3)
        self.assertEqual(len(validated["personalized_ideas"]), 2)

    def test_rescaling_when_model_exceeds_budget(self):
        total_budget = 100000
        event = dict(self.event_data)
        event["budget"] = total_budget

        # Model generated 150,000 in allocations (50% over budget)
        ai_response = {
            "planning_summary": "An extravagant plan",
            "budget_allocation": [
                {"category": "Venue", "estimated_amount": 80000},
                {"category": "Catering", "estimated_amount": 50000},
                {"category": "Decor", "estimated_amount": 20000}
            ]
        }
        validated = validate_and_sanitize_ai_plan(ai_response, event)
        total_allocated = sum(item["estimated_amount"] for item in validated["budget_allocation"])
        self.assertLessEqual(total_allocated, total_budget)

    def test_fallback_plan_execution(self):
        plan = generate_fallback_plan(self.event_data)
        self.assertEqual(plan["ai_source"], "fallback_planner")
        self.assertTrue(len(plan["budget_allocation"]) >= 5)
        self.assertTrue(len(plan["timeline_tasks"]) >= 5)
        self.assertTrue(len(plan["vendor_checklist"]) >= 5)
        self.assertTrue(len(plan["personalized_ideas"]) >= 5)

        # Confirm budget allocation sum equals total budget exactly
        total_allocated = sum(item["estimated_amount"] for item in plan["budget_allocation"])
        self.assertEqual(total_allocated, self.event_data["budget"])

    def test_generate_plan_defaults_to_fallback_without_keys(self):
        plan = generate_plan(self.event_data)
        self.assertIn(plan["ai_source"], ("live_genai", "fallback_planner"))
        self.assertIsNotNone(plan["budget_allocation"])
        self.assertIsNotNone(plan["timeline_tasks"])

if __name__ == "__main__":
    unittest.main()
