import pandas as pd

file_path = r'C:\Users\aless\OneDrive\Desktop\py\PROJECT_base.xlsx'
xls = pd.ExcelFile(file_path)

with pd.ExcelWriter('PROJECT_selected.xlsx') as writer:
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Column B (Job Type): only rows with "A2"
        df = df[df['Job Type'] == 'A2']
        
        # Column C (Bldg Type): only rows with "2"
        df = df[df['Bldg Type'] == 2]
        
        # Column D (Residential): only rows with "YES"
        df = df[df['Residential'] == 'YES']
        
        # Column E (Work Type): only rows with "BL", "MH"
        df = df[df['Work Type'].isin(['BL', 'MH'])]
        
        # Column F (Permit Status): only rows with "ISSUED", "RE-ISSUED"
        df = df[df['Permit Status'].isin(['ISSUED', 'RE-ISSUED'])]
        
        # Save all sheets in the new Excel File 
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("PROJECT_selected")
