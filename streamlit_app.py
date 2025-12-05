"""
Streamlit ML Risk Prediction App
Simplified version that combines frontend + backend in one file
Models are loaded automatically and efficiently
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import sys

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🎯 AI Risk Prediction System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .model-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .model-card:hover {
        transform: scale(1.05);
    }
    .result-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .result-card.high-risk {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# MODEL LOADING (Cached for efficiency)
# ============================================================================

@st.cache_resource
def load_models():
    """Load all models once and cache them"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    models = {
        'synthetic_ai': {
            'delay_probability': None,
            'delay_days': None,
            'loaded': False
        },
        'lending_club': {
            'acceptance': None,
            'default': None,
            'delay': None,
            'fraud': None,
            'loaded': False
        }
    }
    
    # Load Synthetic AI models
    synthetic_dir = os.path.join(BASE_DIR, 'models', 'synthetic_ai')
    try:
        clf_path = os.path.join(synthetic_dir, 'rf_delay_probability.pkl')
        if os.path.exists(clf_path):
            models['synthetic_ai']['delay_probability'] = joblib.load(clf_path)
        
        reg_path = os.path.join(synthetic_dir, 'rf_delay_days.pkl')
        if os.path.exists(reg_path):
            models['synthetic_ai']['delay_days'] = joblib.load(reg_path)
        
        models['synthetic_ai']['loaded'] = True
    except Exception as e:
        st.error(f"Error loading Synthetic AI models: {e}")
    
    # Load LendingClub models
    lending_dir = os.path.join(BASE_DIR, 'models', 'lending_club')
    try:
        for model_type in ['acceptance', 'default', 'delay', 'fraud']:
            model_path = os.path.join(lending_dir, f'{model_type}_model_v1.0.joblib')
            if os.path.exists(model_path):
                models['lending_club'][model_type] = joblib.load(model_path)
        
        models['lending_club']['loaded'] = True
    except Exception as e:
        st.error(f"Error loading LendingClub models: {e}")
    
    return models

# ============================================================================
# PREDICTION FUNCTIONS
# ============================================================================

def predict_synthetic_ai(models, data):
    """Predict payment delay using Synthetic AI models"""
    results = {}
    
    # Predict delay probability
    clf_package = models['synthetic_ai']['delay_probability']
    if clf_package:
        clf = clf_package['model']
        clf_features = clf_package['features']
        
        clf_data = {feat: data.get(feat, 0) for feat in clf_features}
        X_clf = pd.DataFrame([clf_data])
        
        delay_prob = clf.predict_proba(X_clf)[0, 1]
        results['delay_probability'] = round(float(delay_prob * 100), 2)
        results['will_delay'] = 'Yes' if delay_prob > 0.5 else 'No'
        results['delay_risk_level'] = (
            'HIGH' if delay_prob > 0.7 else
            'MEDIUM' if delay_prob > 0.4 else
            'LOW'
        )
    
    # Predict delay days
    reg_package = models['synthetic_ai']['delay_days']
    if reg_package:
        reg = reg_package['model']
        reg_features = reg_package['features']
        
        reg_data = {feat: data.get(feat, 0) for feat in reg_features}
        X_reg = pd.DataFrame([reg_data])
        
        predicted_days = reg.predict(X_reg)[0]
        results['predicted_delay_days'] = round(float(max(0, predicted_days)), 1)
    
    # Calculate risk score
    delay_prob = results.get('delay_probability', 0) / 100
    predicted_days = results.get('predicted_delay_days', 0)
    risk_score = (delay_prob * 60) + (min(predicted_days / 90, 1) * 40)
    results['risk_score'] = round(risk_score, 1)
    results['risk_tier'] = (
        'CRITICAL' if risk_score >= 75 else
        'HIGH' if risk_score >= 50 else
        'MEDIUM' if risk_score >= 25 else
        'LOW'
    )
    
    # Recommendation
    if results['risk_tier'] == 'CRITICAL':
        results['recommendation'] = "⚠️ HIGH RISK - Require advance payment or collateral"
    elif results['risk_tier'] == 'HIGH':
        results['recommendation'] = "⚠️ ELEVATED RISK - Reduce credit terms, monitor closely"
    elif results['risk_tier'] == 'MEDIUM':
        results['recommendation'] = "✓ MODERATE RISK - Standard terms with monitoring"
    else:
        results['recommendation'] = "✅ LOW RISK - Proceed with normal credit terms"
    
    return results

def predict_lending_club(models, data):
    """Predict loan risk using LendingClub models"""
    results = {}
    loan_df = pd.DataFrame([data])
    
    # Acceptance Prediction
    if models['lending_club']['acceptance']:
        pkg = models['lending_club']['acceptance']
        
        for feat in pkg['feature_names']:
            if feat not in loan_df.columns:
                loan_df[feat] = 0
        
        X = loan_df[pkg['feature_names']].fillna(0)
        X_scaled = pkg['scaler'].transform(X)
        
        acceptance_prob = pkg['model'].predict_proba(X_scaled)[0, 1]
        results['acceptance'] = {
            'probability': round(float(acceptance_prob * 100), 2),
            'decision': 'ACCEPT' if acceptance_prob >= 0.5 else 'REJECT',
            'confidence': round(float(abs(acceptance_prob - 0.5) * 200), 2)
        }
    
    # Default Prediction
    if models['lending_club']['default']:
        pkg = models['lending_club']['default']
        
        for feat in pkg['feature_names']:
            if feat not in loan_df.columns:
                loan_df[feat] = 0
        
        X = loan_df[pkg['feature_names']].fillna(0)
        X_scaled = pkg['scaler'].transform(X)
        
        default_prob = pkg['model'].predict_proba(X_scaled)[0, 1]
        results['default'] = {
            'probability': round(float(default_prob * 100), 2),
            'risk_level': 'HIGH' if default_prob > 0.3 else 'MEDIUM' if default_prob > 0.15 else 'LOW'
        }
    
    # Delay Prediction
    if models['lending_club']['delay']:
        pkg = models['lending_club']['delay']
        
        for feat in pkg['feature_names']:
            if feat not in loan_df.columns:
                loan_df[feat] = 0
        
        X = loan_df[pkg['feature_names']].fillna(0)
        X_scaled = pkg['scaler'].transform(X)
        
        delay_prob = pkg['model'].predict_proba(X_scaled)[0, 1]
        results['delay'] = {
            'probability': round(float(delay_prob * 100), 2),
            'risk_level': 'HIGH' if delay_prob > 0.25 else 'MEDIUM' if delay_prob > 0.1 else 'LOW'
        }
    
    # Fraud Detection
    if models['lending_club']['fraud']:
        pkg = models['lending_club']['fraud']
        
        for feat in pkg['feature_names']:
            if feat not in loan_df.columns:
                loan_df[feat] = 0
        
        X = loan_df[pkg['feature_names']].fillna(0)
        X_scaled = pkg['scaler'].transform(X)
        
        anomaly_score = pkg['model'].score_samples(X_scaled)[0]
        fraud_score = (1 - (anomaly_score - (-0.5)) / 0.5) * 100
        fraud_score = np.clip(fraud_score, 0, 100)
        
        results['fraud'] = {
            'score': round(float(fraud_score), 2),
            'risk_level': (
                'CRITICAL' if fraud_score > 75 else
                'HIGH' if fraud_score > 50 else
                'MEDIUM' if fraud_score > 25 else
                'LOW'
            ),
            'is_suspicious': 'Yes' if fraud_score > 60 else 'No'
        }
    
    # Composite Risk Score
    default_prob = results.get('default', {}).get('probability', 0) / 100
    delay_prob = results.get('delay', {}).get('probability', 0) / 100
    fraud_score = results.get('fraud', {}).get('score', 0) / 100
    
    composite_score = (
        0.40 * default_prob * 100 +
        0.30 * delay_prob * 100 +
        0.30 * fraud_score * 100
    )
    
    results['composite_risk'] = {
        'score': round(float(composite_score), 1),
        'tier': (
            'CRITICAL' if composite_score >= 75 else
            'HIGH' if composite_score >= 50 else
            'MEDIUM' if composite_score >= 25 else
            'LOW'
        )
    }
    
    return results

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Load models
    models = load_models()
    
    # Header
    st.markdown('<div class="main-header">🎯 AI Risk Prediction System</div>', unsafe_allow_html=True)
    st.markdown("Advanced machine learning models for comprehensive risk assessment")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        model_type = st.radio(
            "Select Prediction Model",
            options=['Synthetic AI Dataset', 'LendingClub Dataset'],
            index=0
        )
    
    # Main content
    if model_type == 'Synthetic AI Dataset':
        st.header("💼 Synthetic AI Dataset - Payment Delay Prediction")
        st.markdown("Payment delay prediction for companies based on historical transaction patterns")
        
        # Check if models are loaded
        if not models['synthetic_ai']['loaded']:
            st.error("❌ Models not loaded. Please check model files.")
            return
        
        # Input form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_delay_days = st.number_input("Average Delay Days", value=0.0, min_value=0.0)
            max_delay_days = st.number_input("Max Delay Days", value=15.0, min_value=0.0)
            std_delay_days = st.number_input("Std Dev Delay Days", value=3.0, min_value=0.0)
        
        with col2:
            on_time_rate = st.slider("On-Time Payment Rate", 0.0, 1.0, 0.8)
            total_value = st.number_input("Total Transaction Value ($)", value=100000.0, min_value=0.0)
            avg_credit_days = st.number_input("Avg Credit Days", value=30.0, min_value=0.0)
        
        with col3:
            delayed_count = st.number_input("Delayed Payments Count", value=0.0, min_value=0.0)
            total_txn = st.number_input("Total Transactions", value=10.0, min_value=1.0)
            credit_days = st.number_input("Current Credit Days", value=30.0, min_value=0.0)
            amount = st.number_input("Current Amount ($)", value=10000.0, min_value=0.0)
            outstanding = st.number_input("Outstanding Amount ($)", value=0.0, min_value=0.0)
        
        # Sample data presets
        if st.button("📊 Load Sample Data"):
            sample_choice = st.selectbox("Select Sample Profile", ["Low Risk", "Medium Risk", "High Risk"])
            
            if sample_choice == "Low Risk":
                avg_delay_days = 2.5
                max_delay_days = 15
                std_delay_days = 3.2
                on_time_rate = 0.95
            elif sample_choice == "Medium Risk":
                avg_delay_days = 8.5
                max_delay_days = 30
                std_delay_days = 6.8
                on_time_rate = 0.85
            else:
                avg_delay_days = 18.5
                max_delay_days = 60
                std_delay_days = 12.5
                on_time_rate = 0.65
        
        # Predict button
        if st.button("🚀 Get Prediction", type="primary"):
            input_data = {
                'avg_delay_days': avg_delay_days,
                'max_delay_days': max_delay_days,
                'std_delay_days': std_delay_days,
                'on_time_rate': on_time_rate,
                'total_value': total_value,
                'avg_credit_days': avg_credit_days,
                'delayed_count': delayed_count,
                'total_txn': total_txn,
                'CreditDays': credit_days,
                'Amount': amount,
                'OutstandingAmount': outstanding
            }
            
            results = predict_synthetic_ai(models, input_data)
            
            # Display results
            st.subheader("📈 Prediction Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Delay Probability",
                    f"{results['delay_probability']}%",
                    delta=results['delay_risk_level']
                )
            with col2:
                st.metric(
                    "Predicted Delay Days",
                    f"{results['predicted_delay_days']} days"
                )
            with col3:
                st.metric(
                    "Risk Score",
                    f"{results['risk_score']}/100",
                    delta=results['risk_tier']
                )
            
            st.info(f"💡 **Recommendation:** {results['recommendation']}")
    
    else:  # LendingClub Dataset
        st.header("💳 LendingClub Dataset - Loan Risk Assessment")
        st.markdown("Comprehensive loan risk assessment including default, delay, and fraud prediction")
        
        # Check if models are loaded
        if not models['lending_club']['loaded']:
            st.error("❌ Models not loaded. Please check model files.")
            return
        
        # Sample data presets
        col_sample1, col_sample2, col_sample3 = st.columns(3)
        with col_sample1:
            if st.button("📊 Low Risk Sample", key="low_risk_lending"):
                st.session_state.lending_sample = "low_risk"
        with col_sample2:
            if st.button("⚠️ Medium Risk Sample", key="med_risk_lending"):
                st.session_state.lending_sample = "medium_risk"
        with col_sample3:
            if st.button("🚨 High Risk Sample", key="high_risk_lending"):
                st.session_state.lending_sample = "high_risk"
        
        # Set defaults based on sample profile
        if 'lending_sample' not in st.session_state:
            st.session_state.lending_sample = None
        
        if st.session_state.lending_sample == "low_risk":
            loan_amnt_default = 10000.0
            dti_default = 15.0
            emp_length_default = 8.0
            int_rate_default = 7.5
            annual_inc_default = 95000.0
            credit_util_default = 20.0
            delinq_2yrs_default = 0
            open_acc_default = 12
            pub_rec_default = 0
        elif st.session_state.lending_sample == "medium_risk":
            loan_amnt_default = 25000.0
            dti_default = 28.0
            emp_length_default = 4.0
            int_rate_default = 12.5
            annual_inc_default = 55000.0
            credit_util_default = 55.0
            delinq_2yrs_default = 1
            open_acc_default = 8
            pub_rec_default = 0
        elif st.session_state.lending_sample == "high_risk":
            loan_amnt_default = 35000.0
            dti_default = 42.0
            emp_length_default = 2.0
            int_rate_default = 18.0
            annual_inc_default = 38000.0
            credit_util_default = 85.0
            delinq_2yrs_default = 3
            open_acc_default = 5
            pub_rec_default = 1
        else:
            loan_amnt_default = 15000.0
            dti_default = 20.0
            emp_length_default = 5.0
            int_rate_default = 12.0
            annual_inc_default = 65000.0
            credit_util_default = 35.0
            delinq_2yrs_default = 0
            open_acc_default = 10
            pub_rec_default = 0
        
        # Input form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            loan_amnt = st.number_input("Loan Amount ($)", value=loan_amnt_default, min_value=1000.0)
            dti = st.number_input("Debt-to-Income Ratio (%)", value=dti_default, min_value=0.0)
            emp_length = st.number_input("Employment Length (years)", value=emp_length_default, min_value=0.0)
        
        with col2:
            int_rate = st.number_input("Interest Rate (%)", value=int_rate_default, min_value=0.0)
            annual_inc = st.number_input("Annual Income ($)", value=annual_inc_default, min_value=10000.0)
            credit_util = st.number_input("Credit Utilization (%)", value=credit_util_default, min_value=0.0, max_value=100.0)
        
        with col3:
            delinq_2yrs = st.number_input("Delinquencies (2 years)", value=delinq_2yrs_default, min_value=0)
            open_acc = st.number_input("Open Accounts", value=open_acc_default, min_value=0)
            pub_rec = st.number_input("Public Records", value=pub_rec_default, min_value=0)
        
        # Predict button
        if st.button("🚀 Get Prediction", type="primary"):
            input_data = {
                'loan_amnt': loan_amnt,
                'dti': dti,
                'emp_length_years': emp_length,
                'int_rate': int_rate,
                'installment': loan_amnt / 36,
                'annual_inc': annual_inc,
                'delinq_2yrs': delinq_2yrs,
                'inq_last_6mths': 0,
                'open_acc': open_acc,
                'pub_rec': pub_rec,
                'revol_bal': annual_inc * 0.15,
                'total_acc': open_acc + 3,
                'Credit_Utilization': credit_util,
                'Default_Rate_By_State': 15,
                'Dispute_Count': 0,
                'collections_12_mths_ex_med': 0,
                'pub_rec_bankruptcies': 0,
                'term': 36,
                'grade': 3,
                'acc_now_delinq': 0,
                'state_encoded': 5
            }
            
            results = predict_lending_club(models, input_data)
            
            # Display results
            st.subheader("📈 Prediction Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Default Risk",
                    f"{results['default']['probability']}%",
                    delta=results['default']['risk_level']
                )
                st.metric(
                    "Delay Risk",
                    f"{results['delay']['probability']}%",
                    delta=results['delay']['risk_level']
                )
            
            with col2:
                st.metric(
                    "Fraud Score",
                    f"{results['fraud']['score']}/100",
                    delta=results['fraud']['risk_level']
                )
                st.metric(
                    "Composite Risk",
                    f"{results['composite_risk']['score']}/100",
                    delta=results['composite_risk']['tier']
                )
            
            # Acceptance decision
            acceptance = results['acceptance']
            if acceptance['decision'] == 'ACCEPT':
                st.success(f"✅ **ACCEPT** - Approval Probability: {acceptance['probability']}%")
            else:
                st.error(f"❌ **REJECT** - Rejection Probability: {100 - acceptance['probability']}%")

if __name__ == "__main__":
    main()
