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

HTTP POST → Validation → Classification → Routing → Google Sheets

---

## Antigravity Workflow Structure

The workflow was designed using prompt-based development in Antigravity.

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
- saves all request data and metadata

---

## Step-by-Step Development

### STEP 1 — Webhook Setup

POST /ticket

Accepts JSON input:
- name
- email
- message

---

### STEP 2 — Validation

The system checks:
- Missing fields
- Invalid email format

Invalid requests:
- Are not deleted
- Are stored in Google Sheets
- Are marked as "Invalid"
- Include validation errors

---

### STEP 3 — Classification

Categories:
- billing
- bug
- feature_request
- general

Priorities:
- low
- medium
- high

AI classification is performed using the Gemini API.

If AI fails (e.g., API limitations), a rule-based fallback classifier is used.

---

### STEP 4 — Routing

- billing → finance_email
- bug → dev_slack
- feature_request / general → shared_email

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
- status

---

## Antigravity Prompts Used

Prompt 1:
Create a Flask-based customer support triage application.
Add a POST endpoint at /ticket.
Accept JSON input: name, email, message.
Return structured JSON response.

Prompt 2:
Add validation logic.
Check missing fields and email format.
Invalid inputs should not be deleted.
Store them with validation_status and validation_errors.

Prompt 3:
Classify messages into billing, bug, feature_request, general.
Assign priority: low, medium, high.
Return category and priority.

Prompt 4:
Route tickets based on category:
billing → finance_email
bug → dev_slack
others → shared_email

Prompt 5:
Store all requests in Google Sheets with full metadata.

Prompt 6:
If AI fails, use rule-based classification.
Ensure system continues to function.

---

## Project Files

- app.py → Main application
- requirements.txt → Dependencies
- .env.example → Environment variables
- README.md → Documentation

---

## Setup Instructions

1) Create Google Sheet:
support_tickets

Columns:
timestamp | name | email | message | validation_status | validation_errors | category | priority | routed_to | status

---

2) Google Service Account

- Enable Google Sheets API
- Enable Google Drive API
- Create Service Account
- Download JSON
- Rename to service_account.json
- Place in project folder
- Share sheet with service account email

---

3) Install Dependencies

pip install -r requirements.txt

---

4) Create .env file

GOOGLE_SHEET_NAME=support_tickets
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GEMINI_API_KEY=your_api_key_here

---

5) Run

python app.py

---

## Test

Valid request:
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" -Method POST -Headers @{ "Content-Type"="application/json" } -Body '{"name":"Ceren","email":"ceren@gmail.com","message":"I was charged twice"}'

Invalid request:
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" -Method POST -Headers @{ "Content-Type"="application/json" } -Body '{"name":"","email":"cerenmail.com","message":""}'

---

## Notes

- AI classification is supported with fallback logic
- System works even if AI fails
- Sensitive files are not included

---

## Conclusion

This system implements:
- Validation
- Classification
- Routing
- Google Sheets storage
- Handling of valid and invalid data

It fulfills HW3 requirements.
