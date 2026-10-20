# PlanGenie — GenAI-Powered Event Planning Assistant

**A lightweight, secure, and production-grade intelligent assistant for organizing Weddings, Birthday Parties, and Community Gatherings.**

---

## 1. Chosen Challenge Vertical

**Chosen Vertical: Event Planning**

Organizing events is notoriously chaotic—requiring coordination across multi-tier budgets, time-sensitive schedules, vendor contracts, and diverse guest expectations. **PlanGenie** directly addresses these challenges by transforming raw event parameters into structured, actionable event plans specifically optimized for:
- **Weddings:** Multi-day milestone coordination, banquet and mandap venue booking, bridal styling, photography/cinematography, and guest hospitality.
- **Birthday Parties:** Focal theme decor, personalized birthday cakes, age-appropriate entertainment/games, and return gift logistics.
- **Community Events:** Civic & municipal permits, crowd logistics, stage & AV sound infrastructure, first aid readiness, volunteer coordination, and eco-friendly waste management.

---

## 2. Problem Statement & Solution

### The Practical Problem
Event planners and hosts face severe friction:
1. **Unrealistic Budgeting:** Ad-hoc expense tracking leads to rapid budget exhaustion, unaccounted emergency costs, and floating-point financial errors.
2. **Generic AI Advice:** Standard chatbots generate fluffy, repetitive advice that completely ignores guest headcounts, local constraints, and real calendar countdowns.
3. **Fragile Cloud Dependency:** Many web apps fail entirely if an API key is missing, invalid, or rate-limited.
4. **Data Disarray:** Critical tasks and vendor negotiations are scattered across text messages, notebooks, and disconnected spreadsheets.

### PlanGenie's Solution
PlanGenie delivers an integrated, deterministic-backed planning engine that pairs **GenAI creativity** (via Google Gemini or OpenAI) with **mathematically rigorous fallback planners** and an **interactive single-page management dashboard**:
- **Proportional Financial Allocation:** Budget distributions guarantee that planned expenses never silently exceed the available budget ceiling.
- **Dynamic Calendar Scaling:** Task schedules scale intelligently whether an event is 10 days or 9 months away—preventing past deadlines.
- **Persistent Local Management:** SQLite database persistence tracks budget items, actual expenditures, task completion, and vendor quotes across browser refreshes.
- **100% Offline Demonstrability:** Operates out-of-the-box using the deterministic rule-based planning engine without requiring any external API key.

---

## 3. Features

- **Event Creation & Tailored Personalization:** Collects essential fields (name, category, date, city, guest count, budget, currency) and deep personalization parameters (theme, venue type, dietary requirements, accessibility needs, notes).
- **Multi-Currency Support:** Defaults to Indian Rupees (`INR - ₹`) while providing seamless selector support for `USD ($)`, `EUR (€)`, `GBP (£)`, `CAD`, `AUD`, `AED`, and `SGD`.
- **Intelligent Budget Planner:** Automatically allocates expenses into event-tailored categories (e.g. Venue, Catering, Media, Decor, Contingency Reserve). Users can adjust estimates, input real expenditures, track remaining reserves, and view over-budget warnings.
- **Dynamic Chronological Timeline:** Derives actionable task deadlines from the event date. Features overdue detection, priority tags, and filterable completion toggles.
- **Vendor & Logistics Checklist:** Event-specific vendor directories (e.g. Master Caterer, AV Sound Engineer, Civic Clearance) with status tracking (`Not Contacted`, `In Discussion`, `Quote Received`, `Hired`, `Completed`) and comparison notes.
- **Personalized Event Ideas:** Tailored recommendations for decorations, guest engagement, dietary safety, and sustainability—each backed by an explicit explanation of *why* it fits the user's specific event.
- **Event Lifecycle Persistence:** Saved Events drawer allows users to switch between multiple events, review overall progress, print/export clean summary PDFs, or delete events with an accessible confirmation dialog.
- **Honest AI & Fallback Transparency:** Visually identifies whether the active blueprint was formulated by **Live GenAI** or the **Intelligent Rule-Based Engine**.

---

## 4. Approach and Decision Logic

```
   User Event Input (Category, Budget, Date, Guests, Preferences)
                             │
                             ▼
               Backend Validation & Sanitization
              (Date bounds, Budget caps, XSS escaping)
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [API Key Configured?]             [No API Key / Offline]
            │                                 │
    (Yes, Google Gemini)                      │
            │                                 │
    Live GenAI Execution                      │
   - Strict JSON schema                       │
   - Context-rich prompt                      │
   - Bounded 12s timeout                      │
            │                                 │
   Validate & Sanitize AI Output              │
   - Budget sum <= total budget               │
   - Dates clamped to [today, event_date]     │
            │                                 │
            ├────► [On JSON Error / Fail] ────┤
            ▼                                 ▼
   Live GenAI Plan                Deterministic Fallback Planner
   (Source: live_genai)           - Category templates (sum == 100%)
            │                     - Proportional interval scaling
            │                     - Localized vendor baselines
            │                     (Source: fallback_planner)
            └────────────────┬────────────────┘
                             │
                             ▼
         SQLite Transactional Persistence (Parameterized SQL)
                             │
                             ▼
         Interactive SPA Dashboard (Safe DOM Rendering)
```

1. **Budget Allocation Logic:** Integer-based percentage distribution templates per category ensure zero floating-point accumulation drift. Remainder amounts are automatically deposited into the Emergency Contingency Reserve.
2. **Timeline Calculation Logic:** Relative percentage offsets calculate realistic target dates based on `total_days = max(1, event_date - today)`. For short-notice events (e.g., 5 days), intervals compress proportionally so tasks are never placed in the past or after the event.
3. **Security-First Architecture:** Input lengths and types are constrained on both client and server. Database queries use parameterized SQL statements. The frontend uses `textContent` and strict DOM element creation to eliminate DOM-based XSS.

---

## 5. Technical Architecture

### Tech Stack
- **Backend:** Python 3.10+ with **Flask** (lightweight WSGI microframework)
- **Frontend:** Semantic HTML5, Vanilla Modern CSS (glassmorphism accents, responsive mobile/desktop layouts), Vanilla JavaScript (zero build step, no NPM build bloat)
- **Persistence:** **SQLite** with parameterized queries, index optimizations, and cascade foreign key constraints
- **Testing:** Python's built-in `unittest` framework (zero external test dependencies required)
- **AI Service:** Isolated provider adapter supporting **Google Gemini REST API** and **OpenAI Chat Completions** with built-in schema sanitization and rule-based fallback

### Project Directory Layout
```
challange-5/
├── app.py                     # Flask web server and RESTful API endpoints
├── config.py                  # Environment variable configuration and constants
├── database.py                # SQLite schema management and parameterized CRUD operations
├── validation.py              # Input validation and sanitization rules
├── requirements.txt           # Minimal Python dependencies (Flask, requests)
├── .env.example               # Template environment configuration (no secrets)
├── .gitignore                 # Excludes .env, *.db, __pycache__, and test caches
├── README.md                  # Comprehensive project documentation
├── services/
│   ├── __init__.py
│   ├── ai_planner.py          # GenAI integration, schema validation, and fallback orchestrator
│   ├── fallback_planner.py    # Deterministic event planning logic for weddings, birthdays, community
│   ├── budget_engine.py       # Integer money math, category distribution, spend warnings
│   └── timeline_engine.py     # Relative deadline calculation, short-notice scaling, overdue checker
├── templates/
│   └── index.html             # Accessible, semantic single-page application interface
├── static/
│   ├── css/
│   │   └── style.css          # Cohesive dark productivity theme and print styling
│   └── js/
│       └── app.js             # State management, safe DOM rendering, inline editing, modals
└── tests/
    ├── __init__.py
    ├── test_validation.py     # Input constraints and edge case validation tests
    ├── test_budget.py         # Integer math, exact sum, and budget alert tests
    ├── test_timeline.py       # Scheduling intervals, short-notice scaling, overdue tests
    ├── test_database.py       # SQLite CRUD and cascade deletion tests
    ├── test_ai_service.py     # AI schema validation, budget rescaling, fallback tests
    └── test_routes.py         # Flask REST API endpoint integration tests
```

---

## 6. How the Solution Works

1. **Step 1: Event Specification**
   The user opens the application and selects the event category (Wedding, Birthday, or Community Event). The user enters essential details (name, target date, city, guest headcount, budget ceiling, currency) and optional personalization preferences (theme, dietary restrictions, accessibility requirements).
2. **Step 2: Intelligent Plan Synthesis**
   Upon clicking *"Generate Intelligent Event Plan"*, the backend validates all inputs. If an API key is available, the GenAI service generates a structured JSON blueprint. If no API key is configured or the network request times out, the deterministic fallback engine generates an event-tailored plan instantly.
3. **Step 3: Financial Management & Tracking**
   In the Budget tab, the user reviews estimated amounts across essential and optional categories. As actual invoices or quotations arrive, the user inputs real expenditures directly in the table. The application recalculates actual spend, remaining balance, and utilization percentages immediately.
4. **Step 4: Milestone Execution**
   In the Timeline tab, tasks appear sorted chronologically. Users can mark tasks complete, review overdue items, and add custom milestone checkpoints.
5. **Step 5: Vendor Negotiations**
   In the Vendor Checklist tab, users manage vendors through different procurement stages (`Not Contacted` → `In Discussion` → `Quote Received` → `Hired` → `Completed`) and store comparison notes.
6. **Step 6: Plan Retention & Export**
   Plans are automatically persisted in the local SQLite database. Users can switch between events via the *Saved Events* modal or export/print the complete plan as a clean PDF document.

---

## 7. Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Standard `pip` package manager
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Installation Steps

1. **Clone or Navigate to the Repository:**
   ```bash
   cd challange-5
   ```

2. **(Optional) Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Configure Environment Variables (Optional):**
   ```bash
   cp .env.example .env
   ```
   *Note: Providing an API key in `.env` is entirely optional. If omitted, PlanGenie automatically operates in offline mode using its built-in rule-based planning engine.*

5. **Run the Automated Test Suite:**
   ```bash
   python -m unittest discover tests
   ```

6. **Start the Application:**
   ```bash
   python app.py
   ```

7. **Access the Application:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 8. Environment Configuration

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Environment mode (`production` or `development`) | `production` | No |
| `FLASK_SECRET_KEY` | Session signing secret key | Dev default | No (recommended for production) |
| `PORT` | Local HTTP server port | `5000` | No |
| `AI_PROVIDER` | Preferred GenAI provider (`gemini` or `openai`) | `gemini` | No |
| `GEMINI_API_KEY` | Google Gemini API key (from Google AI Studio) | None | No (activates live AI if set) |
| `OPENAI_API_KEY` | OpenAI API key | None | No (alternative provider) |
| `DATABASE_PATH` | Local SQLite database file location | `events.db` | No |

### Offline Fallback Guarantee
If neither `GEMINI_API_KEY` nor `OPENAI_API_KEY` is provided, the application runs without errors or degradation in UI capabilities. The assistant clearly labels all outputs as generated by the **Intelligent Fallback Engine**.

---

## 9. Security & Privacy Safeguards

- **Zero Credential Exposure:** API keys are read solely from backend environment variables and are never rendered in HTML, JavaScript, logs, or API responses.
- **Strict Parameterized SQL:** All database interactions use parameter substitution (`?`), eliminating SQL injection vulnerabilities.
- **Safe DOM Rendering:** Untrusted user input and AI-generated text are inserted using native DOM APIs (`textContent`, `replaceChildren`, `appendChild`) rather than raw `innerHTML`, mitigating Cross-Site Scripting (XSS).
- **Security Headers:** The server automatically attaches `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Referrer-Policy: strict-origin-when-cross-origin`.
- **Payload & Input Limits:** Server-side request body size is capped at 1 MB. String lengths for names, locations, and descriptions are strictly bounded.
- **Public Deployment Notice:** This prototype is designed as a single-user local productivity tool. In a public multi-tenant deployment, user authentication (OAuth / JWT), role-based access control, and encrypted database storage must be added.

---

## 10. Assumptions & Limitations

- **Estimated Prices:** All cost allocations generated by the assistant are planning estimates based on historical category proportions, not real-time contracted quotes.
- **Vendor Directory:** Vendor entries serve as logistics checklists and selection criteria templates; PlanGenie does not execute live external vendor bookings or payments.
- **Single-User Local Scope:** The application persists data to a local SQLite database for the local user.

---

## 11. Automated Test Results

The test suite covers all essential functionality without requiring an external internet connection or live API credentials.

**Command Executed:**
```bash
python -m unittest discover tests
```

**Results:**
```
Ran 41 tests in 0.840s

OK
```

### Test Coverage Breakdown:
1. `tests/test_validation.py` (9 tests): Validates wedding, birthday, and community event inputs; rejects missing fields, past dates, non-positive budgets, zero guest counts, and oversize inputs.
2. `tests/test_budget.py` (6 tests): Validates integer arithmetic, guarantees allocation sums equal total budgets across categories, checks remaining balances, and verifies over-budget warnings.
3. `tests/test_timeline.py` (6 tests): Tests relative deadline calculations, short-notice event interval scaling, overdue task identification, Day-of Run of Show generation, and predictive bottleneck synthesis.
4. `tests/test_database.py` (5 tests): Tests SQLite CRUD operations, cascade deletion of related child records, task completion toggling, and budget expense updates.
5. `tests/test_ai_service.py` (6 tests): Tests JSON code-fence cleaning, structured schema validation, proportional budget rescaling when model outputs exceed ceilings, and fallback execution.
6. `tests/test_routes.py` (9 tests): Tests HTTP status codes, JSON payload responses, REST endpoints for events, budget tracking, task toggling, vendor updates, and run of show payloads.

---

## 12. GitHub Repository Compliance

- **Branch Count:** Exactly 1 branch (`main`).
- **Repository Size:** Strictly below 10 MB (~250 KB total source code, lightweight custom CSS, zero heavy binary assets).
- **Clean Repository:** Sensitive files (`.env`, `*.db`, `__pycache__`, virtual environments) are ignored by `.gitignore` and never committed.
- **To Connect to a Public GitHub Repository:**
  ```bash
  git remote add origin https://github.com/<your-username>/<your-repo-name>.git
  git push -u origin main
  ```
