# 🎯 AI Risk Prediction System

A comprehensive machine learning application for predicting payment delays, loan defaults, and fraud detection using Streamlit.

## 📊 Features

### 1. **Synthetic AI Dataset Model**
- Payment delay probability prediction
- Predicted delay days estimation
- Risk tier classification (LOW → MEDIUM → HIGH → CRITICAL)
- Actionable business recommendations

**Inputs:**
- Average/Max/Std Dev of delay days
- On-time payment rate
- Transaction value and count
- Credit days and outstanding amounts

### 2. **LendingClub Dataset Model**
- **Acceptance Prediction**: Loan approval probability
- **Default Risk**: Probability of loan default
- **Delay Risk**: Probability of payment delays
- **Fraud Detection**: Anomaly score and fraud likelihood
- **Composite Risk Score**: Weighted combination of all risks

**Inputs:**
- Loan amount and interest rate
- Debt-to-income ratio
- Employment length
- Credit history and delinquencies
- Account information

## 🚀 Quick Start

### Local Development (5 seconds)

```bash
# Navigate to project folder
cd frontend

# Run the app
streamlit run streamlit_app.py
```

App opens automatically at `http://localhost:8501`

### Production Deployment (30 seconds)

**See `STREAMLIT_DEPLOYMENT.md` for detailed instructions**

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Select repository and file
4. Click deploy
5. Live in 30-60 seconds at `https://your-repo.streamlit.app`

## 📁 Project Structure

```
frontend/
├── streamlit_app.py              # Main application
├── streamlit_requirements.txt     # Python dependencies
├── STREAMLIT_DEPLOYMENT.md       # Deployment guide
├── run_streamlit.sh              # Quick start script
├── .streamlit/
│   └── config.toml               # Streamlit configuration
└── models/
    ├── synthetic_ai/
    │   ├── rf_delay_probability.pkl    (1 MB)
    │   └── rf_delay_days.pkl           (28 MB)
    └── lending_club/
        ├── acceptance_model_v1.0.joblib    (348 KB)
        ├── default_model_v1.0.joblib       (436 KB)
        ├── delay_model_v1.0.joblib         (434 KB)
        └── fraud_model_v1.0.joblib         (1.2 MB)
```

## 🔧 Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python with Flask models
- **ML Libraries**: scikit-learn, pandas, numpy, joblib
- **Deployment**: Streamlit Cloud (free) or self-hosted
- **Total Model Size**: 31.4 MB

## 📈 Performance

| Metric | Value |
|--------|-------|
| Synthetic AI Prediction | ~50ms |
| LendingClub Prediction | ~100ms |
| Page Load Time | ~2s (first load includes caching) |
| Model Load Time | ~5-10s (cached after first load) |
| Free Tier Concurrent Users | 3 |

## ✨ Model Features Explained

### Synthetic AI Model
- **Delay Probability**: Percentage chance payment will be late
- **Predicted Days**: Expected number of days delayed
- **Risk Score**: Composite 0-100 score
- **Risk Tier**: Business-friendly categorization
- **Recommendation**: Actionable guidance for credit decisions

### LendingClub Models

**Acceptance Model:**
- Predicts likelihood loan application will be approved
- Helps screen potential loans before processing

**Default Model:**
- Probability borrower will default (not pay back)
- Risk levels: LOW (<15%), MEDIUM (15-30%), HIGH (>30%)

**Delay Model:**
- Probability of payment delays
- Risk levels: LOW (<10%), MEDIUM (10-25%), HIGH (>25%)

**Fraud Detection (Isolation Forest):**
- Anomaly scoring system
- Detects suspicious application patterns
- Risk levels based on outlier severity

**Composite Risk:**
- Weighted score: 40% default + 30% delay + 30% fraud
- Final decision: ACCEPT or REJECT

## 🎨 UI Components

### Model Selection
- Sidebar selector between two datasets
- Clear visual separation of models

### Input Forms
- Organized in 3-column layout
- Numeric inputs with sensible defaults
- Slider for percentage values
- Load sample data presets (Low/Medium/High risk)

### Results Display
- **Key Metrics**: Displayed as prominent cards
- **Recommendation**: Clear actionable guidance
- **Color Coding**: Green for low risk, red for high risk

## 🔐 Deployment Security

- Models are bundled with code (no external API calls)
- No data is sent to third-party services
- All processing happens on Streamlit servers
- Free HTTPS on Streamlit Cloud

## 📦 Dependencies

```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.23.0
joblib>=1.3.0
scikit-learn>=1.3.0
```

Install with:
```bash
pip install -r streamlit_requirements.txt
```

## 🐛 Troubleshooting

### Q: Models not loading?
**A:** Check logs in Streamlit Cloud dashboard → app settings → Logs

### Q: App running slowly?
**A:** Normal on first load (models cached after). Subsequent predictions are instant.

### Q: Can I customize the UI?
**A:** Yes! Edit colors in `.streamlit/config.toml` or modify HTML/CSS in `streamlit_app.py`

### Q: How many users can it handle?
**A:** Free tier = 3 concurrent users. Upgrade to Pro/Business for more.

## 📚 API Documentation

If you want to use as backend API instead of UI:

```python
# Load models
models = load_models()

# Synthetic AI prediction
data = {
    'avg_delay_days': 5,
    'max_delay_days': 20,
    'std_delay_days': 3,
    # ... more fields
}
results = predict_synthetic_ai(models, data)

# LendingClub prediction
data = {
    'loan_amnt': 15000,
    'dti': 20,
    'int_rate': 12,
    # ... more fields
}
results = predict_lending_club(models, data)
```

## 🤝 Contributing

To add features:
1. Modify `streamlit_app.py`
2. Test locally with `streamlit run streamlit_app.py`
3. Commit and push
4. Streamlit auto-deploys

## 📝 License

This project is proprietary. All rights reserved.

## 🎓 Model Information

**Synthetic AI Models:**
- Type: Random Forest (Classification + Regression)
- Classes: Binary (will delay / won't delay)
- Features: 11 (transaction patterns and credit behavior)

**LendingClub Models:**
- Acceptance: Random Forest
- Default: Random Forest / Gradient Boosting ensemble
- Delay: XGBoost / Neural Network
- Fraud: Isolation Forest

## 📞 Support

For issues:
1. Check Streamlit Cloud logs
2. Review STREAMLIT_DEPLOYMENT.md
3. Test locally first with `streamlit run streamlit_app.py`

---

**Created:** 2024  
**Framework:** Streamlit 1.28+  
**Python:** 3.8+
