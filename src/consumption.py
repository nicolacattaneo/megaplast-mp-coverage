import requests
from auth import get_access_token, D365_CONSUMPTION_URL
from datetime import date, timedelta
import pandas as pd

def _get_json_or_exit(response):
    if response.status_code != 200:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        exit()
    return response.json()

def get_consumption():
    token = get_access_token()

    today = date.today()
    week_ago = today - timedelta(days=7)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
    "$filter": f"(ReferenceCategory eq Microsoft.Dynamics.DataEntities.InventTransType'ProdLine' or ReferenceCategory eq Microsoft.Dynamics.DataEntities.InventTransType'BomLine') and (InventLocationId eq 'MAP01' or InventLocationId eq 'MEZ01' or InventLocationId eq 'Compuestos' or InventLocationId eq 'P2Mezclas') and DatePhysical ge {week_ago.isoformat()} and DatePhysical le {today.isoformat()}"
    }

    response = requests.get(D365_CONSUMPTION_URL, headers=headers, params=params)  # type: ignore
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

def aggregate_consumption(data):
    df = pd.DataFrame(data)
    consumption_only = df[df['Qty'] < 0]
    grouped = consumption_only.groupby(['ItemId', 'configId'])['Qty'].sum().reset_index()
    grouped['avg_daily_consumption'] = grouped['Qty'].abs() / 7

    return grouped