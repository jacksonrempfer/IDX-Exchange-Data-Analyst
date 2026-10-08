from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "week1"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "week2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Week 1 Residential datasets
sold = pd.read_csv(DATA_DIR / "sold_residential.csv", low_memory=False)
listed = pd.read_csv(DATA_DIR / "listings_residential.csv", low_memory=False)

# Numeric fields to analyze
numeric_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

# Analyze sold and listing datasets
for name, df in [("sold", sold), ("listed", listed)]:

    print(f"\n{name.upper()} DATASET")

    # Dataset understanding
    print("\nRows and columns:", df.shape)
    print("\nFirst five rows:")
    print(df.head())
    print("\nColumn data types:")
    print(df.dtypes)

    # Check property types and confirm Residential filter
    print("\nProperty types:")
    print(df["PropertyType"].unique())

    df = df[df["PropertyType"] == "Residential"].copy()

    # Separate market analysis fields from other fields
    market_fields = [col for col in numeric_fields if col in df.columns]
    other_fields = [col for col in df.columns if col not in market_fields]

    print("\nMarket analysis fields:")
    print(market_fields)
    print("\nOther fields to review (including metadata):")
    print(other_fields)

    # Missing value analysis
    missing = pd.DataFrame({
        "Missing Count": df.isnull().sum(),
        "Missing Percent": df.isnull().mean() * 100
    })

    missing["Above 90% Missing"] = missing["Missing Percent"] > 90
    missing = missing.sort_values("Missing Percent", ascending=False)

    print("\nMissing value report:")
    print(missing)

    print("\nColumns above 90% missing:")
    print(missing[missing["Above 90% Missing"]])

    missing.to_csv(OUTPUT_DIR / f"{name}_missing_report.csv")

    # Drop BusinessType because it is not needed
    # for this Residential market analysis
    df = df.drop(columns=["BusinessType"], errors="ignore")

    # Numeric distribution review
    numeric = df[market_fields].apply(pd.to_numeric, errors="coerce")

    summary = numeric.describe(
        percentiles=[0.01, 0.25, 0.50, 0.75, 0.95, 0.99]
    ).T

    print("\nNumeric distribution summary:")
    print(summary)

    summary.to_csv(OUTPUT_DIR / f"{name}_numeric_summary.csv")

    # Histograms and boxplots
    for col in market_fields:

        plt.figure()
        numeric[col].hist(bins=30)
        plt.title(f"{name} - {col} Histogram")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.savefig(OUTPUT_DIR / f"{name}_{col}_histogram.png")
        plt.close()

        plt.figure()
        numeric[[col]].boxplot()
        plt.title(f"{name} - {col} Boxplot")
        plt.savefig(OUTPUT_DIR / f"{name}_{col}_boxplot.png")
        plt.close()

    # Save Week 2 Residential dataset
    df.to_csv(OUTPUT_DIR / f"{name}_residential.csv", index=False)
