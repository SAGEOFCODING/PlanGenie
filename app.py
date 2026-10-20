"""
Main Flask Application for the GenAI-Powered Event Planning Assistant.
Provides RESTful APIs for event creation, AI plan generation, budget management,
timeline task updates, vendor checklist tracking, and persistence.
"""
import logging
from flask import Flask, render_template, request, jsonify

from config import Config
from database import Database
from validation import validate_event_input
from services.ai_planner import generate_plan
from services.budget_engine import calculate_budget_summary
from services.timeline_engine import (
    evaluate_task_status,
    generate_day_of_run_of_show,
    generate_predictive_insights
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = Database(app.config["DATABASE_PATH"])

# --- Security Headers Middleware ---
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# --- Error Handlers (Safe, non-leaking JSON responses) ---
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"success": False, "error": "Bad request. Please check your input parameters."}), 400

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({"success": False, "error": "The requested resource was not found."}), 404

@app.errorhandler(413)
def handle_payload_too_large(e):
    return jsonify({"success": False, "error": "Uploaded payload is too large. Maximum allowed size is 1MB."}), 413

@app.errorhandler(500)
def handle_internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({"success": False, "error": "An unexpected server error occurred. Please try again."}), 500

# --- Frontend Entrypoint ---
@app.route("/")
def index():
    return render_template("index.html")

# --- App Config Endpoint ---
@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns application configuration, supported currencies, and AI status safely."""
    return jsonify({
        "success": True,
        "ai_available": Config.HAS_AI,
        "ai_provider": Config.AI_PROVIDER if Config.HAS_AI else "fallback_planner",
        "supported_currencies": Config.SUPPORTED_CURRENCIES,
        "categories": Config.VALID_CATEGORIES
    })

# --- Event Management Routes ---
@app.route("/api/events", methods=["GET"])
def list_events():
    """Returns a list of all saved events with budget totals."""
    try:
        events = db.list_events()
        enriched = []
        for ev in events:
            budget_items = db.get_budget_items(ev["id"])
            summary = calculate_budget_summary(ev["budget"], budget_items)
            tasks = db.get_tasks(ev["id"])
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t["is_completed"])
            
            enriched.append({
                "id": ev["id"],
                "name": ev["name"],
                "category": ev["category"],
                "event_date": ev["event_date"],
                "location": ev["location"],
                "guests": ev["guests"],
                "budget": ev["budget"],
                "currency": ev["currency"],
                "ai_source": ev["ai_source"],
                "total_actual": summary["total_actual"],
                "remaining_balance": summary["remaining_balance"],
                "utilization_pct": summary["utilization_pct"],
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "created_at": ev["created_at"]
            })
        return jsonify({"success": True, "events": enriched})
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve events."}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    """Validates inputs, executes AI / Fallback planning, and saves to database."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    is_valid, sanitized, errors = validate_event_input(data)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        # Generate complete intelligent plan
        plan = generate_plan(sanitized)
        sanitized["ai_source"] = plan.get("ai_source", "fallback_planner")
        sanitized["plan_summary"] = plan.get("planning_summary", "")

        # Persist event
        event_id = db.create_event(sanitized)

        # Persist budget items
        db.set_budget_items(event_id, plan.get("budget_allocation", []))

        # Persist tasks
        db.set_tasks(event_id, plan.get("timeline_tasks", []))

        # Persist vendor checklist
        db.set_vendor_items(event_id, plan.get("vendor_checklist", []))

        # Persist personalized ideas
        db.set_personalized_ideas(event_id, plan.get("personalized_ideas", []))

        # Return full saved plan
        full_plan = db.get_complete_event_plan(event_id)
        budget_summary = calculate_budget_summary(full_plan["event"]["budget"], full_plan["budget"])
        
        # Enrich tasks with overdue info
        enriched_tasks = [evaluate_task_status(t) for t in full_plan["tasks"]]
        full_plan["tasks"] = enriched_tasks
        full_plan["budget_summary"] = budget_summary
        full_plan["run_of_show"] = generate_day_of_run_of_show(full_plan["event"]["category"])
        full_plan["predictive_insights"] = generate_predictive_insights(full_plan["event"])

        return jsonify({
            "success": True,
            "event_id": event_id,
            "data": full_plan,
            "ai_source": sanitized["ai_source"]
        }), 201

    except Exception as e:
        logger.error(f"Error creating event: {e}", exc_info=True)
        return jsonify({"success": False, "error": "An error occurred while generating the plan."}), 500

@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """Retrieves full event details, budget calculations, tasks, and vendors."""
    try:
        full_plan = db.get_complete_event_plan(event_id)
        if not full_plan:
            return jsonify({"success": False, "error": "Event not found."}), 404

        budget_summary = calculate_budget_summary(full_plan["event"]["budget"], full_plan["budget"])
        enriched_tasks = [evaluate_task_status(t) for t in full_plan["tasks"]]
        full_plan["tasks"] = enriched_tasks
        full_plan["budget_summary"] = budget_summary
        full_plan["run_of_show"] = generate_day_of_run_of_show(full_plan["event"]["category"])
        full_plan["predictive_insights"] = generate_predictive_insights(full_plan["event"])

        return jsonify({"success": True, "data": full_plan})
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve event."}), 500

@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    """Updates essential and personalization fields of an existing event."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    existing = db.get_event(event_id)
    if not existing:
        return jsonify({"success": False, "error": "Event not found."}), 404

    data = request.get_json()
    is_valid, sanitized, errors = validate_event_input(data, is_update=True)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        sanitized["plan_summary"] = existing["plan_summary"]
        updated = db.update_event(event_id, sanitized)
        if not updated:
            return jsonify({"success": False, "error": "Update failed."}), 500

        full_plan = db.get_complete_event_plan(event_id)
        budget_summary = calculate_budget_summary(full_plan["event"]["budget"], full_plan["budget"])
        full_plan["tasks"] = [evaluate_task_status(t) for t in full_plan["tasks"]]
        full_plan["budget_summary"] = budget_summary
        full_plan["run_of_show"] = generate_day_of_run_of_show(full_plan["event"]["category"])
        full_plan["predictive_insights"] = generate_predictive_insights(full_plan["event"])

        return jsonify({"success": True, "data": full_plan})
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        return jsonify({"success": False, "error": "Failed to update event."}), 500

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Deletes an event and all associated records."""
    try:
        deleted = db.delete_event(event_id)
        if not deleted:
            return jsonify({"success": False, "error": "Event not found or already deleted."}), 404
        return jsonify({"success": True, "message": "Event deleted successfully."})
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        return jsonify({"success": False, "error": "Failed to delete event."}), 500

# --- Budget Routes ---
@app.route("/api/events/<int:event_id>/budget/<int:item_id>", methods=["PATCH"])
def update_budget_item(event_id, item_id):
    """Updates estimated amount, actual expense, or notes for a budget category."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    est = data.get("estimated_amount")
    act = data.get("actual_amount")
    notes = data.get("notes")

    # Validate numbers
    try:
        est_val = max(0, int(est)) if est is not None else None
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Estimated amount must be a positive number."}), 400

    try:
        act_val = max(0, int(act)) if act is not None else None
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Actual amount must be a positive number."}), 400

    try:
        updated = db.update_budget_item(item_id, est_val, act_val, notes)
        if not updated:
            return jsonify({"success": False, "error": "Budget item not found."}), 404

        event = db.get_event(event_id)
        budget_items = db.get_budget_items(event_id)
        summary = calculate_budget_summary(event["budget"], budget_items)

        return jsonify({
            "success": True,
            "budget_items": budget_items,
            "budget_summary": summary
        })
    except Exception as e:
        logger.error(f"Error updating budget item: {e}")
        return jsonify({"success": False, "error": "Failed to update budget item."}), 500

@app.route("/api/events/<int:event_id>/budget", methods=["POST"])
def add_budget_item(event_id):
    """Adds a custom budget item to an event."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    category = str(data.get("category", "")).strip()[:80]
    if not category:
        return jsonify({"success": False, "error": "Category name is required."}), 400

    try:
        est = max(0, int(data.get("estimated_amount", 0)))
        act = max(0, int(data.get("actual_amount", 0)))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Amounts must be valid positive numbers."}), 400

    priority = str(data.get("priority", "essential")).lower()
    notes = str(data.get("notes", "")).strip()[:300]

    try:
        new_id = db.add_budget_item(event_id, category, est, act, priority, notes)
        event = db.get_event(event_id)
        budget_items = db.get_budget_items(event_id)
        summary = calculate_budget_summary(event["budget"], budget_items)

        return jsonify({
            "success": True,
            "item_id": new_id,
            "budget_items": budget_items,
            "budget_summary": summary
        }), 201
    except Exception as e:
        logger.error(f"Error adding budget item: {e}")
        return jsonify({"success": False, "error": "Failed to add budget item."}), 500

@app.route("/api/events/<int:event_id>/budget/<int:item_id>", methods=["DELETE"])
def delete_budget_item(event_id, item_id):
    """Deletes a budget item."""
    try:
        deleted = db.delete_budget_item(item_id)
        if not deleted:
            return jsonify({"success": False, "error": "Budget item not found."}), 404

        event = db.get_event(event_id)
        budget_items = db.get_budget_items(event_id)
        summary = calculate_budget_summary(event["budget"], budget_items)

        return jsonify({
            "success": True,
            "budget_items": budget_items,
            "budget_summary": summary
        })
    except Exception as e:
        logger.error(f"Error deleting budget item: {e}")
        return jsonify({"success": False, "error": "Failed to delete budget item."}), 500

# --- Task Routes ---
@app.route("/api/events/<int:event_id>/tasks/<int:task_id>", methods=["PATCH"])
def update_task_status(event_id, task_id):
    """Toggles or updates task completion status."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    is_completed = bool(data.get("is_completed", False))

    try:
        updated = db.update_task_status(task_id, is_completed)
        if not updated:
            return jsonify({"success": False, "error": "Task not found."}), 404

        tasks = db.get_tasks(event_id)
        enriched = [evaluate_task_status(t) for t in tasks]
        return jsonify({"success": True, "tasks": enriched})
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({"success": False, "error": "Failed to update task status."}), 500

@app.route("/api/events/<int:event_id>/tasks", methods=["POST"])
def add_task(event_id):
    """Adds a custom task to an event."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    title = str(data.get("title", "")).strip()[:100]
    if not title:
        return jsonify({"success": False, "error": "Task title is required."}), 400

    due_date = str(data.get("due_date", "")).strip()
    if not due_date:
        return jsonify({"success": False, "error": "Due date is required."}), 400

    desc = str(data.get("description", "")).strip()[:300]
    priority = str(data.get("priority", "medium")).lower()
    category = str(data.get("category", "General")).strip()[:50]

    try:
        new_id = db.add_task(event_id, title, desc, due_date, priority, category)
        tasks = db.get_tasks(event_id)
        enriched = [evaluate_task_status(t) for t in tasks]
        return jsonify({"success": True, "task_id": new_id, "tasks": enriched}), 201
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return jsonify({"success": False, "error": "Failed to add task."}), 500

@app.route("/api/events/<int:event_id>/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(event_id, task_id):
    """Deletes a task."""
    try:
        deleted = db.delete_task(task_id)
        if not deleted:
            return jsonify({"success": False, "error": "Task not found."}), 404
        tasks = db.get_tasks(event_id)
        enriched = [evaluate_task_status(t) for t in tasks]
        return jsonify({"success": True, "tasks": enriched})
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({"success": False, "error": "Failed to delete task."}), 500

# --- Vendor Routes ---
@app.route("/api/events/<int:event_id>/vendors/<int:vendor_id>", methods=["PATCH"])
def update_vendor(event_id, vendor_id):
    """Updates vendor status, notes, or estimated quote."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    status = data.get("status")
    notes = data.get("notes")
    estimated_cost = data.get("estimated_cost")

    try:
        updated = db.update_vendor_item(vendor_id, status, notes, estimated_cost)
        if not updated:
            return jsonify({"success": False, "error": "Vendor item not found."}), 404

        vendors = db.get_vendor_items(event_id)
        return jsonify({"success": True, "vendors": vendors})
    except Exception as e:
        logger.error(f"Error updating vendor: {e}")
        return jsonify({"success": False, "error": "Failed to update vendor item."}), 500

@app.route("/api/events/<int:event_id>/vendors", methods=["POST"])
def add_vendor(event_id):
    """Adds a custom vendor checklist item."""
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required."}), 400

    data = request.get_json()
    title = str(data.get("title", "")).strip()[:100]
    category = str(data.get("category", "General")).strip()[:80]
    if not title:
        return jsonify({"success": False, "error": "Vendor title/role is required."}), 400

    desc = str(data.get("description", "")).strip()[:400]
    status = str(data.get("status", "not_contacted")).strip().lower()
    notes = str(data.get("notes", "")).strip()[:400]
    try:
        cost = max(0, int(data.get("estimated_cost", 0)))
    except (ValueError, TypeError):
        cost = 0

    try:
        new_id = db.add_vendor_item(event_id, category, title, desc, status, notes, cost)
        vendors = db.get_vendor_items(event_id)
        return jsonify({"success": True, "vendor_id": new_id, "vendors": vendors}), 201
    except Exception as e:
        logger.error(f"Error adding vendor: {e}")
        return jsonify({"success": False, "error": "Failed to add vendor item."}), 500

@app.route("/api/events/<int:event_id>/vendors/<int:vendor_id>", methods=["DELETE"])
def delete_vendor(event_id, vendor_id):
    """Deletes a vendor item."""
    try:
        deleted = db.delete_vendor_item(vendor_id)
        if not deleted:
            return jsonify({"success": False, "error": "Vendor item not found."}), 404
        vendors = db.get_vendor_items(event_id)
        return jsonify({"success": True, "vendors": vendors})
    except Exception as e:
        logger.error(f"Error deleting vendor: {e}")
        return jsonify({"success": False, "error": "Failed to delete vendor item."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
