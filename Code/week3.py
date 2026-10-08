from pathlib import Path
import pandas as pd

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "week2"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "week3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Week 2 datasets
sold = pd.read_csv(DATA_DIR / "sold_residential.csv", low_memory=False)
listings = pd.read_csv(DATA_DIR / "listed_residential.csv", low_memory=False)

# Fetch mortgage rate data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]

# Resample weekly rates to monthly averages
mortgage["rate_30yr_fixed"] = pd.to_numeric(
    mortgage["rate_30yr_fixed"], errors="coerce"
)

mortgage["year_month"] = mortgage["date"].dt.to_period("M")

mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)

# Create matching year_month keys
# Sold dataset uses CloseDate
sold["year_month"] = pd.to_datetime(
    sold["CloseDate"], errors="coerce"
).dt.to_period("M")

# Listings dataset uses ListingContractDate
listings["year_month"] = pd.to_datetime(
    listings["ListingContractDate"], errors="coerce"
).dt.to_period("M")

# Merge monthly mortgage rates
sold_with_rates = sold.merge(
    mortgage_monthly, on="year_month", how="left"
)

listings_with_rates = listings.merge(
    mortgage_monthly, on="year_month", how="left"
)

# Validate the merge
print("Sold rows:", len(sold_with_rates))
print("Listings rows:", len(listings_with_rates))

print("Sold missing mortgage rates:",
      sold_with_rates["rate_30yr_fixed"].isnull().sum())

print("Listings missing mortgage rates:",
      listings_with_rates["rate_30yr_fixed"].isnull().sum())

# Preview
print("\nSold data preview:")
print(
    sold_with_rates[
        ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
    ].head()
)

print("\nListings data preview:")
print(
    listings_with_rates[
        ["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]
    ].head()
)

# Save enriched datasets
sold_with_rates.to_csv(
    OUTPUT_DIR / "sold_with_mortgage_rates.csv", index=False
)

listings_with_rates.to_csv(
    OUTPUT_DIR / "listings_with_mortgage_rates.csv", index=False
)
