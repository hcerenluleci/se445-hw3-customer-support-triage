# SE445 - HW3: Intelligent Customer Support Triage

This project implements Homework 3 for Customer Support Triage.

---

## What it does

- Receives support tickets via HTTP POST
- Validates input data (name, email, message)
- Classifies tickets into category and priority
- Routes tickets based on classification
- Stores all requests (valid and invalid) in Google Sheets

---

## Required HW3 flow

HTTP POST → Validation → AI Classification → Routing → Delivery (Slack/Email) → Google Sheets

---

## Antigravity Workflow Structure

The workflow was designed and implemented in Antigravity using prompt-based development.

```text
Webhook Trigger (/ticket)
        ↓
Input Parser
        ↓
Validation Step
- checks missing name
- checks invalid email
- checks empty message
        ↓
Classification Step
- category: billing, bug, feature_request, general
- priority: low, medium, high
        ↓
Routing Step
- billing → finance_email
- bug → dev_slack
- general / feature_request → shared_email
        ↓
Google Sheets Connector
- saves original data
- saves validation status
- saves category, priority, routed_to
```

---

## Step-by-Step Development

### STEP 1 — Webhook Setup

Using Antigravity, I generated a Flask application with a POST endpoint:

```text
POST /ticket
```

This endpoint receives JSON input with:

- name
- email
- message

---

### STEP 2 — Validation

The system checks:

- Missing fields
- Invalid email format

If input is invalid:

- It is not deleted
- It is stored in Google Sheets
- It is marked as Invalid
- Errors are logged

---

### STEP 3 — Classification

The system assigns:

Category:
- billing
- bug
- feature_request
- general

Priority:
- low
- medium
- high

The AI classification was designed using a structured prompt to ensure consistent outputs for category and priority labels.

The system attempts AI-based classification using the Gemini API.
If the AI service fails (e.g., API limitations), a fallback rule-based classifier ensures continuous operation.

---

### STEP 4 — Routing

Tickets are routed as follows:

- billing → finance_email
- bug → dev_slack
- general / feature_request → shared_email

In the final implementation:
- Bug tickets are sent to Slack using a webhook
- Billing tickets are sent via email (SMTP)
- General and feature requests are sent to a shared inbox email

---

### STEP 5 — Data Storage

Stored fields:

- timestamp
- name
- email
- message
- validation_status
- validation_errors
- category
- priority
- routed_to
- delivery_status

---

## Antigravity Prompts Used

Prompt 1:
Create a Flask-based customer support triage application for SE445 HW3.
The app should have a POST endpoint at /ticket.
It should accept JSON input with exactly three fields: name, email, and message.

Prompt 2:
Add validation logic. Check missing fields and validate email format.
Invalid requests should not be deleted but stored with validation errors.

Prompt 3:
Classify customer support messages into one of the following categories: billing, bug, feature_request, general.
Also assign a priority level: low, medium, high.
Return both category and priority in a structured format.

Prompt 4:
Add routing logic based on classification results.
Billing tickets → finance_email (via SMTP email)
Bug tickets → dev_slack (via Slack webhook)
General and feature_request → shared_email (via email)

Prompt 5:
Store all requests in Google Sheets with full metadata.

Prompt 6:
Handle AI failures by adding fallback classification logic.

---

## Project Files

- app.py → Main Flask application
- requirements.txt → Dependencies
- .env.example → Environment variables
- README.md → Documentation

---

## Setup Instructions

1) Create Google Sheet:
support_tickets

Columns:
timestamp | name | email | message | validation_status | validation_errors | category | priority | routed_to | delivery_status

---

2) Google Service Account

- Enable Google Sheets API
- Enable Google Drive API
- Create Service Account
- Download JSON
- Rename to: service_account.json
- Place in project folder
- Share sheet with service account email

---

3) Install Dependencies

pip install -r requirements.txt

---

4) Create .env file

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email

FINANCE_EMAIL=finance_email_address
SHARED_INBOX_EMAIL=shared_email_address
SLACK_WEBHOOK_BUG=your_slack_webhook_url

---

5) Run

python app.py

---

## Test

Valid request:

Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"name":"Ceren","email":"ceren@gmail.com","message":"I was charged twice"}'

Invalid request:

Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"name":"","email":"cerenmail.com","message":""}'

---

## Notes

- AI classification is supported with a fallback rule-based mechanism to ensure continuous system operation due to API limitations.
- The system remains fully functional even if AI fails.
- Sensitive files (.env, service_account.json) are not included in the repository.

---

## Conclusion

This system successfully implements:

- Validation
- Classification
- Routing
- Google Sheets storage
- Handling of both valid and invalid requests

It fulfills HW3 requirements.
