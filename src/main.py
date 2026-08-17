from merge import merge
from grouping import apply_grouping
from calculate import add_days_remaining
from excel_output import generate_report

def main():
    merged = merge()
    grouped, unclassified_items = apply_grouping(merged)
    report_data = add_days_remaining(grouped)
    filepath = generate_report(report_data, unclassified_items)
    print(f"Report saved to {filepath}")
    return filepath