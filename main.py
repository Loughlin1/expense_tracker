from data_processing.data_loading import load_config, load_and_combine_csvs
from data_processing.file_management import archive_processed_files
from categorisation.manual_categorisation import apply_categorisation_rules
from categorisation.ai_categorisation import apply_ai_categorisation
from categorisation.categorisation_rules import rules
from parser.excel.openpyxl.main import update_excel_file
from models.llama_runner import setup_llm
from models.ollama_runner import ask_ollama
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

    print("Parsing CSV statements...")

    print("Combining statements...")
    df, filepaths_dict = load_and_combine_csvs(accounts, DATA_DIR, output_columns)

    # Categorising
    print("Categorising transactions...")
    df["Category"] = apply_categorisation_rules(df, rules)
    # df = apply_ai_categorisation(ask_ollama, df, classification_features, category_list)
    df = df[output_columns]
    print(df.head())

    df["Category"] = df["Category"].apply(
        lambda cat: f"{category_emoji_map.get(cat, '')} {cat}" if cat in category_emoji_map else cat
    )
    category_colour_map = {
        f"{category_emoji_map.get(cat, '')} {cat}": colour for cat, colour in category_colour_map.items()
    }
    category_list_with_emojis = [f"{category_emoji_map.get(cat, '')} {cat}" for cat in category_list]

    df.to_csv(CSV_OUTPUT_PATH, index=False)
    print(f"Combined CSV saved to: {CSV_OUTPUT_PATH}")
    update_excel_file(
        df, EXCEL_OUTPUT_PATH, category_list_with_emojis, category_colour_map, account_colour_map
    )
    print(f"Excel spreadsheet saved to {EXCEL_OUTPUT_PATH}")

    print(f"Archiving processed files...")
    archive_processed_files(accounts, filepaths_dict, DATA_DIR, archive_folder)


if __name__ == "__main__":
    main()
