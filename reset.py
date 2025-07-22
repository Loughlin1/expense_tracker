from data_processing.data_loading import load_config, load_path_variables
from data_processing.file_management import unarchive_processed_folders
from parser.excel.openpyxl.main import delete_sheet_in_excel_file
import pandas as pd
import os
import yaml
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    print("Loading config...")
    config = load_config("config.yaml")
    DATA_DIR, _, EXCEL_OUTPUT_PATH = load_path_variables(config)
    archive_folder = config["archive_folder"]
    archive_dir = os.path.join(DATA_DIR, archive_folder)

    print(f"Unarchiving files in '{archive_dir}' and moving to '{DATA_DIR}'...")
    unarchive_processed_folders(archive_dir, DATA_DIR)

    print(f"Removing worksheet in '{EXCEL_OUTPUT_PATH}'...")
    delete_sheet_in_excel_file(EXCEL_OUTPUT_PATH)


if __name__ == "__main__":
    main()
