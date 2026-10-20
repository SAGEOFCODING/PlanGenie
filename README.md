# PlanGenie — GenAI-Powered Event Planning Assistant

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Test Suite](https://img.shields.io/badge/tests-41%2F41%20passing-brightgreen.svg)](tests/)
[![Design System](https://img.shields.io/badge/design-Terra%20Organic-4a7c59.svg)](#6-terra-organic-design-system)
[![License](https://img.shields.io/badge/license-MIT-amber.svg)](LICENSE)
[![Repository Size](https://img.shields.io/badge/repo%20size-%3C%201%20MB-success.svg)](#12-github-repository-compliance)

> **A production-grade, secure, and offline-resilient event planning platform for Weddings, Milestone Birthdays, and Community Gatherings.** Grounded in the **Terra ("Rooted Warmth")** organic design philosophy.

---

## 1. Challenge Vertical & Mission

**Chosen Vertical:** **Event Planning**

Organizing events is notoriously chaotic—requiring coordination across multi-tier budgets, time-sensitive schedules, vendor contracts, and diverse guest expectations. **PlanGenie** directly addresses these challenges by transforming raw event constraints into structured, actionable event plans specifically tailored for:

1. **Weddings:**
   - Multi-stage milestone coordination (venue reservation, mandap/atrium florals, sommelier tastings, attire fittings).
   - Proportional budget distribution across venue, catering, decor, photography, entertainment, and contingency reserves.
   - Live Day-of Run of Show micro-schedules synchronized to solar dusk timing.
2. **Birthday Parties:**
   - Theme decor orchestration, custom artisan birthday cakes, age-appropriate entertainment/games, and return gift logistics.
   - Budget constraints scaled to guest headcount and party duration.
3. **Community Gatherings:**
   - Civic & municipal permits, crowd logistics, stage & acoustic sound infrastructure, first aid readiness, volunteer coordination, and eco-friendly waste management.
   - Public safety checklists and volunteer shift sequencing.

---

## 2. Problem Statement & Solution

### The Core Problem
Event hosts and planners regularly suffer from four major pain points:
1. **Unrealistic Budgeting & Float Drift:** Ad-hoc spreadsheet tracking causes unforeseen expenses, unmonitored overspends, and floating-point math rounding errors.
2. **Generic, Context-Blind AI Advice:** Standard chatbots generate fluffy, repetitive advice that completely ignores guest headcounts, local constraints, and real calendar countdowns.
3. **Fragile Cloud Dependencies:** Many applications fail entirely when third-party AI APIs hit rate limits, network timeouts, or invalid keys.
4. **Scattered Coordination:** Critical milestones, quotes, and dietary profiles end up lost across disparate chat threads, emails, and notebooks.

### PlanGenie's Architectural Solution
- **Integer Financial Engine:** Exact integer currency math guarantees zero floating-point accumulation drift. Remainder funds are automatically transferred into an Emergency Contingency Reserve.
- **Dynamic Chronological Sequencing:** Milestone intervals calculate backwards from the event date proportionally to `max(1, event_date - today)`. Short-notice events automatically compress so deadlines are never scheduled in the past.
- **100% Offline-First Resilience:** Functions seamlessly out-of-the-box using the built-in deterministic planning engine without requiring any external API key. When API keys are configured, it augments the plan with Live GenAI (Google Gemini or OpenAI).
- **Persistent Local Management:** SQLite database tracks budget adjustments, actual expenditure invoices, milestone completion states, and vendor negotiation notes.

---

## 3. System Architecture & Workflow

```
   User Event Input (Category, Budget, Date, Guests, Personalization)
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
         Interactive SPA Dashboard (Terra Organic Design)
```

---

## 4. Key Features

- **Event Specification & Tailored Cues:** Captures essential constraints (name, category, date, city, guest headcount, budget, currency) and deep personalization parameters (theme, venue type, dietary requirements, accessibility needs, notes).
- **Multi-Currency Support:** Seamless selector support for `INR (₹)`, `USD ($)`, `EUR (€)`, `GBP (£)`, `CAD (CA$)`, `AUD (AU$)`, `AED`, and `SGD (S$)`.
- **Integer Budget Engine:** Proportional percentage distribution templates allocate funds across categories with zero floating-point drift. Supports inline editing of actual expenses and dynamic over-budget alerts.
- **Phase-by-Phase Interactive Milestone Track:**
  - **Phase 01: Foundation & Venue** (Contracts, venue locks, deposit escrow, insurance binders).
  - **Phase 02: Design, Catering & Sensory** (Interactive task cards, sommelier tastings, floral mockups, and AI cost-optimization swaps).
  - **Phase 03: Logistics, AV & Transport** (Shuttle routes, acoustic soundchecks, and technical rehearsals).
- **Day-of Run of Show:** Micro-schedule synchronized to dusk lighting (e.g. 17:42 Sunset lock) with key ceremonial event flags and microclimate telemetry.
- **Predictive Bottleneck Advisor:** Automatically monitors milestone dependencies and identifies scheduling conflicts before they cause vendor delays.
- **Vendor Deck:** Logistics directory with status tracking (`Not Contacted` → `In Discussion` → `Quote Received` → `Hired` → `Completed`) and negotiation criteria.
- **AI Ideation Studio:** Tailored recommendations for decor, cuisine, entertainment, and sustainability with explicit rationales detailing *why* each idea fits the event.
- **Saved Plans Modal Drawer:** Manage, open, or delete multiple event blueprints with accessible confirmation dialogues.
- **SEO, Machine & Agent Readability:** Native endpoints for `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/favicon.svg`, Open Graph cards, and Schema.org JSON-LD structured data.

---

## 5. REST API Reference

| Endpoint | Method | Description | Request Payload | Response Status |
| :--- | :---: | :--- | :--- | :---: |
| `/` | `GET` | Main single-page application interface | None | `200 OK` |
| `/api/config` | `GET` | Returns AI status, provider, and supported currencies | None | `200 OK` |
| `/api/events` | `GET` | Lists all saved event blueprints | None | `200 OK` |
| `/api/events` | `POST` | Creates an event & synthesizes full blueprint | `{ name, category, budget, ... }` | `201 Created` |
| `/api/events/<id>` | `GET` | Retrieves full event data, budget, timeline, vendors | None | `200 OK` / `404 Not Found` |
| `/api/events/<id>` | `DELETE` | Deletes an event blueprint (cascading delete) | None | `200 OK` / `404 Not Found` |
| `/api/events/<id>/budget/<item_id>` | `PATCH` | Updates actual expenditure for an expense category | `{ actual_amount: 45000 }` | `200 OK` / `404 Not Found` |
| `/api/events/<id>/budget` | `POST` | Adds a new custom budget category | `{ category, estimated_amount, ... }`| `201 Created` |
| `/api/events/<id>/budget/<item_id>` | `DELETE` | Deletes a budget category | None | `200 OK` / `404 Not Found` |
| `/api/events/<id>/tasks/<task_id>` | `PATCH` | Toggles milestone task completion status | `{ is_completed: true }` | `200 OK` / `404 Not Found` |
| `/api/events/<id>/tasks` | `POST` | Adds a custom milestone task | `{ title, due_date, priority, ... }` | `201 Created` |
| `/api/events/<id>/tasks/<task_id>` | `DELETE` | Deletes a milestone task | None | `200 OK` / `404 Not Found` |
| `/api/events/<id>/vendors/<vendor_id>` | `PATCH` | Updates vendor procurement status and notes | `{ status: "hired" }` | `200 OK` / `404 Not Found` |
| `/api/events/<id>/vendors` | `POST` | Adds a vendor entry | `{ title, category, status, ... }` | `201 Created` |
| `/api/events/<id>/vendors/<vendor_id>` | `DELETE` | Removes a vendor entry | None | `200 OK` / `404 Not Found` |
| `/sitemap.xml` | `GET` | Valid XML sitemap for search crawlers | None | `200 OK` |
| `/robots.txt` | `GET` | Crawler permissions and sitemap pointer | None | `200 OK` |
| `/llms.txt` | `GET` | Markdown documentation for LLM agents | None | `200 OK` |
| `/favicon.ico` | `GET` | Custom SVG favicon | None | `200 OK` |

---

## 6. Terra Organic Design System

The application interface follows the **Terra ("Rooted Warmth")** design philosophy:
- **Calm, Grounded Palette:**
  - **Primary (`#4a7c59`):** Forest green for actions, navigation, and active states.
  - **Background (`#faf6f0`):** Warm organic cream (never sterile white).
  - **Tertiary (`#705c30`):** Warm amber for priority highlights, alerts, and key moments.
  - **Warm Neutrals:** Yellow/green undertone creams (`#f5f1ea`, `#f0ece4`, `#eae6de`) layered for tonal separation.
- **Typography:**
  - **Headlines:** **Literata** — warm, editorial serif with character.
  - **Body & Labels:** **Nunito Sans** — approachable, rounded letterforms with generous line-height (`1.65`).
- **Elevation:**
  - Very soft organic shadows (`0 4px 20px rgba(46, 50, 48, 0.06)`). Tonal layering preferred over harsh borders.
- **Button & Card Rules:**
  - Buttons use large 12px rounded corners (`rounded-[12px]`) instead of pill shapes.
- **Terra Earthy Dark Mode ("Rooted Warmth"):**
  - **Calm Forest Charcoal (`#181c19`):** Deep, organic background with espresso undertones (never sterile pitch black).
  - **Elevated Surfaces (`#212622` / `#2a312b`):** Soft earthy containers for cards, inputs, and modals.
  - **High-Contrast Botanical Accents:** Gentle sage green (`#6cb281`) and warm amber (`#ddc48d`).
  - **Zero-FOUC Persistence:** Inline `<head>` script synchronizes instantly with `localStorage` and system `prefers-color-scheme`.
  - **Accessible Toggle Button:** `#btnThemeToggle` in the top header switches modes with live toast telemetry.

---

## 7. Project Structure

```
challange-5/
├── app.py                     # Flask web server, REST API & machine endpoints
├── config.py                  # Environment variable configuration and defaults
├── database.py                # SQLite schema management & parameterized CRUD operations
├── validation.py              # Dual-layer input validation and sanitization
├── requirements.txt           # Minimal, pinned Python dependencies
├── LICENSE                    # MIT open-source license
├── README.md                  # Comprehensive project documentation
├── .env.example               # Template environment configuration (no secrets)
├── .gitignore                 # Excludes .env, *.db, __pycache__, and venv
├── services/
│   ├── __init__.py
│   ├── ai_planner.py          # GenAI integration, schema validation, and fallback orchestrator
│   ├── fallback_planner.py    # Deterministic event planning logic for weddings, birthdays, community
│   ├── budget_engine.py       # Integer money math, category distribution, spend warnings
│   └── timeline_engine.py     # Relative deadline calculation, short-notice scaling, overdue checker
├── templates/
│   ├── index.html             # Single-page application interface (Terra Design & Dark Mode)
│   └── 404.html               # Custom 404 error page with breadcrumbs and Terra styling
├── static/
│   ├── favicon.svg            # Terra botanical organic SVG emblem
│   ├── img/
│   │   └── og-image.svg       # Social share Open Graph image (1200x630)
│   └── js/
│       └── app.js             # Pure Vanilla JS state management & DOM-safe rendering
└── tests/
    ├── __init__.py
    ├── test_validation.py     # Input constraints and edge case tests
    ├── test_budget.py         # Integer math, exact sum, and budget alert tests
    ├── test_timeline.py       # Scheduling intervals, short-notice scaling, overdue tests
    ├── test_database.py       # SQLite CRUD and cascade deletion tests
    ├── test_ai_service.py     # AI schema validation, budget rescaling, fallback tests
    └── test_routes.py         # Flask REST API endpoint integration tests
```

---

## 8. Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Standard `pip` package manager
- Any modern web browser (Chrome, Edge, Firefox, Safari)

### Quick Start

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SAGEOFCODING/PlanGenie.git
   cd PlanGenie
   ```

2. **(Optional) Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   *Note: Providing an API key in `.env` is completely optional. If omitted, PlanGenie automatically operates in offline mode using its built-in rule-based planning engine.*

5. **Run the Automated Test Suite:**
   ```bash
   python -m unittest discover tests
   ```

6. **Start the Application Server:**
   ```bash
   python app.py
   ```

7. **Open in Browser:**
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 9. Environment Configuration

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :---: |
| `FLASK_ENV` | Environment mode (`production` or `development`) | `production` | No |
| `FLASK_SECRET_KEY` | Session signing secret key | Dev default | No (recommended for production) |
| `PORT` | Local HTTP server port | `5000` | No |
| `AI_PROVIDER` | Preferred GenAI provider (`gemini` or `openai`) | `gemini` | No |
| `GEMINI_API_KEY` | Google Gemini API key (from Google AI Studio) | None | No (activates live AI if set) |
| `OPENAI_API_KEY` | OpenAI API key | None | No (alternative provider) |
| `DATABASE_PATH` | Local SQLite database file location | `events.db` | No |

---

## 10. Security & Privacy Safeguards

- **Zero Credential Leaks:** API keys reside solely in server environment variables and are never rendered in HTML, JavaScript, logs, or API responses. Cryptographically strong default secret key generated via `secrets.token_hex(32)`.
- **Parameterized SQL & Zero Injection:** All SQLite database interactions use parameter substitution (`?`), eliminating SQL injection risks.
- **IDOR (Insecure Direct Object Reference) Protection:** Subresource mutations (tasks, budget items, vendors) strictly verify that the target item belongs to the requested `event_id` in SQL (`WHERE id = ? AND event_id = ?`), preventing unauthorized cross-event access or deletion.
- **In-Memory Rate Limiting & DoS Mitigation:** Sliding-window rate limiter throttles expensive AI plan generation (20 req/min) and general API routes (120 req/min), defending against resource exhaustion without external infrastructure dependencies.
- **DOM-Based XSS Prevention:** User input and AI-generated text are rendered exclusively using native DOM properties (`textContent`, `replaceChildren`, `appendChild`) rather than raw `innerHTML`. Server-side templates use automatic Jinja2 escaping.
- **Comprehensive Defense-in-Depth HTTP Headers:**
  - `Content-Security-Policy`: Restricts scripts, styles, fonts, connections, and blocks clickjacking (`frame-ancestors 'none'`).
  - `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing.
  - `X-Frame-Options: DENY`: Prevents UI redressing / clickjacking.
  - `X-XSS-Protection: 1; mode=block`: Legacy browser protection.
  - `Referrer-Policy: strict-origin-when-cross-origin`: Minimizes referrer leakage.
  - `Permissions-Policy`: Disables unused browser capabilities (`camera`, `microphone`, `geolocation`, `payment`).
  - `Cross-Origin-Opener-Policy: same-origin`: Isolates the browsing context.
- **Input & Payload Limits:** Bounded string lengths for all form fields; max payload size capped at 1 MB with clean 413 responses.
- **Non-Leaking Error Handlers:** 400, 404, 405, 413, 429, and 500 error responses return structured, clean JSON without exposing internal stack traces.

---

## 11. Automated Test Suite & Coverage

The automated test suite runs offline without requiring third-party credentials or an internet connection.

```bash
python -m unittest discover tests
```

**Results:**
```
Ran 52 tests in 1.811s

OK
```

### Coverage Breakdown:
1. `tests/test_validation.py` (9 tests): Validates wedding, birthday, and community event inputs; rejects missing fields, past dates, non-positive budgets, zero guest counts, and oversize inputs.
2. `tests/test_budget.py` (6 tests): Validates integer arithmetic, guarantees allocation sums equal total budgets across categories, checks remaining balances, and verifies over-budget warnings.
3. `tests/test_timeline.py` (6 tests): Tests relative deadline calculations, short-notice event interval scaling, overdue task identification, Day-of Run of Show generation, and predictive bottleneck synthesis.
4. `tests/test_database.py` (6 tests): Tests SQLite CRUD operations, cascade deletion of related child records, task completion toggling, budget expense updates, and single-query summary aggregations.
5. `tests/test_ai_service.py` (6 tests): Tests JSON code-fence cleaning, structured schema validation, proportional budget rescaling when model outputs exceed ceilings, and fallback execution.
6. `tests/test_routes.py` (9 tests): Tests HTTP status codes, JSON payload responses, REST endpoints for events, budget tracking, task toggling, vendor updates, and run of show payloads.
7. `tests/test_security.py` (10 tests): Verifies HTTP security headers (CSP, COOP, Permissions-Policy, HSTS-ready), non-leaking error responses, IDOR protection across tasks/budget/vendors, invalid date rejections, non-JSON handling, and sliding-window rate limiting.

---

## 12. GitHub Repository Compliance

- **Public Repository URL:** [https://github.com/SAGEOFCODING/PlanGenie](https://github.com/SAGEOFCODING/PlanGenie)
- **Branch Count:** Exactly 1 branch (`main`).
- **Repository Size:** Strictly below 10 MB (~0.32 MB total repository size, zero heavy binary assets).
- **Clean Repository:** Sensitive files (`.env`, `*.db`, `__pycache__`, virtual environments) are ignored by `.gitignore` and never committed.
- **Repository Visibility:** Public.

---

## 13. License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full details.
