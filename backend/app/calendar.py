from datetime import datetime, timedelta
import os

# functions to call Graph API via provided client (requests.Session)

async def get_events_for_day(client, date: datetime):
    """Get all events for a specific day from the calendar"""
    calendar_address = os.getenv("CALENDAR_ADDRESS", "sportheim@westfalia-osterwick.de")
    
    # Set time range for the whole day
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Query calendar events
    url = f"https://graph.microsoft.com/v1.0/users/{calendar_address}/calendar/calendarView"
    params = {
        "startDateTime": start_of_day.isoformat(),
        "endDateTime": end_of_day.isoformat()
    }
    
    resp = client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    # Format events for frontend
    events = []
    for event in data.get("value", []):
        start = event.get("start", {}).get("dateTime", "")
        end = event.get("end", {}).get("dateTime", "")
        
        # Extract time portion (no subject for privacy)
        if start and end:
            try:
                start_time = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime("%H:%M")
                end_time = datetime.fromisoformat(end.replace("Z", "+00:00")).strftime("%H:%M")
                events.append({
                    "start": start_time,
                    "end": end_time
                })
            except:
                pass
    
    return events


async def check_availability(client, start_dt: datetime, end_time_str: str):
    """Check if the requested time slot is available by querying existing events"""
    calendar_address = os.getenv("CALENDAR_ADDRESS", "sportheim@westfalia-osterwick.de")
    end_dt = datetime.fromisoformat(f"{start_dt.date()}T{end_time_str}")
    
    # Query calendar events for the requested time period
    url = f"https://graph.microsoft.com/v1.0/users/{calendar_address}/calendar/calendarView"
    params = {
        "startDateTime": start_dt.isoformat(),
        "endDateTime": end_dt.isoformat()
    }
    
    resp = client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    # If there are any events in this time range, it's not available
    events = data.get("value", [])
    return len(events) == 0  # Available if no events found

async def create_event(client, start_dt: datetime, end_time_str: str, name: str, email: str, purpose: str, phone: str = ""):
    calendar_address = os.getenv("CALENDAR_ADDRESS", "sportheim@westfalia-osterwick.de")
    end_dt = datetime.fromisoformat(f"{start_dt.date()}T{end_time_str}")
    
    # Build body with contact information (similar to screenshot format)
    body_content = f"Anlass: {name} / {purpose}\n"
    if phone:
        body_content += f"Rückrufnummer: {phone}\n"
    body_content += f"Kontaktmail: {email}"
    
    event = {
        "subject": f"{name} / {purpose}",
        "body": {
            "contentType": "Text", 
            "content": body_content
        },
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Berlin"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Berlin"},
        "attendees": [],
    }
    # Create event in the calendar account
    resp = client.post(f"https://graph.microsoft.com/v1.0/users/{calendar_address}/calendar/events", json=event)
    resp.raise_for_status()
    return resp.json()

async def send_confirmation(client, event, user_email: str, user_name: str, date: str, start_time: str, end_time: str, purpose: str):
    sender_email = os.getenv("SENDER_EMAIL", "sportheim@westfalia-osterwick.de")
    
    # Format date nicely
    date_obj = datetime.fromisoformat(date)
    formatted_date = date_obj.strftime("%d.%m.%Y")
    
    # use Graph API sendMail
    message = {
        "message": {
            "subject": "Buchungsbestätigung - SV Westfalia Osterwick Vereinsheim",
            "body": {
                "contentType": "HTML", 
                "content": f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #c41e3a;">Buchungsbestätigung</h2>
                    <p>Hallo {user_name},</p>
                    <p>Ihre Buchung wurde erfolgreich angelegt:</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #c41e3a; margin: 20px 0;">
                        <p><strong>Anlass:</strong> {purpose}</p>
                        <p><strong>Datum:</strong> {formatted_date}</p>
                        <p><strong>Uhrzeit:</strong> {start_time} - {end_time} Uhr</p>
                        <p><strong>Ort:</strong> SV Westfalia Osterwick Vereinsheim</p>
                    </div>
                    <p>Bei Fragen wenden Sie sich bitte an unsere Ansprechpartner.</p>
                    <p>Mit sportlichen Grüßen,<br>
                    <strong>SV Westfalia Osterwick 1923 e.V.</strong></p>
                </body>
                </html>
                """
            },
            "toRecipients": [{"emailAddress": {"address": user_email}}],
            "from": {"emailAddress": {"address": sender_email}}
        },
        "saveToSentItems": "true"
    }
    
    resp = client.post(f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail", json=message)
    resp.raise_for_status()
    return resp.status_code
