import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# File path 
input_path = r"C:\Users\aless\OneDrive\Desktop\py\PROJECT_cleaned.xlsx"
xls = pd.ExcelFile(input_path)
sheet_names = xls.sheet_names

# Output directory
output_dir = r"C:\Users\aless\OneDrive\Desktop\py\duration_paragone_final"
os.makedirs(output_dir, exist_ok=True)

# Colors for boroughs (light)
colors_borough = {
    "MH_obs": "#87CEFA",  # light blue
    "BL_obs": "#FF9999",  # light red
    "Expected": "#90EE90"  # light green
}

# Colors for NYC (dark)
colors_nyc = {
    "MH_obs": "#1E90FF",  # dark blue
    "BL_obs": "#B22222",  # dark red
    "Expected": "#90EE90"  # light green
}

# Expected values by building height
expected = {
    'Manhattan': {'3–5 floors': 47.0, '6–10 floors': 29.5, '11–15 floors': 6.0, '>15 floors': 17.5},
    'Brooklyn': {'3–5 floors': 69.0, '6–10 floors': 23.0, '11–15 floors': 7.0, '>15 floors': 1.0},
    'Queens': {'3–5 floors': 76.0, '6–10 floors': 19.0, '11–15 floors': 4.0, '>15 floors': 1.0},
    'Bronx': {'3–5 floors': 59.0, '6–10 floors': 32.0, '11–15 floors': 7.0, '>15 floors': 2.0},
    'Staten Island': {'3–5 floors': 89.0, '6–10 floors': 9.0, '11–15 floors': 2.0, '>15 floors': 0.0}
}

labels = ["3–5 floors", "6–10 floors", "11–15 floors", ">15 floors"]
width = 0.2

# Duration categorization
def get_categoria(d, tipo):
    if tipo == "BL":
        if d <= 60:
            return "3–5 floors"
        elif d <= 120:
            return "6–10 floors"
        elif d <= 179:
            return "11–15 floors"
        else:
            return ">15 floors"
    elif tipo == "MH":
        if d <= 120:
            return "3–5 floors"
        elif d <= 180:
            return "6–10 floors"
        elif d <= 269:
            return "11–15 floors"
        else:
            return ">15 floors"
    return None

# Borough comparison plots
for sheet in sheet_names:
    borough = next((b for b in expected if b.lower() == sheet.lower()), None)
    if borough is None:
        continue

    df = xls.parse(sheet)
    df = df.dropna(subset=["Permit Subtype", "Duration"])
    df["Permit Subtype"] = df["Permit Subtype"].str.strip()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(labels))
    observed = {}

    for tipo in ["MH", "BL"]:
        df_tipo = df[df["Permit Subtype"] == tipo].copy()
        df_tipo["Category"] = df_tipo["Duration"].apply(lambda x: get_categoria(x, tipo))
        obs = df_tipo["Category"].value_counts(normalize=True).reindex(labels).fillna(0) * 100
        observed[f"{tipo}_obs"] = obs

    expected_vals = [expected[borough].get(label, 0) for label in labels]
    offsets = [-width, 0, width]
    keys = ["MH_obs", "BL_obs", "Expected"]
    data_sources = [observed["MH_obs"], observed["BL_obs"], expected_vals]

    for i, key in enumerate(keys):
        vals = data_sources[i]
        bars = ax.bar(x + offsets[i], vals, width=width,
                      color=colors_borough[key], edgecolor="black",
                      alpha=1 if key != "Expected" else 0.6,
                      hatch="//" if key == "Expected" else "",
                      label=key.replace("_", " ").upper())

        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f"{val:.1f}%", ha="center", fontsize=9)

    ax.set_title(f"{borough.upper()} – Observed vs Expected Permit Durations by Height")
    ax.set_ylabel("Permit Share (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.legend(ncol=3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{borough.replace(' ', '_')}_grouped_comparison.png"))
    plt.close()

# NYC total comparison plot
df_all = pd.concat([xls.parse(s) for s in sheet_names])
df_all = df_all.dropna(subset=["Permit Subtype", "Duration"])
df_all["Permit Subtype"] = df_all["Permit Subtype"].str.strip()

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(labels))
observed = {}

for tipo in ["MH", "BL"]:
    df_tipo = df_all[df_all["Permit Subtype"] == tipo].copy()
    df_tipo["Category"] = df_tipo["Duration"].apply(lambda x: get_categoria(x, tipo))
    obs = df_tipo["Category"].value_counts(normalize=True).reindex(labels).fillna(0) * 100
    observed[f"{tipo}_obs"] = obs

# Average expected values across boroughs
media_expected = {}
for label in labels:
    vals = [expected[b].get(label, 0) for b in expected]
    media_expected[label] = sum(vals) / len(vals)

expected_vals = [media_expected[label] for label in labels]
offsets = [-width, 0, width]
keys = ["MH_obs", "BL_obs", "Expected"]
data_sources = [observed["MH_obs"], observed["BL_obs"], expected_vals]

for i, key in enumerate(keys):
    vals = data_sources[i]
    bars = ax.bar(x + offsets[i], vals, width=width,
                  color=colors_nyc[key], edgecolor="black",
                  alpha=1 if key != "Expected" else 0.6,
                  hatch="//" if key == "Expected" else "",
                  label=key.replace("_", " ").upper())

    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{val:.1f}%", ha="center", fontsize=9)

ax.set_title("NYC TOTAL – Observed vs Expected Permit Durations by Height")
ax.set_ylabel("Permit Share (%)")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.6)
ax.legend(ncol=3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "NYC_grouped_comparison.png"))
plt.close()

print("Updated charts saved in:", output_dir)
