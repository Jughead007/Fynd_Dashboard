from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form

import os
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base


DB_PATH = os.getenv("DB_PATH", "/data/feedback.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()



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

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def health_check(request: Request):
    return "<h3>App is running</h3>"

@app.get("/user", response_class=HTMLResponse)
def user_dashboard(request: Request):
    return templates.TemplateResponse(
        "user.html",
        {"request": request}
    )

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    db = SessionLocal()
    feedback_list = db.query(Feedback).all()
    db.close()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "feedbacks": feedback_list
        }
    )



@app.post("/submit", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    rating: int = Form(...),
    review: str = Form(...)
):
    # 1️⃣ Call mock AI
    ai_result = generate_ai_outputs(review, rating)

    # 2️⃣ Save everything to DB
    db = SessionLocal()
    feedback = Feedback(
        rating=rating,
        review=review,
        ai_summary=ai_result["summary"],
        ai_action=ai_result["action"]
    )
    db.add(feedback)
    db.commit()
    db.close()

    # 3️⃣ Show AI response to user
    return templates.TemplateResponse(
        "thank_you.html",
        {
            "request": request,
            "ai_response": ai_result["user_response"]
        }
    )



