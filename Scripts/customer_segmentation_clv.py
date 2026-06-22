import pandas as pd
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "Data" / "Raw" / "Online Retail.xlsx"
PROCESSED_DIR = BASE_DIR / "Data" / "Processed"
OUTPUT_DIR = BASE_DIR / "Output"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_excel(RAW_FILE)

# -----------------------------
# Clean data
# -----------------------------
df = df.dropna(subset=["CustomerID"])
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]  # remove cancelled invoices
df = df[df["Quantity"] > 0]
df = df[df["UnitPrice"] > 0]

df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["TotalSales"] = df["Quantity"] * df["UnitPrice"]

# -----------------------------
# RFM calculation
# -----------------------------
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("TotalSales", "sum"),
    FirstPurchase=("InvoiceDate", "min"),
    LastPurchase=("InvoiceDate", "max"),
    Country=("Country", lambda x: x.mode()[0])
).reset_index()

rfm["AvgOrderValue"] = rfm["Monetary"] / rfm["Frequency"]
rfm["CustomerLifespanDays"] = (rfm["LastPurchase"] - rfm["FirstPurchase"]).dt.days + 1
rfm["OrdersPerMonth"] = rfm["Frequency"] / (rfm["CustomerLifespanDays"] / 30)

# Use customer age from first purchase to the dataset snapshot date.
# This avoids over-inflating one-time customers who purchased within a short period.
rfm["CustomerAgeDays"] = (snapshot_date - rfm["FirstPurchase"]).dt.days

# Stabilize very new customers so short tenure does not create unrealistic annualized value.
rfm["CustomerAgeDaysAdjusted"] = rfm["CustomerAgeDays"].clip(lower=90)

rfm["OrdersPerYear"] = rfm["Frequency"] / (rfm["CustomerAgeDaysAdjusted"] / 365)

rfm["EstimatedAnnualCLV"] = rfm["AvgOrderValue"] * rfm["OrdersPerYear"]

# -----------------------------
# RFM scores
# -----------------------------
rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

# -----------------------------
# Customer segments
# -----------------------------
def assign_segment(row):
    if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
        return "Champions"
    elif row["F_Score"] >= 4 and row["M_Score"] >= 3:
        return "Loyal Customers"
    elif row["R_Score"] >= 4 and row["F_Score"] >= 2:
        return "Potential Loyalists"
    elif row["R_Score"] >= 4 and row["F_Score"] <= 2:
        return "New Customers"
    elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
        return "At Risk"
    elif row["R_Score"] <= 2 and row["F_Score"] <= 2:
        return "Lost Customers"
    else:
        return "Need Attention"

rfm["CustomerSegment"] = rfm.apply(assign_segment, axis=1)

# -----------------------------
# Summary outputs
# -----------------------------
segment_summary = rfm.groupby("CustomerSegment").agg(
    CustomerCount=("CustomerID", "count"),
    TotalRevenue=("Monetary", "sum"),
    AvgRevenuePerCustomer=("Monetary", "mean"),
    AvgCLV=("EstimatedAnnualCLV", "mean"),
    AvgRecency=("Recency", "mean"),
    AvgFrequency=("Frequency", "mean")
).reset_index()

monthly_revenue = df.groupby(pd.Grouper(key="InvoiceDate", freq="ME")).agg(
    Revenue=("TotalSales", "sum"),
    Orders=("InvoiceNo", "nunique"),
    Customers=("CustomerID", "nunique")
).reset_index()

country_summary = df.groupby("Country").agg(
    Revenue=("TotalSales", "sum"),
    Orders=("InvoiceNo", "nunique"),
    Customers=("CustomerID", "nunique")
).reset_index()

top_products = df.groupby("Description").agg(
    Revenue=("TotalSales", "sum"),
    QuantitySold=("Quantity", "sum"),
    Orders=("InvoiceNo", "nunique")
).reset_index().sort_values("Revenue", ascending=False).head(20)

# -----------------------------
# Export files
# -----------------------------
df.to_csv(PROCESSED_DIR / "cleaned_transactions.csv", index=False)
rfm.to_csv(OUTPUT_DIR / "customer_rfm.csv", index=False)
segment_summary.to_csv(OUTPUT_DIR / "segment_summary.csv", index=False)
monthly_revenue.to_csv(OUTPUT_DIR / "monthly_revenue.csv", index=False)
country_summary.to_csv(OUTPUT_DIR / "country_summary.csv", index=False)
top_products.to_csv(OUTPUT_DIR / "top_products.csv", index=False)

print("Customer Segmentation & CLV data preparation complete.")
print(f"Cleaned transactions: {len(df):,}")
print(f"Customers analyzed: {len(rfm):,}")
print(f"Outputs saved to: {OUTPUT_DIR}")