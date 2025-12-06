# 📤 CSV/JSON Upload Feature for Synthetic AI Model

## Overview

The Streamlit app now supports **batch risk analysis** for the Synthetic AI Dataset model. You can upload CSV or JSON files with transaction data, and the app will automatically:

1. **Parse the transaction data**
2. **Calculate aggregate features** per party/company
3. **Run risk predictions** using ML models
4. **Display results** in an interactive table
5. **Export results** as CSV

## Input File Format

### Required Columns

Your CSV or JSON file must include the following columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `TransactionType` | string | Type of transaction | "Sales", "Receipt", "Purchase", "Payment" |
| `PartyName` | string | Name of the company/party | "Aarav Traders" |
| `Amount` | numeric | Transaction amount | 55000.00 |
| `CreditDays` | numeric | Credit term in days | 30 |
| `DaysInPayment` | numeric | Actual days taken to pay (can be negative for early payment) | 5 |
| `IsDelayed` | boolean | Whether payment was delayed | true/false |
| `InvoiceDate` | date | Invoice date (optional but recommended) | "2024-01-01" |
| `PaymentDate` | date | Payment date (optional but recommended) | "2024-01-31" |
| `OutstandingAmount` | numeric | Outstanding balance (optional) | 0.00 |

### JSON Format Example

```json
[
  {
    "TransactionType": "Sales",
    "PartyName": "Company A",
    "GSTNo": "27AARTR1234A1Z5",
    "InvoiceNo": "INV/S/24/0001",
    "InvoiceDate": "2024-01-01",
    "Amount": 55000.00,
    "CreditDays": 30,
    "DueDate": "2024-01-31",
    "PaymentDate": "2024-01-31",
    "DaysInPayment": 0,
    "IsDelayed": false,
    "OutstandingAmount": 0.00
  },
  {
    "TransactionType": "Receipt",
    "PartyName": "Company B",
    "Amount": 25000.00,
    "CreditDays": 15,
    "DaysInPayment": 5,
    "IsDelayed": true,
    "OutstandingAmount": 0.00
  }
]
```

### CSV Format Example

```csv
TransactionType,PartyName,Amount,CreditDays,DaysInPayment,IsDelayed,OutstandingAmount
Sales,Company A,55000.00,30,0,false,0.00
Receipt,Company B,25000.00,15,5,true,0.00
Purchase,Company C,80000.00,45,-4,false,0.00
```

## How to Use

### Step 1: Prepare Your Data

Make sure your CSV/JSON file has the required columns listed above. Other columns (GSTNo, InvoiceNo, etc.) are optional and will be ignored.

### Step 2: Upload File

1. Open the Streamlit app
2. Select **"Synthetic AI Dataset"** model
3. Choose **"📤 Upload CSV/JSON File"** as input mode
4. Click **"Choose a file"** and select your CSV or JSON file

### Step 3: Preview Data

The app will display:
- ✅ File loaded successfully message
- 📊 Preview of first 5 rows
- Total number of transactions

### Step 4: Generate Predictions

1. Click **"🚀 Generate Risk Analysis"** button
2. Wait for processing (typically 2-5 seconds)
3. View results table

### Step 5: Analyze Results

Results include for each party:

| Column | Description |
|--------|-------------|
| `PartyName` | Company name |
| `Delay_Probability` | % chance of payment delay (0-100) |
| `Expected_Delay_Days` | Predicted number of days delay will occur |
| `Risk_Score` | Composite risk score (0-100) |
| `Risk_Tier` | LOW / MEDIUM / HIGH / CRITICAL |
| `Recommendation` | Action recommendation |

### Step 6: Download Results

Click **"📥 Download Results as CSV"** to export analysis results.

## Feature Calculation

The app automatically calculates the following **party-level features** from transaction data:

### From Raw Transactions

```
avg_delay_days = mean(DaysInPayment)
max_delay_days = max(DaysInPayment)
std_delay_days = std(DaysInPayment)
delayed_count = sum(IsDelayed == true)
total_txn = count(transactions)
total_value = sum(Amount)
avg_credit_days = mean(CreditDays)
```

### Derived Features

```
on_time_rate = 1 - (delayed_count / total_txn)
Amount = total_value / total_txn
CreditDays = avg_credit_days
OutstandingAmount = 0 (default)
```

## Risk Tier Explanation

### Risk Score Calculation
```
Risk_Score = (Delay_Probability × 0.6) + (Normalized_Delay_Days × 0.4)
```

### Risk Tiers

| Tier | Score Range | Description | Action |
|------|-------------|-------------|--------|
| **LOW** | 0-25 | Minimal delay risk | ✅ Proceed with normal credit terms |
| **MEDIUM** | 25-50 | Moderate delay risk | ✓ Standard terms with monitoring |
| **HIGH** | 50-75 | Elevated delay risk | ⚠️ Reduce credit terms, monitor closely |
| **CRITICAL** | 75-100 | High default/delay risk | ⚠️ Require advance payment or collateral |

## Summary Statistics

After generation, the app displays:

- **Total Parties**: Number of companies analyzed
- **High Risk Count**: Companies in HIGH or CRITICAL tier
- **Avg Risk Score**: Average risk across all companies
- **Likely to Delay**: Companies with >50% delay probability

## Examples

### Example 1: Reliable Supplier (Low Risk)
```
Delay_Probability: 5%
Expected_Delay_Days: 0.5
Risk_Score: 12.5
Risk_Tier: LOW
→ Recommendation: Proceed with normal credit terms
```

### Example 2: Moderate Risk Customer
```
Delay_Probability: 35%
Expected_Delay_Days: 8
Risk_Score: 45.2
Risk_Tier: MEDIUM
→ Recommendation: Standard terms with monitoring
```

### Example 3: High Risk Account
```
Delay_Probability: 65%
Expected_Delay_Days: 15
Risk_Score: 67.5
Risk_Tier: HIGH
→ Recommendation: Reduce credit terms, monitor closely
```

## Troubleshooting

### Error: "PartyName not found in file"
**Solution**: Make sure your file has a `PartyName` column. It can be spelled as:
- `PartyName`
- `Party`
- `Company`
- `Customer`

### Error: "DaysInPayment column not found"
**Solution**: This column is required. Calculate it as:
```
DaysInPayment = PaymentDate - DueDate
```
(in days, negative = early payment, positive = late payment)

### All companies showing LOW risk
**Possible causes**:
- Dataset has very reliable payment history
- DaysInPayment values are all near 0
- Transaction data is too recent (not enough history)

**Solution**: Check raw data and verify payment patterns

### Error during upload
**Try**:
1. Verify file format (CSV or JSON only)
2. Check for special characters in column names
3. Ensure no empty rows
4. Verify numeric columns don't contain text

## Performance

| Data Size | Time | Notes |
|-----------|------|-------|
| 10 parties | <1s | Instant |
| 50 parties | 1-2s | Very fast |
| 100 parties | 2-3s | Fast |
| 500 parties | 5-10s | Moderate |
| 1000+ parties | 10-30s | Slower but scalable |

## Tips & Best Practices

✅ **Do**:
- Include multiple transactions per party (minimum 5 recommended)
- Ensure DaysInPayment is numeric (not text)
- Include both early payments and late payments
- Use consistent date formats

❌ **Don't**:
- Mix currency formats (use same currency)
- Include headers as data rows
- Leave required columns empty
- Use special characters in PartyName

## Batch Processing Workflow

```
1. Prepare CSV/JSON → 2. Upload File → 3. Preview Data → 
4. Generate Predictions → 5. View Results → 6. Download CSV
```

## API Integration

If building a custom integration:

```python
from streamlit_app import process_synthetic_json_from_df, generate_bulk_predictions

# Load your data
df = pd.read_csv('transactions.csv')

# Process features
party_stats = process_synthetic_json_from_df(df)

# Generate predictions
results = generate_bulk_predictions(models, party_stats)

# Export
results.to_csv('risk_analysis.csv', index=False)
```

---

**Last Updated**: December 6, 2025
**Feature**: Batch Risk Analysis with CSV/JSON Upload
**Supported Formats**: CSV, JSON
**Max File Size**: 50 MB (typical)
