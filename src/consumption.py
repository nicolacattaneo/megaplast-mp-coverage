import requests
from auth import get_access_token, D365_CONSUMPTION_URL

def _get_json_or_exit(response):
    if response.status_code != 200:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        exit()
    return response.json()

def get_consumption():
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(D365_CONSUMPTION_URL, headers=headers)  # type: ignore
    json_data = _get_json_or_exit(response)

    data = []

    while True:
        data.extend(json_data.get('value') or [])
        if '@odata.nextLink' in json_data:
            response = requests.get(json_data.get('@odata.nextLink'), headers=headers)  # type: ignore
            json_data = _get_json_or_exit(response)
        else:
            break

    return data
