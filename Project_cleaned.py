import pandas as pd

# File path
input_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_completed.xlsx"
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# Duration limits for each permit type
duration_limits = {
    "MH": 271,
    "BL": 181
}

# Output cleaned file path
output_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_cleaned.xlsx"
writer = pd.ExcelWriter(output_path, engine="openpyxl")

for sheet in sheet_names:
    df = xls.parse(sheet)
    
    # Filter valid values for Duration and Permit Subtype
    df = df.dropna(subset=["Permit Subtype", "Duration"])
    df["Permit Subtype"] = df["Permit Subtype"].str.strip()
    
    # Apply filters for each permit subtype
    clean_df = pd.DataFrame()
    for subtype, max_duration in duration_limits.items():
        filtered = df[(df["Permit Subtype"] == subtype) & (df["Duration"] <= max_duration)]
        clean_df = pd.concat([clean_df, filtered], ignore_index=True)
    
    # Write the cleaned sheet
    clean_df.to_excel(writer, sheet_name=sheet, index=False)

writer.close()
print("Cleaned file saved to:", output_path)
