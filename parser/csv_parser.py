"parser/csv_parser.py"

import os
import pandas as pd


def retrieve_csv_filepaths(dir: str) -> list[str]:
    """Retrieves CSV files in a directory"""
    return [
        os.path.join(dir, filename)
        for filename in os.listdir(dir)
        if filename.lower().endswith(".csv")
        and os.path.isfile(os.path.join(dir, filename))
    ]


def load_csv_statement(
    path: str, account: str, columns_mapping: dict, final_columns: list
):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    # print(df.columns)
    df = df.rename(columns=columns_mapping)
    df["Account"] = account
    df["Amount Out"] = -1 * df["Amount Out"].abs()
    if "Amount In" in df.columns:
        df["Amount In"] = df["Amount In"].abs()
    else:
        df["Amount In"] = None

    df["Amount"] = df["Amount Out"].fillna(0) + df["Amount In"].fillna(0)

    for col in final_columns:
        if col not in df.columns:
            df[col] = None

    # print(df[final_columns].head())
    return df[final_columns]


def append_to_csv(new_df, output_path):
    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    combined_df.to_csv(output_path, index=False)
