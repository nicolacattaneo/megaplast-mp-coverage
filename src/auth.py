import msal
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
D365_RESOURCE_URL = os.getenv("D365_RESOURCE_URL")
D365_DATA_URL = os.getenv("D365_DATA_URL")
D365_CONSUMPTION_URL = os.getenv("D365_CONSUMPTION_URL")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

D365_SCOPE = [f"{D365_RESOURCE_URL}/.default"]
GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]

def get_access_token(scope=D365_SCOPE):
    result = app.acquire_token_for_client(scopes=scope)
    
    assert result is not None

    if "access_token" in result:
        return result["access_token"]
    else:
        raise RuntimeError(f"Token acquisition failed: {result.get('error')} - {result.get('error_description')}")