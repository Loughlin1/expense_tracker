"""
data_processing/file_management.py
"""

import os
import shutil
import datetime
import pandas as pd


def check_file_month(file_path: str, date_columns=None) -> str:
    """
    Reads a CSV or Excel file and returns the earliest month (YYYY-MM) found in the specified date columns.

    Parameters:
        file_path (str): Path to the file.
        date_columns (list[str], optional): List of possible date column names to check. Defaults to ["Date", "Transaction Date"].

    Returns:
        str: Earliest month in 'YYYY-MM' format.

    Raises:
        ValueError: If no supported file type, no date columns found, or no valid dates found.
    """
    if date_columns is None:
        date_columns = ["Date", "Transaction Date"]

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Find first matching date column
    date_col = None
    for col in date_columns:
        if col in df.columns:
            date_col = col
            break

    if not date_col:
        raise ValueError(f"No date column found. Checked columns: {date_columns}")

    # Ensure datetime dtype, coerce errors
    df[date_col] = pd.to_datetime(df[date_col], format="%d/%m/%Y")

    if df[date_col].isnull().all():
        raise ValueError(f"No valid dates found in '{date_col}' column.")

    # Get earliest date and format month string
    earliest_date = df[date_col].dropna().min()
    month_str = earliest_date.strftime("%Y-%m")
    return month_str


def archive_file(file_path: str, account: str, archive_dir: str):
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    month = check_file_month(file_path)
    filename = os.path.basename(file_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_name = f"{account}_{month}.csv"
    archived_path = os.path.join(archive_dir, archived_name)

    shutil.move(file_path, archived_path)
    print(f"[📁] Archived {filename} → {archived_name}")


def archive_processed_files(
    accounts: dict, filepaths_dict: dict, data_dir: str, archive_folder: str
):
    if not archive_folder:
        return
    for account, details in accounts.items():
        for file in filepaths_dict.get(account, []):
            dir_name = details["directory"]
            archive_directory = os.path.join(data_dir, archive_folder, dir_name)
            archive_file(file, account, archive_directory)


def unarchive_processed_folders(
    archive_dir: str, destination_dir: str, move: bool = True
):
    """
    Move or copy entire folders from `archive_dir` to `destination_dir`, and ensure
    nothing remains in the archive afterwards.

    Args:
        archive_dir (str): The archive directory containing folders to restore.
        destination_dir (str): The location to move or copy the folders to.
        move (bool): If True, folders will be moved. If False, folders will be copied.
    """
    if not os.path.exists(archive_dir):
        raise FileNotFoundError(f"Archive directory does not exist: {archive_dir}")

    os.makedirs(destination_dir, exist_ok=True)

    for folder_name in os.listdir(archive_dir):
        src_path = os.path.join(archive_dir, folder_name)
        dest_path = os.path.join(destination_dir, folder_name)

        if not os.path.isdir(src_path):
            continue  # Skip files

        if move:
            if not os.path.exists(dest_path):
                shutil.move(src_path, dest_path)
                print(f"[📁] Moved {folder_name} → {dest_path}")
            elif os.path.isdir(dest_path) and not os.listdir(dest_path):
                os.rmdir(dest_path)
                shutil.move(src_path, dest_path)
                print(f"[♻️] Replaced empty {folder_name} → {dest_path}")
            else:
                # Destination exists and has content — merge then delete
                for item in os.listdir(src_path):
                    src_item = os.path.join(src_path, item)
                    dest_item = os.path.join(dest_path, item)

                    if os.path.isdir(src_item):
                        if not os.path.exists(dest_item):
                            shutil.copytree(src_item, dest_item)
                        else:
                            for root, _, files in os.walk(src_item):
                                rel_path = os.path.relpath(root, src_path)
                                target_dir = os.path.join(dest_path, rel_path)
                                os.makedirs(target_dir, exist_ok=True)
                                for file in files:
                                    shutil.copy2(
                                        os.path.join(root, file),
                                        os.path.join(target_dir, file),
                                    )
                    else:
                        shutil.copy2(src_item, dest_item)

                shutil.rmtree(src_path)  # Ensure the archive folder is removed
                print(f"[📥] Merged and removed {folder_name} from archive")
        else:
            # Copy mode: copy entire folder contents, then delete the archive folder
            if not os.path.exists(dest_path):
                shutil.copytree(src_path, dest_path)
                print(f"[📁] Copied {folder_name} → {dest_path}")
            else:
                for item in os.listdir(src_path):
                    src_item = os.path.join(src_path, item)
                    dest_item = os.path.join(dest_path, item)

                    if os.path.isdir(src_item):
                        if not os.path.exists(dest_item):
                            shutil.copytree(src_item, dest_item)
                        else:
                            for root, _, files in os.walk(src_item):
                                rel_path = os.path.relpath(root, src_path)
                                target_dir = os.path.join(dest_path, rel_path)
                                os.makedirs(target_dir, exist_ok=True)
                                for file in files:
                                    shutil.copy2(
                                        os.path.join(root, file),
                                        os.path.join(target_dir, file),
                                    )
                    else:
                        shutil.copy2(src_item, dest_item)

                shutil.rmtree(src_path)
                print(f"[📥] Copied and removed {folder_name} from archive")
