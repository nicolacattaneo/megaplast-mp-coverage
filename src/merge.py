import pandas as pd
from inventory import get_inventory, aggregate_inventory
from consumption import aggregate_consumption, get_consumption

RAW_MATERIAL_PREFIXES = ('AD', 'CC', 'CO', 'Co', 'EL', 'FI', 'FV', 'PC', 'PE', 'PP', 'PV', 'TE', 'TP', 'TPE', 'Mo', 'Re', 'To')
def is_raw_material(item_number):
    return item_number.startswith(RAW_MATERIAL_PREFIXES)

def get_raw_material_inventory():
    data = get_inventory()
    excluded = [row['ItemNumber'] for row in data if not is_raw_material(row['ItemNumber'])]
    if excluded:
        print(f"Excluded {len(excluded)} non-material items: {excluded[:10]}...")
    return [row for row in data if is_raw_material(row['ItemNumber'])]

def merge():
    consumption_data = get_consumption()
    consumption_7d = aggregate_consumption(consumption_data, 7)
    consumption_30d = aggregate_consumption(consumption_data, 30)
    inventory_df = aggregate_inventory(get_raw_material_inventory())

    consumption_7d = consumption_7d[consumption_7d['ItemId'].apply(is_raw_material)]
    consumption_30d = consumption_30d[consumption_30d['ItemId'].apply(is_raw_material)]

    consumption_7d = consumption_7d.rename(columns={'ItemId': 'ItemNumber', 'configId': 'ProductConfigurationId'})
    consumption_30d = consumption_30d.rename(columns={'ItemId': 'ItemNumber', 'configId': 'ProductConfigurationId'})

    # Does warehouse matter?
    merged = pd.merge(inventory_df, consumption_7d, on=['ItemNumber', 'ProductConfigurationId'], how="outer")
    merged = pd.merge(merged, consumption_30d, on=['ItemNumber', 'ProductConfigurationId'], how="outer")

    merged['AvailableOnHandQuantity'] = merged['AvailableOnHandQuantity'].fillna(0)
    merged['avg_daily_consumption_7d'] = merged['avg_daily_consumption_7d'].fillna(0)
    merged['avg_daily_consumption_30d'] = merged['avg_daily_consumption_30d'].fillna(0)

    return merged
