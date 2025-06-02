import pandas as pd
import matplotlib.pyplot as plt
import os

# Input file
input_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_completed.xlsx"
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# Output folder
output_folder = r"C:\Users\aless\OneDrive\Desktop\py\individual_scatter_plots"
os.makedirs(output_folder, exist_ok=True)

# Color map 
color_map = {
    "MH": "#87CEFA",  # light blue
    "BL": "#FF9999"   # light pink
}

# Axis parameters
x_min, x_max = 1980, 2027
y_min, y_max = 0, 4000
x_ticks = list(range(x_min, x_max + 1, 5))
y_ticks = list(range(y_min, y_max + 1, 500))

# Generate scatter plot for each borough × permit subtype
for sheet in sheet_names:
    df = xls.parse(sheet)
    df["Permit Subtype"] = df["Permit Subtype"].str.strip()
    
    for subtype in ["MH", "BL"]:
        df_sub = df[df["Permit Subtype"] == subtype].copy()
        df_sub = df_sub.dropna(subset=["Job Start Date", "Duration"])
        df_sub["Year"] = pd.to_datetime(df_sub["Job Start Date"], errors='coerce').dt.year
        
        df_sub = df_sub[
            (df_sub["Year"] >= x_min) & (df_sub["Year"] <= x_max) &
            (df_sub["Duration"] >= y_min) & (df_sub["Duration"] <= y_max)
        ]
        
        if df_sub.empty:
            continue
        
        # Plot
        plt.figure(figsize=(8, 5))
        plt.scatter(
            df_sub["Year"],
            df_sub["Duration"],
            color=color_map[subtype],
            alpha=0.6,
            edgecolor="black",
            linewidth=0.3
        )
        plt.title(f"{sheet.upper()} – {subtype} – Permit Durations")
        plt.xlabel("Start Year")
        plt.ylabel("Duration (days)")
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xticks(x_ticks)
        plt.yticks(y_ticks)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        
        filename = f"{sheet.upper()}_{subtype}_scatter.png".replace(" ", "_")
        plt.savefig(os.path.join(output_folder, filename))
        plt.close()

print("Scatter plots saved in:", output_folder)
