from data_processing.data_loading import load_config
from data_processing.file_management import unarchive_processed_folders
from parser.excel.openpyxl.main import delete_sheet_in_excel_file
import pandas as pd
import os
import yaml
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    print("Loading config...")
    (
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
    ) = load_config()
    archive_dir = os.path.join(DATA_DIR, archive_folder)

    print(f"Unarchiving files in {archive_dir} and moving to {DATA_DIR}...")
    unarchive_processed_folders(archive_dir, DATA_DIR)

    print(f"Removing worksheet in {EXCEL_OUTPUT_PATH}...")
    delete_sheet_in_excel_file(EXCEL_OUTPUT_PATH)


if __name__ == "__main__":
    main()
