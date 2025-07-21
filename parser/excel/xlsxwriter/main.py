import numpy as np
import pandas as pd
import xlsxwriter


def apply_color_formatting(worksheet, col_idx, value_color_map, start_row, end_row, workbook):
    for value, color in value_color_map.items():
        fmt = workbook.add_format({'bg_color': color})
        col_letter = xlsxwriter.utility.xl_col_to_name(col_idx)
        worksheet.conditional_format(
            f"{col_letter}{start_row}:{col_letter}{end_row}",
            {
                'type': 'cell',
                'criteria': '==',
                'value': f'"{value}"',
                'format': fmt
            }
        )


def create_excel_with_formatting(
    df: pd.DataFrame,
    file_path: str,
    category_list: list[str],
    emoji_map: dict[str, str],
    category_colour_map: dict[str, str],
    account_colour_map: dict[str, str]
):
    
    # Replace NaN, NaT, None, inf with empty string
    df = df.replace({pd.NA: "", pd.NaT: "", None: "", np.inf: "", -np.inf: ""})
    df = df.where(pd.notnull(df), "")
    workbook = xlsxwriter.Workbook(file_path,  {'nan_inf_to_errors': True})
    worksheet = workbook.add_worksheet("Transactions")
    pivot_sheet = workbook.add_worksheet("Category Summary")

    # Write headers
    headers = df.columns.tolist()
    header_format = workbook.add_format({'bold': True, 'bg_color': '#DDEEFF'})
    for col_num, col_name in enumerate(headers):
        worksheet.write(0, col_num, col_name, header_format)

    # Write data
    for row_num, row in enumerate(df.itertuples(index=False), start=1):
        for col_num, value in enumerate(row):
            worksheet.write(row_num, col_num, value)

    # Format currency columns
    currency_format = workbook.add_format({'num_format': '£#,##0.00'})
    if "Amount In" in headers:
        idx = headers.index("Amount In")
        worksheet.set_column(idx, idx, 14, currency_format)
    if "Amount Out" in headers:
        idx = headers.index("Amount Out")
        worksheet.set_column(idx, idx, 14, currency_format)

    # Add dropdown for categories
    if "Category" in headers:
        col_idx = headers.index("Category")
        worksheet.data_validation(
            first_row=1,
            last_row=len(df),
            first_col=col_idx,
            last_col=col_idx,
            options={
                'validate': 'list',
                'source': category_list,
                'input_message': 'Pick a category',
                'show_input': True
            }
        )

    # Add emojis (optional)
    if emoji_map:
        col_idx = headers.index("Category")
        for row_num, value in enumerate(df["Category"], start=1):
            emoji = emoji_map.get(value, "")
            if emoji:
                worksheet.write(row_num, col_idx, f"{emoji} {value}")

    # Add total row
    total_format = workbook.add_format({'bold': True, 'bg_color': '#DDDDDD'})
    row_num = len(df) + 1
    if "Amount In" in headers:
        col = headers.index("Amount In")
        worksheet.write_formula(row_num, col, f"=SUM({xlsxwriter.utility.xl_col_to_name(col)}2:{xlsxwriter.utility.xl_col_to_name(col)}{row_num})", total_format)
    if "Amount Out" in headers:
        col = headers.index("Amount Out")
        worksheet.write_formula(row_num, col, f"=SUM({xlsxwriter.utility.xl_col_to_name(col)}2:{xlsxwriter.utility.xl_col_to_name(col)}{row_num})", total_format)

    # Freeze header
    worksheet.freeze_panes(1, 0)

    # Add pivot table
    pivot_table_name = "TransactionData"
    worksheet.add_table(0, 0, len(df), len(headers) - 1, {
        'name': pivot_table_name,
        'columns': [{'header': col} for col in headers]
    })

    pivot_sheet.add_pivot_table({
        'data': f'{pivot_table_name}',
        'name': 'CategoryPivot',
        'source_type': 'table',
        'destination': 'B3',
        'rows': [{'field': 'Category'}],
        'columns': [],
        'filters': [],
        'values': [
            {'field': 'Amount In', 'function': 'sum'},
            {'field': 'Amount Out', 'function': 'sum'}
        ]
    })

    # After writing data rows
    start_row = 2
    end_row = len(df) + 1

    if "Category" in df.columns:
        col_idx = df.columns.get_loc("Category")
        apply_color_formatting(worksheet, col_idx, category_colour_map, start_row, end_row, workbook)

    if "Account" in df.columns:
        col_idx = df.columns.get_loc("Account")
        apply_color_formatting(worksheet, col_idx, account_colour_map, start_row, end_row, workbook)

    workbook.close()