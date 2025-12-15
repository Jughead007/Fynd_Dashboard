Two-Dashboard AI Feedback System

A web-based AI feedback system built with FastAPI, Jinja2, and Google Gemini AI, designed to collect, process, and analyze user feedback in real-time. The project features two dashboards: a public-facing user dashboard and an internal admin dashboard, both using a shared persistent data source.

Features
User Dashboard

Submit a star rating and short review.

Receive AI-generated feedback acknowledging their input.

Feedback stored in CSV, JSON, or lightweight DB for persistence.

Admin Dashboard

Live-updating list of all submissions.

View user rating, review, AI-generated summary, and recommended actions.

Provides simple analytics such as average rating and total feedback count.

Designed for internal monitoring and business insights.

AI Integration

Uses Google Gemini API to generate user responses, summaries, and recommended actions.

Handles quota limits and API errors gracefully with fallback messages.

Tech Stack

Backend: FastAPI

Frontend: Jinja2 templates

AI: Google Gemini API

Persistent Storage: CSV/JSON or lightweight database

Deployment: Ready for Railway, Render, or similar platforms
