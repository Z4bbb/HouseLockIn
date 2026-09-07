import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dotenv import load_dotenv
import pyfredapi as pf

# -----------------------------------------------------------------------------
# 1. Load Credentials & Fetch Data
# -----------------------------------------------------------------------------
load_dotenv()

api_key = os.getenv("FRED_API_KEY")
if not api_key:
    raise ValueError("FRED_API_KEY is missing. Check your .env file.")

print("Connecting to FRED API...")

# Series IDs:
# - MORTGAGE30US: 30-Year Fixed Rate Mortgage Average (Weekly)
# - EXHOSLUSM495S: Existing Home Sales (Monthly, SAAR)
# - CSUSHPISA: S&P/Case-Shiller U.S. National Home Price Index (Monthly)
series_ids = ["MORTGAGE30US", "EXHOSLUSM495S", "CSUSHPISA"]

print("\n--- Data Verification Check ---")
for series in series_ids:
    # Pull the metadata for each series
    info = pf.get_series_info(series_id=series, api_key=api_key)
    
    # Print the title, frequency, and units to prove data provenance
    print(f"ID: {series}")
    print(f"Title: {info.title}")
    print(f"Frequency: {info.frequency}")
    print(f"Units: {info.units}\n")

# Fetch the actual time-series data
df_mortgage = pf.get_series(series_id="MORTGAGE30US", api_key=api_key)
df_sales = pf.get_series(series_id="EXHOSLUSM495S", api_key=api_key)
df_prices = pf.get_series(series_id="CSUSHPISA", api_key=api_key)

print("\n--- Sanity Checks (Exploratory Data Analysis) ---")
print("Mortgage Data Summary:\n", df_mortgage.describe(), "\n")
print("Sales Data Summary:\n", df_sales.describe(), "\n")
print("Prices Data Summary:\n", df_prices.describe(), "\n")

# -----------------------------------------------------------------------------
# 2. Data Cleaning & Alignment
# -----------------------------------------------------------------------------
# Standardize column names
df_mortgage = df_mortgage.rename(columns={"date": "DATE", "value": "Mortgage_Rate_30Y"})
df_sales = df_sales.rename(columns={"date": "DATE", "value": "Existing_Home_Sales_M"})
df_prices = df_prices.rename(columns={"date": "DATE", "value": "Case_Shiller_Index"})

# Format indices and explicitly enforce numeric typing
for df in [df_mortgage, df_sales, df_prices]:
    df["DATE"] = pd.to_datetime(df["DATE"])
    df.set_index("DATE", inplace=True)
    
    # Safely convert the target column to numeric to prevent resampling errors
    col_name = df.columns[0]
    df[col_name] = pd.to_numeric(df[col_name], errors="coerce")

# Resample weekly mortgage rate to monthly average to align reporting intervals
df_mortgage_m = df_mortgage.resample("MS").mean()
df_sales_m = df_sales.resample("MS").last()
df_prices_m = df_prices.resample("MS").last()

# Combine into a unified dataset and slice the target window (2018–Present)
df_combined = pd.concat([df_mortgage_m, df_sales_m, df_prices_m], axis=1)
df_story = df_combined.loc["2018-01-01":].copy().dropna(how="all")

# Save processed dataset locally
csv_filename = "housing_lockin_dataset.csv"
df_story.to_csv(csv_filename)
print(f"Data processed and saved to '{csv_filename}'")

# -----------------------------------------------------------------------------
# 3. Chart Generation
# -----------------------------------------------------------------------------
plt.style.use("fivethirtyeight")
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["axes.facecolor"] = "#FFFFFF"
plt.rcParams["figure.facecolor"] = "#FFFFFF"
plt.rcParams["savefig.facecolor"] = "#FFFFFF"

# Chart 1: The Cost of Borrowing Explodes
fig1, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
ax1.plot(df_story.index, df_story["Mortgage_Rate_30Y"], color="#D9381E", linewidth=2.5, label="30-Year Fixed Mortgage Rate (%)")
ax1.axhline(y=3.0, color="gray", linestyle=":", alpha=0.7, label="Sub-3% Era")
ax1.set_title("Chart 1: The Cost of Borrowing Explodes (2018–Present)", fontsize=13, fontweight="bold", pad=15)
ax1.set_ylabel("Mortgage Rate (%)", fontsize=11)
ax1.legend(frameon=True, facecolor="white", loc="upper left")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
fig1.tight_layout()
fig1.savefig("chart1_rate_shock.png")
plt.close(fig1)
print("Generated: chart1_rate_shock.png")

# Chart 2: Supply Freeze
fig2, ax2 = plt.subplots(figsize=(10, 5), dpi=300)
ax2.fill_between(df_story.index, df_story["Existing_Home_Sales_M"], color="#2B5B84", alpha=0.3)
ax2.plot(df_story.index, df_story["Existing_Home_Sales_M"], color="#2B5B84", linewidth=2, label="Existing Home Sales (Millions)")
ax2.set_title("Chart 2: The Lock-in Effect Freezes Market Volume", fontsize=13, fontweight="bold", pad=15)
ax2.set_ylabel("Sales Volume (Millions, SAAR)", fontsize=11)
ax2.legend(frameon=True, facecolor="white", loc="lower left")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
fig2.tight_layout()
fig2.savefig("chart2_supply_freeze.png")
plt.close(fig2)
print("Generated: chart2_supply_freeze.png")

# Chart 3: The Price Paradox
fig3, ax3 = plt.subplots(figsize=(10, 5), dpi=300)
ax3.plot(df_story.index, df_story["Case_Shiller_Index"], color="#1B8A5A", linewidth=2.5, label="Case-Shiller Home Price Index")
ax3.axvline(pd.to_datetime("2022-03-01"), color="#D9381E", linestyle="--", alpha=0.8, label="Fed Rate Hikes Begin")
ax3.set_title("Chart 3: The Paradox — Home Prices Reach New Highs", fontsize=13, fontweight="bold", pad=15)
ax3.set_ylabel("Price Index (Jan 2000 = 100)", fontsize=11)
ax3.legend(frameon=True, facecolor="white", loc="upper left")
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
fig3.tight_layout()
fig3.savefig("chart3_price_paradox.png")
plt.close(fig3)
print("Generated: chart3_price_paradox.png")

print("\nPipeline run complete. All outputs saved in current directory.")