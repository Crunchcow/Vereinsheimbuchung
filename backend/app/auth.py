import os
from msal import ConfidentialClientApplication
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from dotenv import load_dotenv

# Load .env file before reading environment variables
load_dotenv()

# You'll need to configure these via .env or environment variables
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else None
SCOPES = ["https://graph.microsoft.com/.default"]

app = None

def _init_app():
    global app
    if app is not None:
        return
    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        raise ValueError("Missing Azure credentials in environment variables or .env file")
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

# simple token provider for app-only auth
async def get_token():
    _init_app()

    result = app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" not in result:
        raise HTTPException(status_code=500, detail="Could not acquire token")
    return result["access_token"]


def get_graph_client(token: str):
    import requests
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    return session
