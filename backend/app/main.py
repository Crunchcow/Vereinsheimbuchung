from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from . import auth, calendar
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load .env file at startup
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="./app/templates")

# Dependency to get authenticated MS Graph client
async def get_client(token: str = Depends(auth.get_token)):
    return auth.get_graph_client(token)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # simple landing page with booking form
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/availability")
async def get_daily_availability(date: str, client=Depends(get_client)):
    """Check what times are already booked on a specific date"""
    try:
        booking_date = datetime.fromisoformat(date)
        events = await calendar.get_events_for_day(client, booking_date)
        return JSONResponse(content={"occupied": events})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/check")
async def check_availability(
    request: Request, 
    name: str = Form(...), 
    purpose: str = Form(...), 
    email: str = Form(...), 
    phone: str = Form(""), 
    date: str = Form(...), 
    start: str = Form(...), 
    end: str = Form(...), 
    privacy: str = Form(...),
    client=Depends(get_client)
):
    # business rule: require booking at least 14 days ahead
    booking_date = datetime.fromisoformat(f"{date}T{start}")
    if booking_date < datetime.utcnow() + timedelta(days=14):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Bitte mindestens 14 Tage vorher buchen. Kontaktieren Sie Ansprechpartner."})

    # query calendar
    available = await calendar.check_availability(client, booking_date, end)
    if not available:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Termin ist bereits belegt."})
    # create event
    event = await calendar.create_event(client, booking_date, end, name, email, purpose, phone)
    # send confirmation email to user
    await calendar.send_confirmation(client, event, email, name, date, start, end, purpose)
    return templates.TemplateResponse("index.html", {"request": request, "success": "Ihre Buchung wurde bestätigt. Sie erhalten eine E-Mail."})
