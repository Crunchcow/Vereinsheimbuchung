from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from . import auth, calendar
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from urllib.parse import quote

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

@app.get("/datenschutz", response_class=HTMLResponse)
async def datenschutz(request: Request):
    return templates.TemplateResponse("datenschutz.html", {"request": request})

@app.get("/api/availability")
async def get_daily_availability(date: str, client=Depends(get_client)):
    """Check what times are already booked on a specific date"""
    try:
        booking_date = datetime.fromisoformat(date)
        events = await calendar.get_events_for_day(client, booking_date)
        return JSONResponse(content={"occupied": events})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/month-bookings")
async def get_month_bookings(year: int, month: int, client=Depends(get_client)):
    """Get all bookings for a specific month"""
    try:
        # Get first and last day of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query calendar
        calendar_address = os.getenv("CALENDAR_ADDRESS", "sportheim@westfalia-osterwick.de")
        url = f"https://graph.microsoft.com/v1.0/users/{calendar_address}/calendar/calendarView"
        params = {
            "startDateTime": start_date.isoformat(),
            "endDateTime": end_date.isoformat()
        }
        
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # Group by date
        bookings_by_date = {}
        for event in data.get("value", []):
            event_start = event.get("start", {}).get("dateTime", "")
            if event_start:
                date_only = event_start.split('T')[0]
                if date_only not in bookings_by_date:
                    bookings_by_date[date_only] = []
                bookings_by_date[date_only].append({
                    "start": datetime.fromisoformat(event_start.replace("Z", "+00:00")).strftime("%H:%M"),
                    "end": datetime.fromisoformat(event.get("end", {}).get("dateTime", "").replace("Z", "+00:00")).strftime("%H:%M")
                })
        
        return JSONResponse(content=bookings_by_date)
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
    
    # Format date for display
    date_obj = datetime.fromisoformat(date)
    formatted_date = date_obj.strftime("%d.%m.%Y")
    
    # Redirect to success page with booking details
    return templates.TemplateResponse("success.html", {
        "request": request,
        "name": name,
        "email": email,
        "purpose": purpose,
        "formatted_date": formatted_date,
        "date": date,
        "start": start,
        "end": end
    })

@app.get("/download-ical")
async def download_ical(name: str, purpose: str, date: str, start: str, end: str):
    """Download iCal file for a booking"""
    try:
        # Create datetime objects
        start_dt = datetime.fromisoformat(f"{date}T{start}")
        end_dt = datetime.fromisoformat(f"{date}T{end}")
        
        # Format for iCal (YYYYMMDDTHHmmSS)
        start_ical = start_dt.strftime("%Y%m%dT%H%M%S")
        end_ical = end_dt.strftime("%Y%m%dT%H%M%S")
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        # Create unique ID
        uid = f"{start_ical}-{name.replace(' ', '-')}@westfalia-osterwick.de"
        
        # iCal content
        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SV Westfalia Osterwick//Vereinsheim Buchung//DE
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{timestamp}
DTSTART:{start_ical}
DTEND:{end_ical}
SUMMARY:{name} / {purpose}
DESCRIPTION:Anlass: {name} / {purpose}\\nZeit: {start} - {end} Uhr
LOCATION:SV Westfalia Osterwick Vereinsheim
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
        
        return Response(
            content=ical_content,
            media_type="text/calendar",
            headers={"Content-Disposition": "attachment; filename=vereinsheim-buchung.ics"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
