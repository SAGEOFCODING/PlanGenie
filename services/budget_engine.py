"""
Budget Engine: Mathematical allocation, tracking, and validation of event finances.
Ensures mathematical consistency using integer calculations to avoid floating-point drift.
"""
from typing import Dict, List, Any

# Proportional category allocations (percentages must sum to 100)
CATEGORY_TEMPLATES = {
    "wedding": [
        {"category": "Catering & Beverages", "pct": 35, "priority": "essential", "notes": "Multi-course meals, welcome drinks, desserts, and service staff"},
        {"category": "Venue & Mandap / Stage", "pct": 25, "priority": "essential", "notes": "Ceremony & reception hall rental, lighting, and power backup"},
        {"category": "Photography & Videography", "pct": 12, "priority": "essential", "notes": "Candid photos, pre-wedding shoot, ceremony coverage, teaser film"},
        {"category": "Decor, Floral & Lighting", "pct": 10, "priority": "essential", "notes": "Entrance arches, table centerpieces, floral mandap, ambient lights"},
        {"category": "Attire, Hair & Makeup", "pct": 8, "priority": "essential", "notes": "Bridal/Groom outfits, bridal makeup artists, hair styling"},
        {"category": "Music, DJ & Entertainment", "pct": 4, "priority": "optional", "notes": "Sound system, DJ, MC/host, traditional instrumentalists"},
        {"category": "Invitations & Favors", "pct": 2, "priority": "optional", "notes": "E-invites, physical cards, welcome kits and return gifts"},
        {"category": "Emergency Contingency Reserve", "pct": 4, "priority": "essential", "notes": "Buffer for unexpected last-minute requirements or extra guests"}
    ],
    "birthday": [
        {"category": "Food, Drinks & Birthday Cake", "pct": 40, "priority": "essential", "notes": "Custom theme cake, appetizers, main course, and kid-friendly beverages"},
        {"category": "Venue Rental & Setup", "pct": 20, "priority": "essential", "notes": "Party hall or cafe rental, seating arrangement, cleanup service"},
        {"category": "Theme Decor & Balloons", "pct": 15, "priority": "essential", "notes": "Balloon garland, backdrop banner, cutout props, tableware"},
        {"category": "Entertainment & Activities", "pct": 12, "priority": "essential", "notes": "Magician, games coordinator, face painter, DJ or music playlist"},
        {"category": "Party Favors & Invitations", "pct": 8, "priority": "optional", "notes": "Theme return gift hampers, digital animated invites"},
        {"category": "Emergency Contingency Reserve", "pct": 5, "priority": "essential", "notes": "Buffer for additional food orders, breakages, or overtime fee"}
    ],
    "community": [
        {"category": "Stage, Sound & AV Equipment", "pct": 25, "priority": "essential", "notes": "Microphones, PA speakers, projector screens, lighting truss, sound tech"},
        {"category": "Venue, Grounds & Municipal Permits", "pct": 20, "priority": "essential", "notes": "Park/auditorium booking, civic permits, police permission, insurance"},
        {"category": "Refreshments & Hydration Stations", "pct": 20, "priority": "essential", "notes": "Drinking water dispensers, light snacks, tea/coffee for attendees"},
        {"category": "Waste Management & Sanitation", "pct": 10, "priority": "essential", "notes": "Segregated trash cans, portable restrooms, post-event green cleanup team"},
        {"category": "Marketing, Banners & Signage", "pct": 10, "priority": "essential", "notes": "Directional signs, welcome banners, flyers, social media promotion"},
        {"category": "Safety, Security & First Aid", "pct": 8, "priority": "essential", "notes": "First aid paramedic desk, crowd control barricades, security volunteers"},
        {"category": "Emergency Contingency Reserve", "pct": 7, "priority": "essential", "notes": "Buffer for weather contingencies, equipment rentals, unexpected logistics"}
    ]
}

def generate_default_budget_allocation(category: str, total_budget: int) -> List[Dict[str, Any]]:
    """
    Allocates total_budget across relevant categories using integer arithmetic.
    Guarantees that the sum of allocated amounts equals total_budget exactly.
    """
    category_key = category.lower().strip()
    template = CATEGORY_TEMPLATES.get(category_key, CATEGORY_TEMPLATES["community"])
    
    allocations = []
    accumulated = 0
    total_budget_int = int(total_budget)
    
    for i, item in enumerate(template):
        if i == len(template) - 1:
            # Assign remainder to the final category (typically Contingency) to guarantee 100% exact match
            amount = max(0, total_budget_int - accumulated)
        else:
            amount = int(round(total_budget_int * (item["pct"] / 100.0)))
            accumulated += amount
            
        allocations.append({
            "category": item["category"],
            "estimated_amount": amount,
            "actual_amount": 0,
            "priority": item.get("priority", "essential"),
            "notes": item.get("notes", "")
        })
    return allocations

def calculate_budget_summary(total_budget: int, budget_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates total planned allocation, actual expenses, unallocated reserve,
    remaining budget, utilization percentage, and over-budget warnings.
    """
    total_budget = int(total_budget)
    total_estimated = sum(int(item.get("estimated_amount", 0)) for item in budget_items)
    total_actual = sum(int(item.get("actual_amount", 0)) for item in budget_items)
    
    unallocated_reserve = max(0, total_budget - total_estimated)
    remaining_balance = total_budget - total_actual
    
    utilization_pct = round((total_actual / total_budget * 100), 1) if total_budget > 0 else 0.0
    allocation_pct = round((total_estimated / total_budget * 100), 1) if total_budget > 0 else 0.0
    
    is_over_budget = total_actual > total_budget
    is_over_allocated = total_estimated > total_budget
    
    warnings = []
    if is_over_budget:
        warnings.append(f"Budget exceeded! Actual expenses exceed total budget by {total_actual - total_budget}.")
    elif total_actual > 0 and (total_budget - total_actual) < (total_budget * 0.05):
        warnings.append("Low budget reserve: Less than 5% of total budget remaining.")
        
    if is_over_allocated:
        warnings.append(f"Allocations exceed total budget by {total_estimated - total_budget}. Consider adjusting estimates.")
        
    # Check individual category overspends
    category_overspends = []
    for item in budget_items:
        est = int(item.get("estimated_amount", 0))
        act = int(item.get("actual_amount", 0))
        if act > est and est > 0:
            diff = act - est
            category_overspends.append(f"{item.get('category')}: exceeded estimate by {diff}")
            
    return {
        "total_budget": total_budget,
        "total_estimated": total_estimated,
        "total_actual": total_actual,
        "unallocated_reserve": unallocated_reserve,
        "remaining_balance": remaining_balance,
        "utilization_pct": min(100.0, utilization_pct),
        "actual_utilization_pct": utilization_pct,
        "allocation_pct": allocation_pct,
        "is_over_budget": is_over_budget,
        "is_over_allocated": is_over_allocated,
        "warnings": warnings,
        "category_overspends": category_overspends
    }
