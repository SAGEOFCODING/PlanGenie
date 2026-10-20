"""
Timeline Engine: Calculates actionable, event-specific task timelines.
Scales planning intervals dynamically for short-notice vs long-term events,
ensuring tasks never receive impossible or past deadlines.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

TIMELINE_TEMPLATES = {
    "wedding": [
        {"title": "Establish Guest List & Budget Caps", "desc": "Finalize primary headcount and allocate per-plate catering targets", "priority": "high", "offset_pct": 0.15, "category": "Planning"},
        {"title": "Shortlist & Book Venue / Banquet Hall", "desc": "Inspect venue capacity, parking, air conditioning, and power backup", "priority": "high", "offset_pct": 0.25, "category": "Venue"},
        {"title": "Book Caterer & Taste Menu Samples", "desc": "Confirm menu courses, vegetarian/vegan live counters, and servers", "priority": "high", "offset_pct": 0.40, "category": "Catering"},
        {"title": "Hire Photographer & Videographer", "desc": "Review portfolios, discuss traditional and candid coverage angles", "priority": "medium", "offset_pct": 0.50, "category": "Media"},
        {"title": "Finalize Decor Theme & Florals", "desc": "Select floral mandap/altar stage palette, lighting, and entrance arches", "priority": "medium", "offset_pct": 0.65, "category": "Decor"},
        {"title": "Send Invitations & Collect RSVPs", "desc": "Distribute digital and printed invitations; track dietary requests", "priority": "high", "offset_pct": 0.75, "category": "Guest Logistics"},
        {"title": "Confirm Attire, Tailoring & Makeup Artist", "desc": "Schedule final outfit fittings and bridal/groom styling trials", "priority": "medium", "offset_pct": 0.85, "category": "Styling"},
        {"title": "Vendor Walkthrough & Schedule Rehearsal", "desc": "Synchronize arrival times, power connections, and ceremonial cues", "priority": "high", "offset_pct": 0.95, "category": "Rehearsal"},
        {"title": "Final Readiness & Emergency Kit Check", "desc": "Pack safety pins, extra cash envelopes, first-aid, and contact sheet", "priority": "high", "offset_pct": 0.99, "category": "Readiness"}
    ],
    "birthday": [
        {"title": "Choose Theme & Pick Party Venue", "desc": "Select birthday theme (colors/characters) and secure room or home setup", "priority": "high", "offset_pct": 0.20, "category": "Venue & Theme"},
        {"title": "Order Custom Birthday Cake & Catering", "desc": "Confirm cake flavor, dietary needs, snacks, and beverage options", "priority": "high", "offset_pct": 0.45, "category": "Food & Cake"},
        {"title": "Send Digital Invitations & Collect RSVPs", "desc": "Share invite graphics with location map, start time, and RSVP deadline", "priority": "medium", "offset_pct": 0.60, "category": "Invitations"},
        {"title": "Purchase Theme Decorations & Balloons", "desc": "Gather balloon arch supplies, tableware, birthday banners, and photo props", "priority": "medium", "offset_pct": 0.75, "category": "Decor"},
        {"title": "Book Entertainer or Plan Party Games", "desc": "Organize music playlist, game host, prizes, and kid activities", "priority": "medium", "offset_pct": 0.85, "category": "Entertainment"},
        {"title": "Assemble Return Gift Favor Bags", "desc": "Pack customized goodies or theme keepsakes for attending guests", "priority": "low", "offset_pct": 0.92, "category": "Favors"},
        {"title": "Day-Before Space Setup & Cake Confirmation", "desc": "Verify bakery pickup/delivery time and prep decorations", "priority": "high", "offset_pct": 0.98, "category": "Setup"}
    ],
    "community": [
        {"title": "Define Objectives & Assemble Volunteer Committee", "desc": "Form core teams for safety, crowd flow, refreshments, and AV sound", "priority": "high", "offset_pct": 0.15, "category": "Organization"},
        {"title": "Secure Municipal Permits & Facility Booking", "desc": "Obtain park/hall approvals, civic clearances, noise permits, and insurance", "priority": "high", "offset_pct": 0.30, "category": "Permits"},
        {"title": "Book Stage, Audio-Visual & PA Sound System", "desc": "Coordinate microphones, speakers, generator backup, and technician", "priority": "high", "offset_pct": 0.50, "category": "Equipment"},
        {"title": "Launch Community Publicity & Signage Campaign", "desc": "Post posters, notify neighborhood groups, and share digital banners", "priority": "medium", "offset_pct": 0.65, "category": "Marketing"},
        {"title": "Arrange Waste Management & Hydration Stations", "desc": "Set up water refill points, segregated trash bins, and green team cleanup", "priority": "high", "offset_pct": 0.80, "category": "Sanitation"},
        {"title": "First Aid & Accessibility Readiness Check", "desc": "Confirm wheelchair ramps, shaded seating, and paramedic first-aid post", "priority": "high", "offset_pct": 0.90, "category": "Safety"},
        {"title": "Volunteer Briefing & Walkthrough", "desc": "Distribute volunteer badges, emergency contact list, and run sheet", "priority": "high", "offset_pct": 0.98, "category": "Coordination"}
    ]
}

def generate_default_timeline(category: str, event_date_str: str, base_date: date = None) -> List[Dict[str, Any]]:
    """
    Generates actionable tasks with calculated due dates based on the event date.
    Dynamically scales intervals between today and event_date so tasks are never in the past.
    """
    if base_date is None:
        base_date = date.today()
        
    try:
        event_dt = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        event_dt = base_date + timedelta(days=30)
        
    days_available = max(1, (event_dt - base_date).days)
    category_key = category.lower().strip()
    template = TIMELINE_TEMPLATES.get(category_key, TIMELINE_TEMPLATES["community"])
    
    tasks = []
    for item in template:
        offset_pct = item.get("offset_pct", 0.5)
        # Calculate task due date as a fraction of the available window
        day_offset = int(round(days_available * offset_pct))
        # Ensure task due date is between base_date and event_dt
        day_offset = max(0, min(day_offset, days_available))
        task_due_date = base_date + timedelta(days=day_offset)
        
        # If task due date exceeds event_dt, cap at event_dt
        if task_due_date > event_dt:
            task_due_date = event_dt
            
        tasks.append({
            "title": item["title"],
            "description": item["desc"],
            "due_date": task_due_date.strftime("%Y-%m-%d"),
            "priority": item["priority"],
            "is_completed": 0,
            "category": item.get("category", "General")
        })
        
    # Sort tasks by due date
    tasks.sort(key=lambda t: t["due_date"])
    return tasks

def evaluate_task_status(task: Dict[str, Any], current_date: date = None) -> Dict[str, Any]:
    """
    Enriches a task with overdue and urgency indicators.
    """
    if current_date is None:
        current_date = date.today()
        
    due_date_str = task.get("due_date", "")
    is_completed = bool(task.get("is_completed", 0))
    
    is_overdue = False
    days_until_due = 0
    
    try:
        task_due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        days_until_due = (task_due - current_date).days
        if not is_completed and days_until_due < 0:
            is_overdue = True
    except (ValueError, TypeError):
        pass
        
    task_copy = dict(task)
    task_copy["is_overdue"] = is_overdue
    task_copy["days_until_due"] = days_until_due
    return task_copy
