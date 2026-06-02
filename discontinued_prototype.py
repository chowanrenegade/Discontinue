import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def load_and_map(file_path, column_type="everest"):
    """Loads file, extracts specific columns, and renames them."""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.csv':
            # dtype=str preserves leading zeros like 05301
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        else:
            # keep_default_na=False prevents empty cells from breaking
            df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
    except Exception as e:
        raise ValueError(f"Could not read file: {e}")

    # Column Mapping Logic based on file type
    if column_type == "everest":
        cols = {'Sku': 'part_number', 'Sell Price': 'price'}
    elif column_type == "website":
        cols = {'Sku': 'part_number', 'Price': 'price'}
    elif column_type == "discontinued":
        cols = {'Sku': 'part_number'}  # Only care about the part number here
    else:
        raise ValueError("Invalid column type specified.")

    # Verify columns exist
    for original_col in cols.keys():
        if original_col not in df.columns:
            raise ValueError(f"Missing column: '{original_col}' in {os.path.basename(file_path)}")

    # Filter to only necessary columns and rename
    df = df[list(cols.keys())].rename(columns=cols)
    
    # Clean Part Numbers: Uppercase and strip spaces (STAYS AS STRING)
    df['part_number'] = df['part_number'].astype(str).str.strip().str.upper()
    
    # Clean Price if it's one of the pricing sheets
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'].replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
    
    return df

def run_comparison():
    file_web = entry_web.get()
    file_ev = entry_ev.get()
    file_disc = entry_disc.get()

    if not file_web or not file_ev or not file_disc:
        messagebox.showerror("Error", "Please select all three files first.")
        return

    try:
        # 1. Load and Format all 3 files
        df_web = load_and_map(file_web, column_type="website")
        df_ev = load_and_map(file_ev, column_type="everest")
        df_disc = load_and_map(file_disc, column_type="discontinued")

        # Get a clean set of discontinued part numbers for fast lookup
        discontinued_set = set(df_disc['part_number'].unique())

        # 2. Merge Website and Everest (Inner join to find parts in both systems)
        merged_df = pd.merge(df_web, df_ev, on='part_number', suffixes=('_website', '_everest'))

        # 3. Find Discontinued Parts still active on BOTH Website and Everest
        active_discontinued = merged_df[merged_df['part_number'].isin(discontinued_set)]

        # 4. Save File Dialog for Discontinued Report
        if not active_discontinued.empty:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile="active_discontinued_parts.txt",
                title="Save Discontinued Parts Report"
            )
            
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(f"DISCONTINUED PARTS STILL ACTIVE ON WEBSITE & EVEREST\n")
                    f.write("="*60 + "\n\n")
                    for _, row in active_discontinued.iterrows():
                        f.write(f"Part Number : {row['part_number']}\n")
                        f.write(f"  Website Price: ${row['price_website']:,.2f}\n")
                        f.write(f"  Everest Price: ${row['price_everest']:,.2f}\n")
                        f.write("-" * 60 + "\n")
                messagebox.showinfo("Success", f"Found {len(active_discontinued)} discontinued parts still active.\nReport saved to: {save_path}")
        else:
            messagebox.showinfo("Clean Audit", "No discontinued parts were found on the Website or Everest!")

    except Exception as e:
        messagebox.showerror("Processing Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("Price & Inventory Auditor Pro")
root.geometry("550x520") # Adjusted height for the third file section

def browse(entry_field):
    fn = filedialog.askopenfilename(filetypes=[("All Data Files", "*.xlsx *.xls *.csv")])
    if fn:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, fn)

# UI Elements - Website
tk.Label(root, text="Website Spreadsheet", font=('Arial', 10, 'bold')).pack(pady=(15,0))
tk.Label(root, text="(Needs 'Sku' column)", font=('Arial', 8, 'italic')).pack()
entry_web = tk.Entry(root, width=55)
entry_web.pack(pady=5)
tk.Button(root, text="Browse Website File", command=lambda: browse(entry_web)).pack(pady=2)

# UI Elements - Everest
tk.Label(root, text="Everest Spreadsheet", font=('Arial', 10, 'bold')).pack(pady=(15,0))
tk.Label(root, text="(Needs 'Sku' column)", font=('Arial', 8, 'italic')).pack()
entry_ev = tk.Entry(root, width=55)
entry_ev.pack(pady=5)
tk.Button(root, text="Browse Everest File", command=lambda: browse(entry_ev)).pack(pady=2)

# UI Elements - Discontinued
tk.Label(root, text="Discontinued Spreadsheet", font=('Arial', 10, 'bold')).pack(pady=(15,0))
tk.Label(root, text="(Needs 'Sku' column)", font=('Arial', 8, 'italic')).pack()
entry_disc = tk.Entry(root, width=55)
entry_disc.pack(pady=5)
tk.Button(root, text="Browse Discontinued File", command=lambda: browse(entry_disc)).pack(pady=2)

# Action Button
tk.Button(root, text="RUN AUDIT & CHECK DISCONTINUED", command=run_comparison, 
          bg="#2ecc71", fg="white", font=('Arial', 12, 'bold'), height=2).pack(pady=25, fill='x', padx=50)

root.mainloop()
