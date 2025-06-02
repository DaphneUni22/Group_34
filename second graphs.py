import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.patches import Patch

# File path
input_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_cleaned.xlsx"
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# Colors (light for boroughs, darker for NYC)
colors_borough = {"MH": "#87CEFA", "BL": "#FF9999"}  # light blue, light pink
colors_nyc = {"MH": "#1E90FF", "BL": "#B22222"}      # dark blue, dark red

# Calculate average duration for each borough
all_averages = []
for sheet in sheet_names:
    df = xls.parse(sheet)
    df["Permit Subtype"] = df["Permit Subtype"].str.strip()
    
    avg = (
        df[["Permit Subtype", "Duration"]]
        .dropna()
        .groupby("Permit Subtype")
        .mean()
        .reindex(["MH", "BL"])
    )
    avg.columns = [sheet]
    all_averages.append(avg)

# Calculate average for all NYC
df_total = pd.concat([xls.parse(s) for s in sheet_names])
df_total["Permit Subtype"] = df_total["Permit Subtype"].str.strip()
avg_total = (
    df_total[["Permit Subtype", "Duration"]]
    .dropna()
    .groupby("Permit Subtype")
    .mean()
    .reindex(["MH", "BL"])
)
avg_total.columns = ["NYC"]
all_averages.append(avg_total)

# Combine all averages into a single DataFrame
df_avg = pd.concat(all_averages, axis=1)

# PLOT
fig, ax = plt.subplots(figsize=(12, 6))

# Labels and group positions
groups = df_avg.columns.tolist()
x = np.arange(len(groups))  # central position for each borough
bar_width = 0.35

for idx, borough in enumerate(groups):
    is_nyc = borough.upper() == "NYC"
    for offset, subtype in zip([-bar_width / 2, bar_width / 2], ["MH", "BL"]):
        duration = df_avg.loc[subtype, borough]
        color = colors_nyc[subtype] if is_nyc else colors_borough[subtype]
        ax.bar(idx + offset, duration, width=bar_width, color=color, edgecolor="black")

# Axis and title
ax.set_xticks(x)
ax.set_xticklabels([b.upper() for b in groups], rotation=0)
ax.set_ylabel("Average Permit Duration (days)")
ax.set_title("Average Duration of MH / BL Permits by Borough and NYC Total")
ax.set_ylim(0, 600)
ax.grid(axis="y", linestyle="--", alpha=0.6)

# Custom legend
legend_elements = [
    Patch(facecolor=colors_borough["MH"], edgecolor="black", label="MH (borough)"),
    Patch(facecolor=colors_borough["BL"], edgecolor="black", label="BL (borough)"),
    Patch(facecolor=colors_nyc["MH"], edgecolor="black", label="MH (NYC)"),
    Patch(facecolor=colors_nyc["BL"], edgecolor="black", label="BL (NYC)")
]
ax.legend(handles=legend_elements, loc="upper right")

# Save plot
plt.tight_layout()
plt.show()
plt.savefig(r"C:\Users\aless\OneDrive\Desktop\py\unified_grouped_permit_duration.png")
