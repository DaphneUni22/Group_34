import pandas as pd
import matplotlib.pyplot as plt
import os

# FILE CONFIGURATION
input_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_cleaned.xlsx"
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# OUTPUT FOLDERS
base_dir = "Duration_Graphs"
dir_boroughs = os.path.join(base_dir, "boroughs_grouped")
dir_total = os.path.join(base_dir, "nyc_total_grouped")
os.makedirs(dir_boroughs, exist_ok=True)
os.makedirs(dir_total, exist_ok=True)

# COLORS
colors_borough = {"MH": "#87CEFA", "BL": "#FF9999"}
colors_nyc = {"MH": "#1E90FF", "BL": "#B22222"}

# CUSTOM DURATION BINS
custom_bins = {
    "BL": {
        "bins": [0, 60, 120, 179, float("inf")],
        "labels": ["3–5 floors", "6–10 floors", "11–15 floors", ">15 floors"]
    },
    "MH": {
        "bins": [0, 120, 180, 269, float("inf")],
        "labels": ["3–5 floors", "6–10 floors", "11–15 floors", ">15 floors"]
    }
}

# FUNCTION TO COMPUTE DURATION
def compute_duration(df):
    df["Issuance Date"] = pd.to_datetime(df["Issuance Date"], errors="coerce")
    df["Expiration Date"] = pd.to_datetime(df["Expiration Date"], errors="coerce")
    df["Duration"] = (df["Expiration Date"] - df["Issuance Date"]).dt.days
    return df.dropna(subset=["Duration"])

# BOROUGH GRAPHS
df_total = pd.DataFrame()

for sheet in sheet_names:
    df = xls.parse(sheet)
    df = compute_duration(df)
    df = df[df["Permit Subtype"].isin(["MH", "BL"])]
    df_total = pd.concat([df_total, df], ignore_index=True)

    labels = custom_bins["MH"]["labels"]
    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, subtype in enumerate(["MH", "BL"]):
        df_sub = df[df["Permit Subtype"] == subtype].copy()
        bins = custom_bins[subtype]["bins"]
        dur_labels = custom_bins[subtype]["labels"]
        df_sub["Duration Category"] = pd.cut(df_sub["Duration"], bins=bins, labels=dur_labels)
        counts = df_sub["Duration Category"].value_counts().reindex(dur_labels).fillna(0)
        total = counts.sum()
        percentages = (counts / total * 100).round(1)

        offset = -width/2 if subtype == "MH" else width/2
        bars = ax.bar([pos + offset for pos in x], counts, width=width,
                      color=colors_borough[subtype], edgecolor="black", label=subtype)

        for bar, perc in zip(bars, percentages):
            if bar.get_height() > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f"{int(bar.get_height())} ({perc}%)", ha="center", fontsize=9)

    ax.set_title(f"{sheet.upper()} – Permit Durations by Building Height")
    ax.set_xlabel("Building Height Category")
    ax.set_ylabel("Number of Permits")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(title="Permit Type")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_ylim(0, None)

    plt.tight_layout()
    filename = f"{sheet}_grouped.png".replace(" ", "_")
    plt.savefig(os.path.join(dir_boroughs, filename))
    plt.close()

# NYC TOTAL GRAPH
fig, ax = plt.subplots(figsize=(10, 6))
labels = custom_bins["MH"]["labels"]
x = range(len(labels))
width = 0.35

for i, subtype in enumerate(["MH", "BL"]):
    df_sub = df_total[df_total["Permit Subtype"] == subtype].copy()
    bins = custom_bins[subtype]["bins"]
    dur_labels = custom_bins[subtype]["labels"]
    df_sub["Duration Category"] = pd.cut(df_sub["Duration"], bins=bins, labels=dur_labels)
    counts = df_sub["Duration Category"].value_counts().reindex(dur_labels).fillna(0)
    total = counts.sum()
    percentages = (counts / total * 100).round(1)

    offset = -width/2 if subtype == "MH" else width/2
    bars = ax.bar([pos + offset for pos in x], counts, width=width,
                  color=colors_nyc[subtype], edgecolor="black", label=subtype)

    for bar, perc in zip(bars, percentages):
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{int(bar.get_height())} ({perc}%)", ha="center", fontsize=9)

ax.set_title("NYC Total – Permit Durations by Building Height")
ax.set_xlabel("Building Height Category")
ax.set_ylabel("Number of Permits")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(title="Permit Type")
ax.grid(axis="y", linestyle="--", alpha=0.6)
ax.set_ylim(0, None)

plt.tight_layout()
plt.savefig(os.path.join(dir_total, "NYC_grouped.png"))
plt.close()

print("Charts saved:")
print(f"- Boroughs (5 grouped): {os.path.abspath(dir_boroughs)}")
print(f"- NYC Total (1 combined): {os.path.abspath(dir_total)}")
