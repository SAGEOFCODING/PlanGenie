"""
Validation module: Sanitizes and rigorously validates user inputs
for event creation and update requests.
"""
from datetime import datetime, date
from typing import Dict, Any, Tuple
from config import Config

def validate_event_input(data: Dict[str, Any], is_update: bool = False) -> Tuple[bool, Dict[str, Any], Dict[str, str]]:
    """
    Validates event input payload.
    Returns (is_valid, sanitized_dict, errors_dict).
    """
    errors = {}
    sanitized = {}

    # 1. Event Name
    name = str(data.get("name", "")).strip()
    if not name:
        errors["name"] = "Event name is required."
    elif len(name) < 2:
        errors["name"] = "Event name must be at least 2 characters long."
    elif len(name) > Config.MAX_NAME_LENGTH:
        errors["name"] = f"Event name cannot exceed {Config.MAX_NAME_LENGTH} characters."
    else:
        sanitized["name"] = name

    # 2. Category
    category = str(data.get("category", "")).strip().lower()
    if category not in Config.VALID_CATEGORIES:
        errors["category"] = f"Category must be one of: {', '.join(Config.VALID_CATEGORIES)}."
    else:
        sanitized["category"] = category

    # 3. Event Date
    date_str = str(data.get("event_date", "")).strip()
    if not date_str:
        errors["event_date"] = "Event date is required (YYYY-MM-DD)."
    else:
        try:
            event_dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = date.today()
            if event_dt < today:
                errors["event_date"] = "Event date cannot be in the past. Please select today or a future date."
            else:
                sanitized["event_date"] = date_str
        except ValueError:
            errors["event_date"] = "Invalid date format. Expected YYYY-MM-DD."

    # 4. Location
    location = str(data.get("location", "")).strip()
    if not location:
        errors["location"] = "Location or city is required."
    elif len(location) < 2:
        errors["location"] = "Location must be at least 2 characters long."
    elif len(location) > Config.MAX_LOCATION_LENGTH:
        errors["location"] = f"Location cannot exceed {Config.MAX_LOCATION_LENGTH} characters."
    else:
        sanitized["location"] = location

    # 5. Guests
    raw_guests = data.get("guests")
    if raw_guests is None or str(raw_guests).strip() == "":
        errors["guests"] = "Guest count is required."
    else:
        try:
            guests = int(raw_guests)
            if guests < Config.MIN_GUESTS:
                errors["guests"] = f"Guest count must be at least {Config.MIN_GUESTS}."
            elif guests > Config.MAX_GUESTS:
                errors["guests"] = f"Guest count cannot exceed {Config.MAX_GUESTS:,}."
            else:
                sanitized["guests"] = guests
        except (ValueError, TypeError):
            errors["guests"] = "Guest count must be a valid whole number."

    # 6. Budget
    raw_budget = data.get("budget")
    if raw_budget is None or str(raw_budget).strip() == "":
        errors["budget"] = "Total budget is required."
    else:
        try:
            # Strip formatting like commas or currency symbols if entered
            clean_budget_str = str(raw_budget).replace(",", "").replace("₹", "").replace("$", "").replace("€", "").replace("£", "").strip()
            budget = int(float(clean_budget_str))
            if budget < Config.MIN_BUDGET:
                errors["budget"] = f"Budget must be at least {Config.MIN_BUDGET}."
            elif budget > Config.MAX_BUDGET:
                errors["budget"] = f"Budget cannot exceed {Config.MAX_BUDGET:,}."
            else:
                sanitized["budget"] = budget
        except (ValueError, TypeError):
            errors["budget"] = "Budget must be a valid positive number."

    # 7. Currency
    currency = str(data.get("currency", "INR")).strip().upper()
    if currency not in Config.SUPPORTED_CURRENCIES:
        sanitized["currency"] = "INR"
    else:
        sanitized["currency"] = currency

    # 8. Personalization fields (optional, sanitized)
    sanitized["theme"] = str(data.get("theme", "")).strip()[:Config.MAX_THEME_LENGTH]
    sanitized["priorities"] = str(data.get("priorities", "")).strip()[:Config.MAX_NOTES_LENGTH]
    venue_type = str(data.get("venue_type", "indoor")).strip().lower()
    sanitized["venue_type"] = venue_type if venue_type in ("indoor", "outdoor", "hybrid") else "indoor"
    sanitized["dietary"] = str(data.get("dietary", "")).strip()[:Config.MAX_NOTES_LENGTH]
    sanitized["accessibility"] = str(data.get("accessibility", "")).strip()[:Config.MAX_NOTES_LENGTH]
    sanitized["notes"] = str(data.get("notes", "")).strip()[:Config.MAX_NOTES_LENGTH]

    is_valid = len(errors) == 0
    return is_valid, sanitized, errors
