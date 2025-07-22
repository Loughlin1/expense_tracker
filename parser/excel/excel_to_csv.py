import pandas as pd
import os


def clean_df(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Drop fully empty rows
    df = df.dropna(thresh=3)
    cols_to_drop = [0] + list(range(11, 15)) + list(range(16, 25))
    df = df.drop(df.columns[cols_to_drop], axis=1)
    print(df)
    df.columns = [
        "Date",
        "Time",
        "Type",
        "Name",
        "Amount",
        "Category",
        "Amount Out",
        "Amount In",
        "Notes",
        "Account",
        "sheet",
    ]
    df = df[df["sheet"] != "Template"]
    # Strip strings in cells
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[df["Date"] != "Date"]
    df = df[df["Date"] != "Total"]

    # Attempt to parse date columns
    for col in df.columns:
        if "date" in col:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    return df


def excel_to_single_csv(input_path: str, output_path: str):
    """
    Reads all sheets from an Excel file and merges them into one CSV.
    """
    excel_file = pd.ExcelFile(input_path)
    all_sheets = []

    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)
        df["Sheet"] = sheet_name  # Optional: track source sheet
        all_sheets.append(df)

    merged_df = pd.concat(all_sheets, ignore_index=True)
    print(merged_df)
    merged_df = clean_df(merged_df)
    print(merged_df)

    merged_df.to_csv(output_path, index=False)
    print(f"✅ Merged CSV saved to: {output_path}")


if __name__ == "__main__":
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    DATA_DIR = config["data_dir"]
    input_excel_path = os.path.join(DATA_DIR, "expenses.xlsx")
    output_csv_path = os.path.join(DATA_DIR, "transactions_labelled.csv")

    os.makedirs(DATA_DIR, exist_ok=True)
    excel_to_single_csv(input_excel_path, output_csv_path)
