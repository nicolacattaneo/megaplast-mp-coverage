from merge import merge
from calculate import add_days_remaining
from excel_output import generate_report

def main():    
    merged = merge()
    report_data = add_days_remaining(merged)
    filepath = generate_report(report_data)
    print(f"Report saved to {filepath}")
    return filepath