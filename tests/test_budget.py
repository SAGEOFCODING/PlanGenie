"""
Unit tests for the budget calculation and allocation engine.
"""
import unittest
from services.budget_engine import generate_default_budget_allocation, calculate_budget_summary

class TestBudgetEngine(unittest.TestCase):
    def test_wedding_budget_allocation_sums_exactly(self):
        budgets = [100000, 500000, 1500000, 3333333, 5000000]
        for b in budgets:
            items = generate_default_budget_allocation("wedding", b)
            total_allocated = sum(item["estimated_amount"] for item in items)
            self.assertEqual(total_allocated, b, f"Failed for budget {b}: got {total_allocated}")

    def test_birthday_budget_allocation_sums_exactly(self):
        budgets = [15000, 45000, 100000, 250000]
        for b in budgets:
            items = generate_default_budget_allocation("birthday", b)
            total_allocated = sum(item["estimated_amount"] for item in items)
            self.assertEqual(total_allocated, b, f"Failed for budget {b}: got {total_allocated}")

    def test_community_budget_allocation_sums_exactly(self):
        budgets = [50000, 120000, 800000, 2000000]
        for b in budgets:
            items = generate_default_budget_allocation("community", b)
            total_allocated = sum(item["estimated_amount"] for item in items)
            self.assertEqual(total_allocated, b, f"Failed for budget {b}: got {total_allocated}")

    def test_budget_summary_normal_spend(self):
        total_budget = 100000
        items = [
            {"category": "Venue", "estimated_amount": 40000, "actual_amount": 38000},
            {"category": "Catering", "estimated_amount": 40000, "actual_amount": 42000},
            {"category": "Decor", "estimated_amount": 20000, "actual_amount": 15000}
        ]
        summary = calculate_budget_summary(total_budget, items)
        self.assertEqual(summary["total_budget"], 100000)
        self.assertEqual(summary["total_estimated"], 100000)
        self.assertEqual(summary["total_actual"], 95000)
        self.assertEqual(summary["remaining_balance"], 5000)
        self.assertEqual(summary["unallocated_reserve"], 0)
        self.assertEqual(summary["utilization_pct"], 95.0)
        self.assertFalse(summary["is_over_budget"])
        self.assertFalse(summary["is_over_allocated"])

    def test_budget_summary_over_budget_warning(self):
        total_budget = 50000
        items = [
            {"category": "Venue", "estimated_amount": 30000, "actual_amount": 35000},
            {"category": "Catering", "estimated_amount": 20000, "actual_amount": 22000}
        ]
        summary = calculate_budget_summary(total_budget, items)
        self.assertTrue(summary["is_over_budget"])
        self.assertEqual(summary["total_actual"], 57000)
        self.assertEqual(summary["remaining_balance"], -7000)
        self.assertTrue(len(summary["warnings"]) > 0)

    def test_category_overspend_detection(self):
        total_budget = 100000
        items = [
            {"category": "Venue", "estimated_amount": 25000, "actual_amount": 30000},
            {"category": "Catering", "estimated_amount": 40000, "actual_amount": 35000}
        ]
        summary = calculate_budget_summary(total_budget, items)
        self.assertEqual(len(summary["category_overspends"]), 1)
        self.assertIn("Venue", summary["category_overspends"][0])

if __name__ == "__main__":
    unittest.main()
