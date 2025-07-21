"""
data_processing/data_loading.py
"""
import os
import yaml
import pandas as pd
from parser.csv_parser import retrieve_csv_filepaths, load_csv_statement


def load_config(filepath="config.yaml"):
    with open(filepath) as f:
        config = yaml.safe_load(f)

    DATA_DIR = config["data_dir"]
    CSV_OUTPUT_PATH = os.path.join(DATA_DIR, config["csv_output"])
    EXCEL_OUTPUT_PATH = os.path.join(DATA_DIR, config["excel_output"])

    accounts = config["accounts"]
    account_colour_map = {
        account: details["colour"] for account, details in accounts.items()
    }
    if not isinstance(accounts, dict):
        raise Exception(f"accounts must be a dict. It is of type {type(accounts)}")

    category_list, category_colour_map, category_emoji_map = load_categories_and_colors(config)

    classification_features = config["classification_features"]
    output_columns = config["output_columns"]

    archive_folder = config.get("archive_folder", None)

    return (
        DATA_DIR,
        CSV_OUTPUT_PATH,
        EXCEL_OUTPUT_PATH,
        accounts,
        account_colour_map,
        category_list,
        category_colour_map,
        category_emoji_map,
        classification_features,
        output_columns,
        archive_folder,
    )


def load_categories_and_colors(config: dict) -> tuple[list[str], dict[str, str]]:
    categories = []
    color_map = {}
    category_emoji_map = {}

    for item in config.get("categories", []):
        if isinstance(item, dict):
            name = item.get("name")
            if name:
                categories.append(name)
                if "color" in item:
                    color_map[name] = item["color"]
                if "emoji" in item:
                    category_emoji_map[name] = item["emoji"]
        elif isinstance(item, str):
            categories.append(item)

    return categories, color_map, category_emoji_map


def check_dfs_not_empty(df_list: list[pd.DataFrame]):
    for i, df in enumerate(df_list):
        if df.empty or df.isna().all().all():
            print(
                f"Warning: DataFrame at index {i} is empty or all NA. Check source file."
            )


def load_and_combine_csvs(accounts: dict, data_dir: str, output_columns: list) -> tuple[pd.DataFrame, dict]:
    df_list = []
    filepaths_dict = {}

    for account, details in accounts.items():
        directory = os.path.join(data_dir, details["directory"])
        filepaths = retrieve_csv_filepaths(directory)
        filepaths_dict[account] = filepaths

        df_list.extend(
            load_csv_statement(path, account, details["mapping"], output_columns)
            for path in filepaths
        )
    check_dfs_not_empty(df_list)

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df["Date"] = pd.to_datetime(combined_df["Date"], format="%d/%m/%Y")
    combined_df.sort_values(by="Date", inplace=True)
    combined_df.reset_index(drop=True, inplace=True)
    return combined_df, filepaths_dict