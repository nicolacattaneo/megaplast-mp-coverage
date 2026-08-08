
def calculate_days_remaining(stock,  avg_daily_consumption):
    if avg_daily_consumption == 0:
        return None
    return stock / avg_daily_consumption

def add_days_remaining(merged_df):
    results = []
    for _, row in merged_df.iterrows():
        days = calculate_days_remaining(row['AvailableOnHandQuantity'], row['avg_daily_consumption'])
        results.append(days)
    merged_df['days_remaining'] = results
    merged_df['no_consumption_data (last 7 days)'] = merged_df['avg_daily_consumption'] == 0
    return merged_df