import pandas as pd
from datetime import datetime

# File paths
input_path = 'PROJECT_selected.xlsx'
output_path = 'PROJECT_completed.xlsx'

excel_file = pd.ExcelFile(input_path)
modified_sheets = {}

# Function to determine "COMPLETED"/"NOT COMPLETED" status 
def stato_completamento(exp_date):
    if pd.isna(exp_date):
        return None
    if isinstance(exp_date, str):
        try:
            exp_date = pd.to_datetime(exp_date, errors='coerce')
        except:
            return None
    return "NOT COMPLETED" if exp_date.year >= 2025 else "COMPLETED"

for sheet_name in excel_file.sheet_names:
    df = excel_file.parse(sheet_name)
    
    if 'Expiration Date' in df.columns and 'Job Start Date' in df.columns:
        df['Expiration Date'] = pd.to_datetime(df['Expiration Date'], errors='coerce')
        df['Job Start Date'] = pd.to_datetime(df['Job Start Date'], errors='coerce')
        
        # Calculate duration in days
        df['Duration'] = (df['Expiration Date'] - df['Job Start Date']).dt.days
        
        # Completion status
        df['Job Finish'] = df['Expiration Date'].apply(stato_completamento)
        
        modified_sheets[sheet_name] = df

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for sheet_name, df in modified_sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Completed file saved as:", output_path)
