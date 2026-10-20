"""
Fallback Planner Service: High-quality, deterministic event planning engine.
Generates comprehensive, event-tailored budgets, timelines, vendor checklists,
and personalized ideas without requiring third-party API connectivity.
"""
from datetime import datetime, date
from typing import Dict, Any, List
from services.budget_engine import generate_default_budget_allocation
from services.timeline_engine import generate_default_timeline

FALLBACK_VENDORS = {
    "wedding": [
        {
            "category": "Venue & Facility",
            "title": "Banquet Hall / Resort Venue",
            "description": "Inspect guest capacity, mandap space, bridal dressing rooms, parking valet, and power generator backup.",
            "status": "not_contacted",
            "notes": "Verify curfew timings and in-house sound restrictions."
        },
        {
            "category": "Catering & Hospitality",
            "title": "Master Wedding Caterer",
            "description": "Finalize multi-cuisine menu, live food counters, dietary options, service captains, and dishware.",
            "status": "not_contacted",
            "notes": "Request food tasting session and per-plate cost breakdown."
        },
        {
            "category": "Media & Memory",
            "title": "Wedding Photographer & Cinematographer",
            "description": "Review portfolio for candid ceremony shots, cinematic video teaser, and family portrait setup.",
            "status": "not_contacted",
            "notes": "Confirm drone clearance and delivery timeline for digital album."
        },
        {
            "category": "Decor & Ambiance",
            "title": "Floral & Stage Designer",
            "description": "Coordinate entrance floral arch, stage backdrop, ambient uplighting, and table centerpieces.",
            "status": "not_contacted",
            "notes": "Align colors with couple's theme and attire."
        },
        {
            "category": "Styling & Beauty",
            "title": "Bridal Makeup Artist & Hair Stylist",
            "description": "Schedule makeup trial, groom touch-up, and day-of styling timetable for bridal party.",
            "status": "not_contacted",
            "notes": "Verify on-location travel availability."
        },
        {
            "category": "Entertainment",
            "title": "DJ, Sound System & Emcee",
            "description": "Book sound system, cordless microphones for announcements, and curate ceremony entrance music.",
            "status": "not_contacted",
            "notes": "Provide customized playlist and 'do-not-play' list."
        },
        {
            "category": "Logistics & Transport",
            "title": "Guest Shuttle & Fleet Service",
            "description": "Arrange local transfers for out-of-town guests from transit hubs to hotel/venue.",
            "status": "not_contacted",
            "notes": "Confirm emergency backup vehicle."
        }
    ],
    "birthday": [
        {
            "category": "Venue",
            "title": "Party Hall / Cafe / Backyard Setup",
            "description": "Secure party zone with adequate room for games, seating for adults, and setup access 2 hours prior.",
            "status": "not_contacted",
            "notes": "Check music volume rules and outside food permissions."
        },
        {
            "category": "Bakery",
            "title": "Custom Theme Cake Bakery",
            "description": "Order centerpiece birthday cake matching selected theme, plus allergy-friendly cupcakes.",
            "status": "not_contacted",
            "notes": "Confirm temperature-controlled delivery time 1 hour before party start."
        },
        {
            "category": "Decor",
            "title": "Balloon Artist & Decor Stylist",
            "description": "Design organic balloon arch, personalized banner backdrop, milestone board, and photo booth.",
            "status": "not_contacted",
            "notes": "Opt for biodegradable latex balloons where feasible."
        },
        {
            "category": "Entertainment",
            "title": "Game Host / Performer / Magician",
            "description": "Engage party entertainer suitable for guest age group with interactive games, music, and prizes.",
            "status": "not_contacted",
            "notes": "Review 45-minute interactive routine schedule."
        },
        {
            "category": "Catering",
            "title": "Party Food & Beverage Vendor",
            "description": "Arrange finger foods, sliders, mocktails/juices, and main meal catering suited for all guests.",
            "status": "not_contacted",
            "notes": "Ensure clearly labeled nut-free and vegetarian options."
        },
        {
            "category": "Photography",
            "title": "Party Event Photographer",
            "description": "Capture candid guest moments, birthday cake cutting, and group family photos.",
            "status": "not_contacted",
            "notes": "Book 2-3 hour coverage package."
        }
    ],
    "community": [
        {
            "category": "Administration",
            "title": "Municipal Civic & Police Clearance",
            "description": "File paperwork for public assembly, sound amplifier usage, and civic health clearances.",
            "status": "not_contacted",
            "notes": "Secure permits at least 3 weeks before event date."
        },
        {
            "category": "Infrastructure",
            "title": "Stage, Truss & AV Equipment Rental",
            "description": "Procure weatherproof stage platform, wireless PA sound system, projector screen, and standby generator.",
            "status": "not_contacted",
            "notes": "Ensure on-site sound technician is present throughout the event."
        },
        {
            "category": "Sanitation",
            "title": "Waste Management & Eco Sanitation Partner",
            "description": "Deploy color-coded dry/wet recycling stations, portable restrooms, and post-event cleanup crew.",
            "status": "not_contacted",
            "notes": "Target zero-landfill community gathering standards."
        },
        {
            "category": "Hospitality",
            "title": "Community Beverage & Hydration Station",
            "description": "Set up water refilling dispensers, reusable tumblers, and volunteer refreshment counters.",
            "status": "not_contacted",
            "notes": "Avoid single-use plastic water bottles."
        },
        {
            "category": "Safety",
            "title": "First Aid & Medical Response Team",
            "description": "Establish clearly marked first-aid booth staffed with trained volunteers and automated external defibrillator/basic supplies.",
            "status": "not_contacted",
            "notes": "Coordinate emergency vehicle access lane."
        },
        {
            "category": "Signage & Print",
            "title": "Community Signage & Badge Printing",
            "description": "Produce large directional boards, accessibility indicators, volunteer lanyards, and schedule posters.",
            "status": "not_contacted",
            "notes": "Include high-contrast lettering and Braille/universal icons where possible."
        }
    ]
}

def generate_personalized_ideas(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates intelligent personalized event ideas tailored to the event category,
    budget tier, guest count, dietary preferences, and accessibility requirements.
    """
    category = event_data.get("category", "community").lower().strip()
    guests = int(event_data.get("guests", 50))
    budget = int(event_data.get("budget", 50000))
    currency = event_data.get("currency", "INR")
    location = event_data.get("location", "City")
    venue_type = event_data.get("venue_type", "indoor").lower()
    theme = event_data.get("theme", "")
    priorities = event_data.get("priorities", "")
    dietary = event_data.get("dietary", "")
    accessibility = event_data.get("accessibility", "")
    
    ideas = []
    
    # 1. Budget-conscious Decoration Idea
    if category == "wedding":
        ideas.append({
            "category": "decor",
            "title": "Warm Architectural Up-Lighting & Brass Accents",
            "description": f"Focus lighting investments on floor uplights and traditional brass lamps/lanterns rather than exorbitant fresh floral walls. Create dramatic entrance pathways with clustered fairy lights and sustainable potted foliage.",
            "rationale": f"Delivers a regal, premium ambiance for your {guests}-guest celebration in {location} while saving up to 25% on perishable floral costs."
        })
    elif category == "birthday":
        ideas.append({
            "category": "decor",
            "title": f"Focal Photo-Op Backdrop ({theme or 'Vibrant Milestone Theme'})",
            "description": "Concentrate 70% of balloon and floral budget into a single striking photo backdrop with a customized marquee name cutout, leaving guest tables clean and minimalist with small themed centerpieces.",
            "rationale": f"Creates memorable social photos for the birthday VIP without overcrowding the {venue_type} celebration area."
        })
    else:
        ideas.append({
            "category": "decor",
            "title": "Community-Crafted Eco Banners & Local Art Wall",
            "description": "Display canvas banners painted by local art groups or schools alongside potted native plants rented from local nurseries.",
            "rationale": "Fosters community ownership, minimizes synthetic single-use flex plastic, and creates high visual impact on an efficient budget."
        })
        
    # 2. Guest Engagement / Activity Idea
    if category == "wedding":
        ideas.append({
            "category": "activity",
            "title": "Digital Guestbook & Live Polaroids",
            "description": "Equip a dedicated welcome nook with 2 instant cameras and a customized scrapbook where guests write personal marriage blessings alongside candid polaroids.",
            "rationale": "High sentimental value, deeply engaging for guests of all ages, and provides an instant keepsake for the couple."
        })
    elif category == "birthday":
        ideas.append({
            "category": "activity",
            "title": "Time-Capsule Message Jar & Interactive Trivia",
            "description": "Host a fast-paced 15-minute trivia quiz about the birthday person with small novelty prizes, followed by guests dropping prediction cards into a milestone time capsule.",
            "rationale": f"Keeps all {guests} guests energized and prevents downtime between arrival and food service."
        })
    else:
        ideas.append({
            "category": "activity",
            "title": "Interactive Feedback Chalkboard & Volunteer Recognition",
            "description": "Erect a giant chalkboard or magnetic idea wall inviting attendees to answer 'What makes our community vibrant?' with a 10-minute public shoutout honoring frontline volunteers.",
            "rationale": "Inspires participatory civic spirit and builds lasting community momentum."
        })

    # 3. Dietary & Culinary Personalization
    dietary_text = dietary if dietary else "diverse regional palate"
    ideas.append({
        "category": "food",
        "title": "Interactive Live Tasting Stations & Allergy Clarity",
        "description": f"Feature dedicated live counters addressing {dietary_text}. Display elegant tent cards clearly marking gluten-free, vegan, nut-free, and regional specialties.",
        "rationale": f"Prevents queue bottlenecks for {guests} guests and guarantees that every attendee dines safely and enthusiastically."
    })

    # 4. Sustainability & Green Footprint
    ideas.append({
        "category": "sustainability",
        "title": "Zero Single-Use Plastic & Food Rescue Partnership",
        "description": "Partner with a local food redistribution NGO (such as Robin Hood Army / Feeding India) to collect unserved banquet dishes at the conclusion of the event, paired with compostable areca palm leaf plates.",
        "rationale": "Reduces event waste by over 80% and channels surplus celebration resources into local community welfare."
    })

    # 5. Accessibility Enhancements
    access_text = accessibility if accessibility else "universal accessibility and senior comfort"
    ideas.append({
        "category": "accessibility",
        "title": "Seamless Navigation Ramps & Reserved Quiet Seating",
        "description": f"Ensure step-free zero-threshold entry ramps, wide 4-foot aisles between tables, high-contrast directional signage, and a designated quiet comfort zone accommodating {access_text}.",
        "rationale": "Ensures seniors, parents with strollers, and differently-abled guests participate with complete dignity and comfort."
    })

    # 6. Budget-Saving Strategic Recommendation
    ideas.append({
        "category": "budget_saving",
        "title": "Off-Peak Time Scheduling & Digital First Communications",
        "description": f"Replace luxury printed cards with interactive digital mobile invites featuring Google Maps pins and automated RSVP tracking. Reserve 5% ({int(budget * 0.05)} {currency}) as an untouched emergency buffer.",
        "rationale": f"Saves printing and postal logistics expenses while keeping your {currency} {budget:,} financial plan resilient against sudden price increases."
    })
    
    return ideas

def generate_fallback_plan(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a complete, structured, and realistic event plan without live AI.
    """
    category = event_data.get("category", "community").lower().strip()
    total_budget = int(event_data.get("budget", 50000))
    event_date_str = event_data.get("event_date", date.today().strftime("%Y-%m-%d"))
    name = event_data.get("name", "Special Event")
    location = event_data.get("location", "City")
    guests = int(event_data.get("guests", 50))
    currency = event_data.get("currency", "INR")
    
    # Generate balanced budget items
    budget_items = generate_default_budget_allocation(category, total_budget)
    
    # Generate timeline tasks
    tasks = generate_default_timeline(category, event_date_str)
    
    # Generate vendor checklist
    vendors = FALLBACK_VENDORS.get(category, FALLBACK_VENDORS["community"])
    # Clone vendors to avoid mutating module constant
    vendor_items = [dict(v) for v in vendors]
    
    # Generate personalized ideas
    ideas = generate_personalized_ideas(event_data)
    
    summary = (
        f"Customized planning roadmap for {name} ({category.title()}) in {location} "
        f"for {guests} guests with a total budget of {currency} {total_budget:,}. "
        f"Formulated by the deterministic Planning Engine with balanced allocations, "
        f"realistic countdown milestones, and safety safeguards."
    )
    
    return {
        "event_overview": {
            "name": name,
            "category": category,
            "event_date": event_date_str,
            "location": location,
            "guests": guests,
            "budget": total_budget,
            "currency": currency
        },
        "planning_summary": summary,
        "budget_allocation": budget_items,
        "timeline_tasks": tasks,
        "vendor_checklist": vendor_items,
        "personalized_ideas": ideas,
        "ai_source": "fallback_planner"
    }
