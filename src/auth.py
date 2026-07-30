import msal
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
D365_RESOURCE_URL = os.getenv("D365_RESOURCE_URL")
D365_DATA_URL = os.getenv("D365_DATA_URL")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

SCOPE = [f"{D365_RESOURCE_URL}/.default"]

def get_access_token():
    result = app.acquire_token_for_client(scopes=SCOPE)
    
    assert result is not None

    if "access_token" in result:
        return result["access_token"]
    else:
        print(result.get("error"))
        print(result.get("error_description"))