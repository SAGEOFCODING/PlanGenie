"""
AI Planner Service: Integrates with GenAI provider APIs (Google Gemini / OpenAI)
to generate tailored, structured event plans. Includes strict schema validation,
sanitization, timeout handling, and seamless, transparent fallback execution.
"""
import json
import logging
import re
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple

from config import Config
from services.fallback_planner import generate_fallback_plan
from services.budget_engine import generate_default_budget_allocation
from services.timeline_engine import generate_default_timeline

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are an elite, highly practical GenAI Event Planning Architect.
Your task is to generate a comprehensive, realistic, and mathematically consistent event plan.
You must respond ONLY with a single valid JSON object, without any surrounding markdown code fences or conversational text.

The JSON object must have this exact structure:
{
  "planning_summary": "Concise executive summary explaining how the plan addresses the user's specific priorities, location, and guest count.",
  "budget_allocation": [
    {
      "category": "Category Name (e.g. Catering, Venue, Decor, Photography, Sound, Contingency)",
      "estimated_amount": 12345,
      "priority": "essential",
      "notes": "Practical explanation of items covered"
    }
  ],
  "timeline_tasks": [
    {
      "title": "Actionable task title",
      "description": "Specific details of what to execute",
      "due_date": "YYYY-MM-DD",
      "priority": "high",
      "category": "Category"
    }
  ],
  "vendor_checklist": [
    {
      "category": "Vendor Category",
      "title": "Vendor Role (e.g. Master Caterer, Sound Engineer)",
      "description": "Key responsibilities and selection criteria",
      "status": "not_contacted",
      "notes": "Questions to ask or terms to compare"
    }
  ],
  "personalized_ideas": [
    {
      "category": "decor | activity | food | sustainability | accessibility | budget_saving",
      "title": "Creative concept title",
      "description": "Detailed implementation details",
      "rationale": "Clear explanation of why this fits this specific event and budget"
    }
  ],
  "risks_and_contingencies": [
    {
      "risk": "Description of risk",
      "mitigation": "Actionable contingency plan"
    }
  ],
  "assumptions_and_suggestions": [
    "Practical assumption or proactive suggestion"
  ]
}

CRITICAL RULES:
1. The sum of estimated_amount across all items in budget_allocation MUST NOT exceed the total budget provided.
2. Every task due_date MUST be formatted as YYYY-MM-DD, between today and the event date.
3. Tailor every recommendation specifically to the category (wedding, birthday, community event), guest count, location, and user priorities.
4. Distinguish clearly between essential expenses and optional upgrades.
5. All price values are estimates, not verified vendor quotes.
"""

def build_user_prompt(event_data: Dict[str, Any]) -> str:
    """Builds a rich, contextual prompt from user inputs."""
    today_str = date.today().strftime("%Y-%m-%d")
    return f"""Please create a complete event plan based on these verified specifications:
- Event Name: {event_data.get('name', 'Special Event')}
- Event Category: {event_data.get('category', 'wedding').title()}
- Event Date: {event_data.get('event_date')} (Current Planning Date: {today_str})
- Location / City: {event_data.get('location', 'Unspecified')}
- Expected Guests: {event_data.get('guests', 50)}
- Total Budget: {event_data.get('currency', 'INR')} {event_data.get('budget', 50000):,}
- Preferred Theme / Style: {event_data.get('theme') or 'Not specified'}
- Main Priorities: {event_data.get('priorities') or 'Smooth guest experience and balanced budget'}
- Venue Setting Preference: {event_data.get('venue_type', 'indoor').title()}
- Food & Dietary Requirements: {event_data.get('dietary') or 'Standard catering'}
- Accessibility Requirements: {event_data.get('accessibility') or 'Standard accessibility'}
- Additional Instructions: {event_data.get('notes') or 'None'}

Remember: Sum of budget items must equal or be less than {event_data.get('budget')}. Output pure JSON only."""

def clean_json_response(raw_text: str) -> str:
    """Strips markdown code fences, leading/trailing whitespace, and extracts JSON."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Match the outermost {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def validate_and_sanitize_ai_plan(parsed_data: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates model output to enforce data integrity, numeric limits,
    date ranges, and required fields.
    """
    total_budget = int(event_data.get("budget", 50000))
    event_date_str = event_data.get("event_date", date.today().strftime("%Y-%m-%d"))
    category = event_data.get("category", "community").lower().strip()
    today = date.today()
    
    try:
        event_dt = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        event_dt = today + timedelta(days=30)
        event_date_str = event_dt.strftime("%Y-%m-%d")

    # 1. Validate planning_summary
    summary = str(parsed_data.get("planning_summary", "")).strip()
    if not summary or len(summary) < 20:
        summary = f"Comprehensive planning blueprint for {event_data.get('name')} in {event_data.get('location')}."

    # 2. Validate budget_allocation
    raw_budget = parsed_data.get("budget_allocation")
    validated_budget = []
    if isinstance(raw_budget, list) and len(raw_budget) >= 3:
        current_sum = 0
        for item in raw_budget:
            if not isinstance(item, dict):
                continue
            cat_name = str(item.get("category", "Miscellaneous")).strip()[:80]
            try:
                est_val = max(0, int(round(float(item.get("estimated_amount", 0)))))
            except (ValueError, TypeError):
                est_val = 0
            priority = str(item.get("priority", "essential")).lower()
            if priority not in ("essential", "optional"):
                priority = "essential"
            notes = str(item.get("notes", "")).strip()[:300]
            
            validated_budget.append({
                "category": cat_name,
                "estimated_amount": est_val,
                "actual_amount": 0,
                "priority": priority,
                "notes": notes
            })
            current_sum += est_val

        # If model hallucinated and sum exceeds total budget, rescale proportionally
        if current_sum > total_budget and current_sum > 0:
            scale_factor = total_budget / float(current_sum)
            rescaled_sum = 0
            for i, b_item in enumerate(validated_budget):
                if i == len(validated_budget) - 1:
                    b_item["estimated_amount"] = max(0, total_budget - rescaled_sum)
                else:
                    new_val = int(round(b_item["estimated_amount"] * scale_factor))
                    b_item["estimated_amount"] = new_val
                    rescaled_sum += new_val
    else:
        # Fallback to balanced template budget
        validated_budget = generate_default_budget_allocation(category, total_budget)

    # 3. Validate timeline_tasks
    raw_tasks = parsed_data.get("timeline_tasks")
    validated_tasks = []
    if isinstance(raw_tasks, list) and len(raw_tasks) >= 3:
        for t in raw_tasks:
            if not isinstance(t, dict):
                continue
            title = str(t.get("title", "")).strip()[:100]
            if not title:
                continue
            desc = str(t.get("description", "")).strip()[:300]
            priority = str(t.get("priority", "medium")).lower()
            if priority not in ("high", "medium", "low"):
                priority = "medium"
            t_cat = str(t.get("category", "Planning")).strip()[:50]
            
            # Validate due_date
            due_str = str(t.get("due_date", "")).strip()
            task_date = None
            try:
                d = datetime.strptime(due_str, "%Y-%m-%d").date()
                if d < today:
                    task_date = today
                elif d > event_dt:
                    task_date = event_dt
                else:
                    task_date = d
            except (ValueError, TypeError):
                # Assign default date halfway
                task_date = today + timedelta(days=max(0, (event_dt - today).days // 2))
                
            validated_tasks.append({
                "title": title,
                "description": desc,
                "due_date": task_date.strftime("%Y-%m-%d"),
                "priority": priority,
                "is_completed": 0,
                "category": t_cat
            })
        validated_tasks.sort(key=lambda x: x["due_date"])
    else:
        validated_tasks = generate_default_timeline(category, event_date_str)

    # 4. Validate vendor_checklist
    raw_vendors = parsed_data.get("vendor_checklist")
    validated_vendors = []
    if isinstance(raw_vendors, list) and len(raw_vendors) >= 3:
        for v in raw_vendors:
            if not isinstance(v, dict):
                continue
            v_title = str(v.get("title", "")).strip()[:100]
            if not v_title:
                continue
            v_cat = str(v.get("category", "General Logistics")).strip()[:80]
            v_desc = str(v.get("description", "")).strip()[:400]
            v_notes = str(v.get("notes", "")).strip()[:400]
            validated_vendors.append({
                "category": v_cat,
                "title": v_title,
                "description": v_desc,
                "status": "not_contacted",
                "notes": v_notes
            })
    else:
        # Use fallback vendors
        fallback_plan = generate_fallback_plan(event_data)
        validated_vendors = fallback_plan["vendor_checklist"]

    # 5. Validate personalized_ideas
    raw_ideas = parsed_data.get("personalized_ideas")
    validated_ideas = []
    if isinstance(raw_ideas, list) and len(raw_ideas) >= 2:
        for idea in raw_ideas:
            if not isinstance(idea, dict):
                continue
            i_title = str(idea.get("title", "")).strip()[:120]
            if not i_title:
                continue
            i_cat = str(idea.get("category", "idea")).lower().strip()[:40]
            i_desc = str(idea.get("description", "")).strip()[:500]
            i_rationale = str(idea.get("rationale", "")).strip()[:500]
            validated_ideas.append({
                "category": i_cat,
                "title": i_title,
                "description": i_desc,
                "rationale": i_rationale
            })
    else:
        fallback_plan = generate_fallback_plan(event_data)
        validated_ideas = fallback_plan["personalized_ideas"]

    return {
        "event_overview": {
            "name": event_data.get("name"),
            "category": category,
            "event_date": event_date_str,
            "location": event_data.get("location"),
            "guests": int(event_data.get("guests", 1)),
            "budget": total_budget,
            "currency": event_data.get("currency", "INR")
        },
        "planning_summary": summary,
        "budget_allocation": validated_budget,
        "timeline_tasks": validated_tasks,
        "vendor_checklist": validated_vendors,
        "personalized_ideas": validated_ideas,
        "ai_source": "live_genai"
    }

def call_gemini_api(prompt: str, api_key: str) -> str:
    """Invokes Google Gemini REST API with bounded timeout."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4,
            "maxOutputTokens": 4096
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=12)
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("No candidates returned from Gemini API")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts or "text" not in parts[0]:
        raise ValueError("Empty content text in Gemini candidate response")
    return parts[0]["text"]

def call_openai_api(prompt: str, api_key: str) -> str:
    """Invokes OpenAI Chat Completions API with JSON mode and bounded timeout."""
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
        "max_tokens": 4096
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(url, json=payload, headers=headers, timeout=12)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("No choices returned from OpenAI API")
    return choices[0].get("message", {}).get("content", "")

def generate_plan(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for generating an event plan.
    Attempts live GenAI if configured, verifies and sanitizes the output,
    and falls back cleanly and transparently to the rule-based planner on any failure.
    """
    user_prompt = build_user_prompt(event_data)
    
    # 1. Attempt Google Gemini if configured
    if Config.HAS_GEMINI and (Config.AI_PROVIDER == "gemini" or not Config.HAS_OPENAI):
        try:
            logger.info("Calling live Google Gemini API...")
            raw_text = call_gemini_api(user_prompt, Config.GEMINI_API_KEY)
            cleaned = clean_json_response(raw_text)
            parsed = json.loads(cleaned)
            return validate_and_sanitize_ai_plan(parsed, event_data)
        except Exception as e:
            logger.warning(f"Gemini API invocation failed ({e}). Reverting to fallback planner.")

    # 2. Attempt OpenAI if configured
    elif Config.HAS_OPENAI:
        try:
            logger.info("Calling live OpenAI API...")
            raw_text = call_openai_api(user_prompt, Config.OPENAI_API_KEY)
            cleaned = clean_json_response(raw_text)
            parsed = json.loads(cleaned)
            return validate_and_sanitize_ai_plan(parsed, event_data)
        except Exception as e:
            logger.warning(f"OpenAI API invocation failed ({e}). Reverting to fallback planner.")

    # 3. Transparent Fallback Planner
    logger.info("Using intelligent offline Fallback Planner.")
    return generate_fallback_plan(event_data)
