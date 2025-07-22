"""
data_processing/manual_categorisation.py
"""

import re
import pandas as pd


def apply_categorisation_rules(df: pd.DataFrame, rules: list[dict]) -> pd.Series:
    categories = pd.Series(index=df.index, dtype=object)
    subcategories = pd.Series(index=df.index, dtype=object)

    for rule in rules:
        mask = pd.Series([True] * len(df))

        for cond in rule["conditions"]:
            col = cond["column"]
            if "contains" in cond:
                terms = cond["contains"]
                pattern = r"|".join(re.escape(term.lower()) for term in terms)
                mask &= df[col].astype(str).str.lower().str.contains(pattern, na=False)
            elif "equals" in cond:
                mask &= df[col] == cond["equals"]
            elif "gt" in cond:
                mask &= df[col] > cond["gt"]
            elif "lt" in cond:
                mask &= df[col] < cond["lt"]

        categories[mask] = rule["category"]
        if "subcategory" in rule:
            subcategories[mask] = rule["subcategory"]

    return pd.DataFrame({"Category": categories, "Subcategory": subcategories})
