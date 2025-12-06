import json
import pandas as pd
import numpy as np

def compute_party_features(json_path, output_csv="party_features.csv"):
    # -----------------------------------------
    # 1. LOAD JSON
    # -----------------------------------------
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # -----------------------------------------
    # 2. CLEAN & CONVERT TYPES
    # -----------------------------------------
    date_cols = ["InvoiceDate", "PaymentDate", "PaymentReceiptDate", "DueDate"]
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    num_cols = ["Amount", "CreditDays", "DaysInPayment", "OutstandingAmount"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Use only settled invoices for delay calculations
    settled_df = df.dropna(subset=["DaysInPayment"])

    # -----------------------------------------
    # 3. AGGREGATE ENGINEERED FEATURES
    # -----------------------------------------
    party_stats = settled_df.groupby("PartyName").agg(
        avg_delay_days=("DaysInPayment", "mean"),
        max_delay_days=("DaysInPayment", "max"),
        std_delay_days=("DaysInPayment", "std"),
        delayed_count=("IsDelayed", "sum"),
        total_txn=("IsDelayed", "count"),
        total_value=("Amount", "sum"),
        avg_credit_days=("CreditDays", "mean")
    ).reset_index()

    # Replace NaN std dev with 0
    party_stats["std_delay_days"] = party_stats["std_delay_days"].fillna(0)

    # On-time rate
    party_stats["on_time_rate"] = 1 - (party_stats["delayed_count"] / party_stats["total_txn"])

    # -----------------------------------------
    # 4. ADD REGRESSOR FEATURES
    # -----------------------------------------
    party_stats["CreditDays"] = party_stats["avg_credit_days"]

    # Average amount per settled invoice
    party_stats["Amount"] = party_stats["total_value"] / party_stats["total_txn"]

    # Set outstanding to 0 for feature consistency
    party_stats["OutstandingAmount"] = 0

    # -----------------------------------------
    # 5. SAVE TO CSV
    # -----------------------------------------
    party_stats.to_csv(output_csv, index=False)
    print(f"✅ Features calculated and saved to: {output_csv}")

    return party_stats


# Run directly
if __name__ == "__main__":
    compute_party_features("/home/sury/proj/solviser/solviser/solve/pythonTry1/AI.json")
