# Vereinsheim Buchung

This project replaces the existing Power Automate flow for booking the Vereinsheim.

## Overview

- **Backend:** FastAPI application that uses Microsoft Graph API via MSAL for authentication and calendar operations.
- **Frontend:** Simple web UI served by FastAPI with Jinja templates (can be replaced with React later).

## Features to implement

1. Authenticate with Azure AD (Microsoft identity platform).
2. Query the Vereinsheim calendar for availability.
3. Allow users to select a date/time and enforce rules (e.g., 14 days notice).
4. Create calendar events and send confirmation emails using Graph API.

## Getting Started

1. Create a virtual environment and install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and fill in the Azure AD values plus optional calendar/email settings.
4. Run the server with `uvicorn backend.app.main:app --reload`.

### Testing

- Install `pytest` (`pip install pytest`).
- Execute `pytest` from the `backend` directory to run the basic calendar-unit tests.

