import os
import re
from datetime import datetime
from flask import Flask, request, jsonify
import gspread
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Connect to Google Sheets
gc = gspread.service_account(filename=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"))
sheet = gc.open(os.getenv("GOOGLE_SHEET_NAME")).sheet1


# ---------- VALIDATION ----------
def validate_input(name, email, message):
    # Validate required fields and email format
    errors = []

    if not name or name.strip() == "":
        errors.append("name missing")

    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("invalid email")

    if not message or message.strip() == "":
        errors.append("message missing")

    status = "Valid" if len(errors) == 0 else "Invalid"
    return status, ", ".join(errors)


# ---------- AI CLASSIFICATION ----------
def classify_ticket(message):
    # Try AI classification first. If AI fails, use rule-based fallback.
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
Classify this customer support message.

Message: {message}

Return ONLY in this format:
category: one of [billing, bug, feature_request, general]
priority: one of [low, medium, high]
"""

        response = model.generate_content(prompt)
        text = response.text.lower()

        category = "general"
        priority = "low"

        if "billing" in text:
            category = "billing"
            priority = "high"
        elif "bug" in text:
            category = "bug"
            priority = "high"
        elif "feature" in text:
            category = "feature_request"
            priority = "medium"

        return category, priority

    except Exception as e:
        print("AI failed, using fallback:", e)

        message_lower = message.lower()

        if "charged" in message_lower or "payment" in message_lower:
            return "billing", "high"
        elif "error" in message_lower or "bug" in message_lower:
            return "bug", "high"
        elif "feature" in message_lower:
            return "feature_request", "medium"
        else:
            return "general", "low"


# ---------- ROUTING ----------
def route_ticket(category):
    # Route ticket based on its category
    if category == "billing":
        return "finance_email"
    elif category == "bug":
        return "dev_slack"
    else:
        return "shared_email"


# ---------- SAVE ----------
def save_to_sheets(data):
    # Save ticket record to Google Sheets
    sheet.append_row(data)


# ---------- ENDPOINT ----------
@app.route("/ticket", methods=["POST"])
def receive_ticket():
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    validation_status, validation_errors = validate_input(name, email, message)

    if validation_status == "Valid":
        category, priority = classify_ticket(message)
        routed_to = route_ticket(category)
    else:
        category, priority = "none", "none"
        routed_to = "none"

    record = [
        datetime.now().isoformat(),
        name,
        email,
        message,
        validation_status,
        validation_errors,
        category,
        priority,
        routed_to,
        "received"
    ]

    save_to_sheets(record)

    return jsonify({
        "status": "success",
        "validation": validation_status,
        "category": category,
        "priority": priority,
        "routed_to": routed_to
    })


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
