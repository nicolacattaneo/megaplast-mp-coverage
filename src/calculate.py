
def calculate_days_remaining(stock,  avg_daily_consumption):
    if avg_daily_consumption == 0:
        return f"Zero consumption, check manually. {stock} units left. "
    return stock / avg_daily_consumption

