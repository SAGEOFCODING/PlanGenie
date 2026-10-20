"""
Application configuration for the GenAI-Powered Event Planning Assistant.
Loads environment variables safely without exposing sensitive data.
"""
import os

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "events.db")
    
    # AI Provider configuration
    # Can be 'gemini' or 'openai'
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini").lower().strip()
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
    
    # Check if a live AI provider key is configured
    HAS_GEMINI = bool(GEMINI_API_KEY)
    HAS_OPENAI = bool(OPENAI_API_KEY)
    HAS_AI = (AI_PROVIDER == "gemini" and HAS_GEMINI) or (AI_PROVIDER == "openai" and HAS_OPENAI) or HAS_GEMINI or HAS_OPENAI

    # Request size limits (prevent huge payloads)
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB maximum payload

    # Validation constraints
    MAX_NAME_LENGTH = 100
    MAX_LOCATION_LENGTH = 120
    MAX_THEME_LENGTH = 150
    MAX_NOTES_LENGTH = 1000
    MIN_GUESTS = 1
    MAX_GUESTS = 100000
    MIN_BUDGET = 100
    MAX_BUDGET = 500000000  # 50 Crores INR max

    # Supported event categories
    VALID_CATEGORIES = ("wedding", "birthday", "community")
    
    # Supported currencies with symbols
    SUPPORTED_CURRENCIES = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "CAD": "CA$",
        "AUD": "AU$",
        "AED": "AED",
        "SGD": "S$"
    }
