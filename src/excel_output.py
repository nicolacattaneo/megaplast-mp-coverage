from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from datetime import date
from typing import cast



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

FIELD_ORDER = ["item", "config", "stock", "avg_daily", "days_remaining"]

# material_data = {"item": "AD_FLUIDEZ", "config": "Virgen", "stock": 509.04, ...}
def write_data_row(ws, row_number, material_data):
    for col_num, key in enumerate(FIELD_ORDER):
        value = material_data[key]
        cell = ws.cell(row=row_number, column=col_num + 1)
        cell.value = value
        if isinstance(value, (int, float)):
            cell.number_format = '#,##0.00'

SUM_FIELDS = ["stock", "avg_daily"]

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
