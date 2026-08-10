from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from datetime import date
from typing import cast
import math
import os



def setup_sheet(headers: list):
    wb = Workbook()
    ws = cast(Worksheet, wb.active)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="21295C", end_color="21295C", fill_type="solid")

    today = date.today()
    title = f'Reporte de Cobertura de Materia Prima - {today.strftime("%d/%m/%Y")}'
    ws['A1'] = title

    ws.merge_cells('A1:E1')

    for col in range(len(headers)):
        cell = ws.cell(row=3, column=col + 1)
        cell.value = headers[col]
        cell.font = header_font
        cell.fill = header_fill

    return wb, ws

FIELD_ORDER = ["ItemNumber", "ProductConfigurationId", "AvailableOnHandQuantity", "avg_daily_consumption", "days_remaining"]

def write_data_row(ws, row_number, material_data):
    NO_CONSUMPTION_FILL = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
    NO_INVENTORY_FILL = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
    
    for col_num, key in enumerate(FIELD_ORDER):
        value = material_data[key]
        cell = ws.cell(row=row_number, column=col_num + 1)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            cell.value = "N/A"
        else:
            cell.value = value
            if isinstance(value, (int, float)):
                cell.number_format = '#,##0.00'

        if material_data.get('no_inventory_record'):
            cell.fill = NO_INVENTORY_FILL
        elif material_data.get('no_consumption_data (last 7 days)'):
            cell.fill = NO_CONSUMPTION_FILL

SUM_FIELDS = ["AvailableOnHandQuantity", "avg_daily_consumption"]

def write_totals_row(ws, row_number, all_materials_data):
    for col_num, key in enumerate(FIELD_ORDER):
        cell = ws.cell(row=row_number, column=col_num + 1)
        if key in SUM_FIELDS:
            values = [row[key] for row in all_materials_data]
            total = sum(values)
            cell.value = total
            cell.number_format = '#,##0.00'
        elif key == "config":
            cell.value = "Total: "


def generate_report(report_data):
    filename = f"cobertura_mp_{date.today().isoformat()}.xlsx"
    filepath = os.path.join(os.getcwd(), filename)

    headers = FIELD_ORDER
    wb, ws = setup_sheet(headers)

    records = report_data.to_dict('records')

    row_num = 4
    for record in records:
        write_data_row(ws, row_num, record)
        row_num += 1

    write_totals_row(ws, row_num, records)

    wb.save(filepath)
    return filepath