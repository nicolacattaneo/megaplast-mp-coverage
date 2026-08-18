import requests
from auth import get_access_token, D365_CONSUMPTION_URL
from datetime import date, timedelta
import pandas as pd
from classification import normalize_configuration

def _get_json_or_raise(response):
    if response.status_code != 200:
        raise RuntimeError(f"D365 consumption request failed: {response.status_code} - {response.text}")
    return response.json()

MAX_CONSUMPTION_WINDOW_DAYS = 30

def get_consumption():
    token = get_access_token()

    today = date.today()
    window_start = today - timedelta(days=MAX_CONSUMPTION_WINDOW_DAYS)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
    "$filter": f"(ReferenceCategory eq Microsoft.Dynamics.DataEntities.InventTransType'ProdLine' or ReferenceCategory eq Microsoft.Dynamics.DataEntities.InventTransType'BomLine') and (InventLocationId eq 'MAP01' or InventLocationId eq 'MEZ01' or InventLocationId eq 'Compuestos' or InventLocationId eq 'P2Mezclas') and DatePhysical ge {window_start.isoformat()} and DatePhysical le {today.isoformat()}"
    }

    response = requests.get(D365_CONSUMPTION_URL, headers=headers, params=params)  # type: ignore
    json_data = _get_json_or_raise(response)

    data = []

    while True:
        data.extend(json_data.get('value') or [])
        if '@odata.nextLink' in json_data:
            response = requests.get(json_data.get('@odata.nextLink'), headers=headers)  # type: ignore
            json_data = _get_json_or_raise(response)
        else:
            break

    return data

def aggregate_consumption(data, days):
    df = pd.DataFrame(data)
    df['configId'] = df['configId'].apply(normalize_configuration)
    df['DatePhysical'] = pd.to_datetime(df['DatePhysical'])

    window_start = pd.Timestamp(date.today() - timedelta(days=days))
    if df['DatePhysical'].dt.tz is not None:
        window_start = window_start.tz_localize(df['DatePhysical'].dt.tz)
    windowed = df[(df['Qty'] < 0) & (df['DatePhysical'] >= window_start)]

    grouped = windowed.groupby(['ItemId', 'configId'])['Qty'].sum().reset_index()
    grouped[f'avg_daily_consumption_{days}d'] = grouped['Qty'].abs() / days
    grouped = grouped.drop(columns=['Qty'])

    return grouped