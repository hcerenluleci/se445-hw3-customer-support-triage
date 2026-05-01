import os
import re
from datetime import datetime
from flask import Flask, request, jsonify
import gspread
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
load_dotenv()

app = Flask(__name__)

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Google Sheets setup
gc = gspread.service_account(filename=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"))
sheet = gc.open(os.getenv("GOOGLE_SHEET_NAME")).sheet1

# ---------- VALIDATION ----------
def validate_input(name, email, message):
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
    if category == "billing":
        return "finance_email"
    elif category == "bug":
        return "dev_slack"
    else:
        return "shared_email"


# ---------- SAVE ----------
def save_to_sheets(data):
    sheet.append_row(data)


# ---------- ENDPOINT ----------
@app.route("/ticket", methods=["POST"])
def receive_ticket():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # Validation
    validation_status, validation_errors = validate_input(name, email, message)

    # AI only if valid
    if validation_status == "Valid":
        category, priority = classify_ticket(message)
    else:
        category, priority = "none", "none"

    routed_to = route_ticket(category) if validation_status == "Valid" else "none"

    # Save everything
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