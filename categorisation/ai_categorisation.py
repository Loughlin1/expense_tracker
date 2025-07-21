"""
data_processing/ai_categorisation.py
    Module to categorise expenses using an LLM.
"""
import json
import yaml
import time
import re
import pandas as pd
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_prompt(name: str, variables: dict = {}) -> str:
    with open("categorisation/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)

    if name not in prompts:
        raise ValueError(f"Prompt '{name}' not found in prompts.yaml")

    # Support system and user messages separately
    prompt_block = prompts[name]
    rendered = {}
    for k, v in prompt_block.items():
        rendered[k] = Template(v).render(**variables)

    return rendered


def extract_json_objects(raw: str):
    """
    Extracts valid JSON list from raw LLM output, accounting for common LLM formatting quirks.
    """
    raw = raw.strip()

    # Try direct JSON parse
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if all(k.isdigit() for k in data):
                return [v for k, v in sorted(data.items(), key=lambda x: int(x[0]))]
    except json.JSONDecodeError:
        pass

    # Case: multiple JSON objects separated by commas, not wrapped in list
    # Attempt to wrap in brackets and parse
    if raw.startswith("{") and raw.endswith("}"):
        # Try wrapping in brackets
        try:
            wrapped = f"[{raw}]"
            return json.loads(wrapped)
        except json.JSONDecodeError:
            pass

    # Only the end is wrapped in a ']'
    if raw.startswith("{\n") and raw.endswith("}\n]"):
        try:
            wrapped = f"[\n{raw}"
            return json.loads(wrapped)
        except json.JSONDecodeError:
            pass

    # Case: matches valid JSON array using regex
    match = re.search(r"\[\s*{.*}\s*]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("No valid JSON list found in LLM response.")


def apply_ai_categorisation(
    model,
    transactions: pd.DataFrame,
    classification_features: list[str],
    categories: list[str],
    return_columns=["Category", "Confidence"],
    prompt_name="categorise_expenses",
    max_retries=3,
    delay=2,
    batch_size=20,
    max_workers=4,  # Number of parallel threads
) -> pd.DataFrame:
    """
    Batch categorises expenses using an LLM and returns a DataFrame with categories.

    Args:
        model (Callable): A callable that takes a prompt and returns a response.
        transactions (pd.DataFrame): DataFrame containing transactions.
        categories (list[str]): List of valid categories to assign.
        prompt_name (str): Name of the prompt block in prompts.yaml.
        max_retries (int): Retry attempts for LLM response.
        delay (int): Delay between retries.
        batch_size (int): Number of rows to send to the LLM per request.

    Returns:
        pd.DataFrame: DataFrame with assigned categories.
    """
    transactions["Index"] = transactions.index

    with open("categorisation/personal_rules.yaml", "r") as f:
        personal_rules = yaml.safe_load(f)

    def process_batch(start: int, batch: pd.DataFrame) -> list[dict]:
        end = start + batch_size
        prompt_parts = load_prompt(
            prompt_name,
            {
                "transactions": batch[classification_features].to_csv(index=False),
                "categories": categories,
                "personal_rules": personal_rules["personal_rules"],
                "batch_size": batch_size,
                "expected_indices": batch["Index"].tolist(),
            },
        )
        full_prompt = f"{prompt_parts.get('system', '')}\n\n{prompt_parts['user']}"

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[Batch {start}-{end-1}] Attempt {attempt}...")

                raw_response = model(full_prompt)
                json_data = extract_json_objects(raw_response)

                if not isinstance(json_data, list):
                    raise ValueError("LLM response is not a list.")

                # Validate response size
                expected_size = len(batch)
                if len(json_data) != expected_size:
                    raise ValueError(
                        f"Expected {expected_size} responses, but got {len(json_data)}.\n"
                        f"Batch indices: {batch['Index'].tolist()}\n"
                        f"Response: {json_data}\n"
                    )

                for item in json_data:
                    if "index" not in item and "Index" not in item:
                        raise ValueError(
                            "Missing both 'Index' and 'index' in response item."
                        )
                    for col in return_columns:
                        if col.lower() not in map(str.lower, item):
                            raise ValueError(f"Missing '{col}' in response item.")

                # Normalize keys
                return [
                    {k.capitalize(): v for k, v in item.items()} for item in json_data
                ]

            except (json.JSONDecodeError, ValueError) as e:
                print(f"{raw_response=}")
                print(f"❌ Failed to parse response: {e}")
                print("🔁 Retrying...")
                time.sleep(delay)
        else:
            raise RuntimeError("❌ Failed after retries.")

    # Split data into batches
    batches = [
        (start, transactions.iloc[start : start + batch_size])
        for start in range(0, len(transactions), batch_size)
    ]
    all_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_batch, start, batch) for start, batch in batches
        ]

        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as e:
                print(f"❌ Batch failed with error: {e}")
                raise

    # Merge results with original DataFrame
    result_df = pd.DataFrame(all_results)
    final_df = transactions.copy()
    final_df = final_df.drop(
        columns=return_columns, errors="ignore"
    )  # remove old column if exists
    final_df = final_df.merge(result_df, on="Index", how="left", suffixes=("", ""))
    final_df.drop(columns=["Index"], inplace=True)
    return final_df
