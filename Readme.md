# Discontinued Checker

Small Tkinter + pandas tool to compare Website, Everest, and Discontinued spreadsheets to identify discontinued parts that are still active on both systems.

## Features
- Load CSV or Excel (.xlsx/.xls) spreadsheets.
- Handles common formatting issues: preserves leading zeros, trims whitespace, uppercases part numbers.
- Normalizes price values and strips dollar signs/commas.
- Compares Website and Everest datasets and reports parts listed as discontinued but still active in both.
- Saves a plain-text report listing part numbers and both prices.
- Simple Tkinter GUI for file selection and running the audit.

## Installation

Requirements:
- Python 3.8+
- pandas
- openpyxl (for reading .xlsx files)
- xlrd (for older .xls files, optional)

Install dependencies:
```bash
pip install pandas openpyxl xlrd
