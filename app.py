import os
import re
from datetime import datetime
from flask import Flask, request, jsonify
import gspread
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import smtplib
from email.mime.text import MIMEText

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


# ---------- REAL ROUTING INTEGRATIONS ----------
def send_email(to_email, subject, body):
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL")

        if not all([smtp_server, smtp_username, smtp_password, from_email, to_email]):
            print("Missing SMTP configuration or destination email.")
            return False

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def send_slack(webhook_url, message):
    try:
        if not webhook_url:
            print("Missing Slack webhook URL.")
            return False
        response = requests.post(webhook_url, json={"text": message})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Slack message: {e}")
        return False


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
        
        delivery_success = False
        if category == "billing":
            finance_email = os.getenv("FINANCE_EMAIL")
            subject = f"New Billing Ticket - {priority.upper()} Priority"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            delivery_success = send_email(finance_email, subject, body)
        elif category == "bug":
            slack_webhook = os.getenv("SLACK_WEBHOOK_BUG")
            slack_message = f"*New Bug Ticket ({priority.upper()} Priority)*\n*From:* {name} ({email})\n*Message:* {message}"
            delivery_success = send_slack(slack_webhook, slack_message)
        elif category in ["general", "feature_request"]:
            shared_email = os.getenv("SHARED_INBOX_EMAIL")
            subject = f"New {category.replace('_', ' ').title()} Ticket - {priority.upper()} Priority"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            delivery_success = send_email(shared_email, subject, body)

        delivery_status = "success" if delivery_success else "failed"
    else:
        category, priority = "none", "none"
        routed_to = "none"
        delivery_status = "none"

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
        delivery_status
    ]

    save_to_sheets(record)

    return jsonify({
        "status": "success",
        "validation": validation_status,
        "category": category,
        "priority": priority,
        "routed_to": routed_to,
        "delivery_status": delivery_status
    })


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
