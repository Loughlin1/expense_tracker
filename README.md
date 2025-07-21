# Expense Tracker
A Python-based tool to parse and merge bank statements from CSV formats into a unified CSV and Excel file for expense tracking and analysis.

## Features
- Outputs a unified CSV with consistent schema
- Applies categorisation rules


## Setup
1. Install Dependencies:
```bash
pip install -r requirements.txt
```
2. Setup the config files:
- `config.yaml`
- `categorisation/categorisation_rules.py`
- `categorisation/personal_rules.yaml`

## Run the Script

```bash
python main.py