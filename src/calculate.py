
def calculate_days_remaining(stock,  avg_daily_consumption):
    if avg_daily_consumption == 0:
        return None
    return round(stock / avg_daily_consumption)

def add_days_remaining(grouped_df):
    grouped_df['days_remaining_7d'] = grouped_df.apply(
        lambda row: calculate_days_remaining(row['AvailableOnHandQuantity'], row['avg_daily_consumption_7d']), axis=1
    )
    grouped_df['days_remaining_30d'] = grouped_df.apply(
        lambda row: calculate_days_remaining(row['AvailableOnHandQuantity'], row['avg_daily_consumption_30d']), axis=1
    )
    return grouped_df