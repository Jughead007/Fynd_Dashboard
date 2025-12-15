from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import os
from google import genai


import csv
from datetime import datetime

CSV_PATH = os.getenv("CSV_PATH", "/data/feedback.csv")

# Ensure directory exists
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

CSV_HEADERS = [
    "timestamp",
    "rating",
    "review",
    "ai_response",
    "ai_summary",
    "ai_action",
]

def init_csv():
    """Create CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()

def append_feedback(row: dict):
    """Append one feedback row."""
    init_csv()
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)

def read_all_feedback():
    """Read all feedback rows."""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

from google import genai
import os

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def generate_ai_outputs(review: str, rating: int):
    prompt = f"""
A user submitted the following feedback.

Rating: {rating} stars
Review: "{review}"

Tasks:
1. Write a short, polite response to the user.
2. Write a one-sentence summary for an admin dashboard.
3. Suggest one clear recommended action for the business.

Respond strictly in this format:

USER_RESPONSE:
<text>

ADMIN_SUMMARY:
<text>

ADMIN_ACTION:
<text>
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    # DEBUG (TEMPORARY)
    print("====== GEMINI OUTPUT ======")
    print(text)
    print("===========================")

    result = {"user_response": "", "summary": "", "action": ""}

    current_key = None
    for line in text.splitlines():
        line = line.strip()

        if line == "USER_RESPONSE:":
            current_key = "user_response"
        elif line == "ADMIN_SUMMARY:":
            current_key = "summary"
        elif line == "ADMIN_ACTION:":
            current_key = "action"
        elif current_key and line:
            result[current_key] += line + " "

    return result


app = FastAPI(title="Two-Dashboard AI Feedback System")

@app.get("/", response_class=HTMLResponse)
def health_check(request: Request):
    return "<h3>App is running</h3>"

@app.get("/user", response_class=HTMLResponse)
def user_dashboard(request: Request):
    return templates.TemplateResponse(
        "user.html",
        {"request": request}
    )


@app.post("/submit", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    rating: int = Form(...),
    review: str = Form(...)
):
    ai_result = generate_ai_outputs(review, rating)

    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "rating": rating,
        "review": review,
        "ai_response": ai_result["user_response"],
        "ai_summary": ai_result["summary"],
        "ai_action": ai_result["action"],
    }

    append_feedback(row)

    return templates.TemplateResponse(
        "thank_you.html",
        {
            "request": request,
            "ai_response": ai_result["user_response"]
        }
    )
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    feedback_list = read_all_feedback()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "feedbacks": feedback_list
        }
    )


