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

**Category:**

- billing
- bug
- feature_request
- general

**Priority:**

- low
- medium
- high

The AI classification was designed using a structured prompt to ensure consistent outputs for category and priority labels. However, due to API model compatibility issues, a rule-based fallback classification was implemented.

---

### STEP 4 — Routing

Tickets are routed as follows:

- billing → finance_email
- bug → dev_slack
- general / feature_request → shared_email

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

### Prompt 1 — Create the Flask endpoint

```text
Create a Flask-based customer support triage application for SE445 HW3.
The app should have a POST endpoint at /ticket.
It should accept JSON input with exactly three fields: name, email, and message.
For now, receive the data, parse it, and return a structured JSON response.
```

### Prompt 2 — Add validation logic

```text
Update the Flask application by adding validation logic.
Check whether name, email, and message are missing or empty.
Also validate the email format.
Invalid requests should not be deleted.
Instead, they should be stored with a validation_status field as Invalid and validation_errors explaining the problem.
```

### Prompt 3 — Add classification and priority

```text
Add classification logic for customer support tickets.
Classify each message into one of these categories: billing, bug, feature_request, general.
Also assign a priority level: low, medium, or high.
Return both category and priority in the API response.
```

### Prompt 4 — Add routing logic

```text
Add routing logic based on the category.
Billing tickets should be routed to finance_email.
Bug tickets should be routed to dev_slack.
General and feature_request tickets should be routed to shared_email.
Include routed_to in the response and in the stored record.
```

### Prompt 5 — Add Google Sheets storage

```text
Connect the Flask app to Google Sheets using gspread.
Every request should be saved as a new row.
The row should include timestamp, name, email, message, validation_status, validation_errors, category, priority, routed_to, and status.
Both valid and invalid requests must be stored.
```

### Prompt 6 — Fix AI compatibility issue

```text
Gemini API model compatibility caused runtime errors.
Update the classification step with a stable rule-based fallback so that the workflow continues to work reliably.
Keep the same output fields: category and priority.
```

---

## Project Files

- `app.py` → Main Flask application
- `requirements.txt` → Python dependencies
- `.env.example` → Example environment variables
- `README.md` → Project documentation
- `service_account.json` → Google Sheets credentials file, not uploaded to GitHub for security

---

## Setup Instructions

### 1) Create Google Sheet

Create a Google Sheet named:

```text
support_tickets
```

Create the following columns:

```text
timestamp | name | email | message | validation_status | validation_errors | category | priority | routed_to | status
```

---

### 2) Google Service Account

- Enable Google Sheets API
- Enable Google Drive API
- Create a Service Account
- Download the JSON key file
- Rename it to:

```text
service_account.json
```

- Put it in the same folder as `app.py`
- Share the Google Sheet with the service account email as Editor

---

### 3) Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4) Create .env File

```env
GOOGLE_SHEET_NAME=support_tickets
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
```

---

### 5) Run the App

```bash
python app.py
```

The app runs at:

```text
http://127.0.0.1:5000
```

---

## Test the Endpoint

### Valid Request

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" `
-Method POST `
-Headers @{ "Content-Type" = "application/json" } `
-Body '{"name":"Ceren","email":"ceren@gmail.com","message":"I was charged twice"}'
```

Expected response:

```json
{
  "category": "billing",
  "priority": "high",
  "routed_to": "finance_email",
  "status": "success",
  "validation": "Valid"
}
```

---

### Invalid Request

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" `
-Method POST `
-Headers @{ "Content-Type" = "application/json" } `
-Body '{"name":"","email":"cerenmail.com","message":""}'
```

Expected response:

```json
{
  "category": "none",
  "priority": "none",
  "routed_to": "none",
  "status": "success",
  "validation": "Invalid"
}
```

---

## Test Cases

### Valid Input

- Stored as Valid
- Classified into category and priority
- Routed correctly
- Stored in Google Sheets

### Invalid Input

- Stored as Invalid
- Validation errors are logged
- category, priority, and routed_to are set to none
- Invalid data is not deleted

---

## Prompt Engineering Note

This system was designed using prompt-based workflow generation in Antigravity.

The system design, validation logic, classification structure, routing rules, and fallback handling were created and refined through prompt engineering techniques.

---

## Notes

- AI classification is supported with a fallback rule-based mechanism to ensure continuous system operation. classification due to API compatibility issues.
- The system still meets the HW3 requirement by assigning category and priority values.
- The main focus is validation, classification, routing, and persistent storage.
- Sensitive files such as `.env` and `service_account.json` should not be uploaded to GitHub.

---

## Conclusion

This system successfully implements:

- Input validation
- Ticket classification
- Routing logic
- Google Sheets persistence
- Valid and invalid request logging

It fulfills the HW3 requirements for the Customer Support Triage workflow.
