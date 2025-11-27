import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# ========================
# 1. Add to CSV
# ========================
def add_to_csv(
        data: List[Dict[str, Any]],
        filename: str,
        encoding: str = 'utf-8',
        index: bool = False,
        append: bool = True,
        **kwargs
    ) -> None:
    """
    Append or create a CSV file with the provided list of dictionaries.

    Parameters
    ----------
    data : List[Dict[str, Any]]
        Rows to write, each dict representing a record.
    filename : str
        Path to the CSV file.
    encoding : str, optional
        File encoding (default 'utf-8').
    index : bool, optional
        Write pandas index column (default False).
    append : bool, optional
        If True and file exists, append rows below existing data; otherwise overwrite.
    **kwargs
        Extra arguments passed to pandas.DataFrame.to_csv.
    """
    if not data:
        print("No data → nothing saved.")
        return

    df = pd.DataFrame(data)
    file_exists = Path(filename).exists()

    mode = 'a' if append else 'w'
    header = not (append and file_exists)

    df.to_csv(filename, mode=mode, header=header, encoding=encoding, index=index, **kwargs)
    action = "Appended" if (append and file_exists) else "Saved"
    print(f"{action} {len(data)} row(s) → {filename}")


# ========================
# 2. Add to Excel (.xlsx)
# ========================
def add_to_excel(
        data: List[Dict[str, Any]],
        filename: str,
        sheet_name: str = "Sheet1",
        index: bool = False,
        append: bool = True,
        **kwargs
    ) -> None:
    """
    Append or create an Excel file (.xlsx) with the provided list of dictionaries.

    Parameters
    ----------
    data : List[Dict[str, Any]]
        Rows to write, each dict representing a record.
    filename : str
        Path to the Excel file.
    sheet_name : str, optional
        Target worksheet name (default "Sheet1").
    index : bool, optional
        Write pandas index column (default False).
    append : bool, optional
        If True and file exists, append rows below existing data; otherwise overwrite.
    **kwargs
        Extra arguments passed to pandas.DataFrame.to_excel.
    """
    if not data:
        print("No data → nothing saved.")
        return

    df = pd.DataFrame(data)
    file_exists = Path(filename).exists()

    if append and file_exists:
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            workbook = writer.book
            start_row = workbook[sheet_name].max_row if sheet_name in workbook.sheetnames else 0
            df.to_excel(writer, sheet_name=sheet_name, startrow=start_row,
                        index=index, header=(start_row == 0), **kwargs)
        print(f"Appended {len(data)} row(s) → {filename} [{sheet_name}]")
    else:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)
        print(f"Saved {len(data)} row(s) → {filename} [{sheet_name}]")


# ========================
# 3. Add to JSON (JSON Lines – always safe & appendable)
# ========================
def add_to_json(
        data: List[Dict[str, Any]],
        filename: str,
        append: bool = True,
        indent: int = 2,
        **kwargs
    ) -> None:
    """
    Adds records to a JSON file as a proper array: [ {...}, {...} ]
    - If file exists and is valid JSON + append=True → safely appends
    - If file doesn't exist or append=False → creates/overwrites
    """
    if not data:
        print("No data → nothing saved.")
        return

    file_path = Path(filename)
    existing_data = []

    # Try to load existing data if file exists and we're appending
    if append and file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    print("Existing JSON is not an array → starting fresh")
                    existing_data = []
        except (json.JSONDecodeError, OSError):
            print("Existing file is corrupted or unreadable → starting fresh")
            existing_data = []

    # Combine old + new data
    final_data = existing_data + data

    # Write back as proper formatted JSON array
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=indent, ensure_ascii=False, **kwargs)

    action = "Appended to" if (append and existing_data) else "Saved"
    total = len(final_data)
    print(f"{action} {filename} → {total} total record(s) in JSON array")


# ===================================================================
# Beautiful & simple usage
# ===================================================================
if __name__ == "__main__":

    data = [
        {"id": 1, "name": "Alice", "score": 95},
        {"id": 2, "name": "Bob",   "score": 87}
    ]
    
    add_to_csv(data, "players.csv")
    add_to_excel(data, "players.xlsx", sheet_name="Ranking")
    add_to_json(data, "players.json", indent=4)
    