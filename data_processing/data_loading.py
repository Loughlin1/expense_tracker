"""
data_processing/data_loading.py
"""

import os
import yaml
import pandas as pd
from parser.csv_parser import retrieve_csv_filepaths, load_csv_statement


def load_config(filepath="config.yaml"):
    """
    Load YAML configuration file.

    Args:
        filepath (str): Path to the config file. Defaults to 'config.yaml'.

    Returns:
        dict: Parsed YAML configuration as a dictionary.
    """
    with open(filepath) as f:
        config = yaml.safe_load(f)
    return config


def load_path_variables(config: dict):
    """
    Extract and construct key path variables from configuration.

    Args:
        config (dict): Loaded configuration dictionary.

    Returns:
        tuple[str, str, str]: DATA_DIR, CSV_OUTPUT_PATH, EXCEL_OUTPUT_PATH
    """
    DATA_DIR = config["data_dir"]
    CSV_OUTPUT_PATH = os.path.join(DATA_DIR, config["csv_output"])
    EXCEL_OUTPUT_PATH = os.path.join(DATA_DIR, config["excel_output"])
    return DATA_DIR, CSV_OUTPUT_PATH, EXCEL_OUTPUT_PATH


def load_accounts_variables(config: dict):
    """
    Extract account information and map accounts to color values.

    Args:
        config (dict): Loaded configuration dictionary.

    Returns:
        tuple[dict, dict]:
            - accounts: The account details dictionary.
            - account_colour_map: A map from account name to color string.
    """
    accounts = config["accounts"]
    account_colour_map = {
        account: details["colour"] for account, details in accounts.items()
    }
    if not isinstance(accounts, dict):
        raise Exception(f"accounts must be a dict. It is of type {type(accounts)}")
    return accounts, account_colour_map


def load_categories_and_colors(
    config: dict,
) -> tuple[list[str], list[str], dict[str, str], dict[str, str]]:
    """
    Extract categories, subcategories, color map, and emoji map from configuration.

    Args:
        config (dict): Loaded configuration dictionary.

    Returns:
        tuple:
            - list of category names
            - list of subcategory names
            - dict mapping category names to hex color strings
            - dict mapping category names to emojis
    """
    categories = []
    subcategories = []
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
                if "subcategories" in item:
                    subcategories.extend(item["subcategories"])
        elif isinstance(item, str):
            categories.append(item)

    return categories, subcategories, color_map, category_emoji_map


def check_dfs_not_empty(df_list: list[pd.DataFrame]):
    """
    Check that each DataFrame in a list is not empty or fully NA.

    Args:
        df_list (list[pd.DataFrame]): List of DataFrames to validate.

    Prints:
        Warning message for each empty or all-NA DataFrame.
    """
    for i, df in enumerate(df_list):
        if df.empty or df.isna().all().all():
            print(
                f"Warning: DataFrame at index {i} is empty or all NA. Check source file."
            )


def load_and_combine_csvs(
    accounts: dict, data_dir: str, output_columns: list
) -> tuple[pd.DataFrame, dict]:
    """
    Load, parse, and combine CSV statements for multiple accounts.

    Args:
        accounts (dict): Dictionary of account names and their metadata (directory, mapping).
        data_dir (str): Base directory where account folders are stored.
        output_columns (list): Desired column names for the final DataFrame.

    Returns:
        tuple:
            - Combined pandas DataFrame of all transactions
            - Dictionary mapping account names to their CSV file paths
    """
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
