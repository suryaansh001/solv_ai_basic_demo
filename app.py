"""
Risk Prediction Web Application
Supports two model types:
1. Synthetic AI Dataset - Payment delay prediction for companies
2. LendingClub Dataset - Loan risk assessment

Author: Risk Assessment System
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
import sys
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Add cache-busting headers
@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths to models
SYNTHETIC_AI_MODEL_DIR = '/home/sury/proj/solviser/solviser/solve/pythonTry1/'
LENDING_CLUB_MODEL_DIR = '/home/sury/proj/solviser/solviser/solve/pythontry2/final_mdels/'

# Global model storage
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


# ============================================================================
# MODEL LOADING FUNCTIONS
# ============================================================================

def load_synthetic_ai_models():
    """Load Synthetic AI Dataset models"""
    global models
    
    if models['synthetic_ai']['loaded']:
        return True
    
    try:
        # Load delay probability classifier
        clf_path = os.path.join(SYNTHETIC_AI_MODEL_DIR, 'rf_delay_probability.pkl')
        if os.path.exists(clf_path):
            models['synthetic_ai']['delay_probability'] = joblib.load(clf_path)
            print(f"✅ Loaded delay probability model from {clf_path}")
        
        # Load delay days regressor
        reg_path = os.path.join(SYNTHETIC_AI_MODEL_DIR, 'rf_delay_days.pkl')
        if os.path.exists(reg_path):
            models['synthetic_ai']['delay_days'] = joblib.load(reg_path)
            print(f"✅ Loaded delay days model from {reg_path}")
        
        models['synthetic_ai']['loaded'] = True
        return True
    except Exception as e:
        print(f"❌ Error loading Synthetic AI models: {e}")
        return False


def load_lending_club_models():
    """Load LendingClub models"""
    global models
    
    if models['lending_club']['loaded']:
        return True
    
    try:
        model_types = ['acceptance', 'default', 'delay', 'fraud']
        
        for model_type in model_types:
            model_path = os.path.join(LENDING_CLUB_MODEL_DIR, f'{model_type}_model_v1.0.joblib')
            if os.path.exists(model_path):
                models['lending_club'][model_type] = joblib.load(model_path)
                print(f"✅ Loaded {model_type} model from {model_path}")
        
        models['lending_club']['loaded'] = True
        return True
    except Exception as e:
        print(f"❌ Error loading LendingClub models: {e}")
        return False


# ============================================================================
# PREDICTION FUNCTIONS
# ============================================================================

def predict_synthetic_ai(data):
    """
    Predict using Synthetic AI models (Payment delay for companies)
    
    Required features:
    - avg_delay_days: Average historical delay days
    - max_delay_days: Maximum historical delay days
    - std_delay_days: Standard deviation of delay days
    - on_time_rate: Historical on-time payment rate (0-1)
    - total_value: Total transaction value
    - avg_credit_days: Average credit days given
    
    For delay days prediction (if delayed):
    - delayed_count: Number of delayed payments
    - total_txn: Total transactions
    - CreditDays: Current credit days
    - Amount: Current transaction amount
    - OutstandingAmount: Current outstanding amount
    """
    
    if not load_synthetic_ai_models():
        return {"error": "Failed to load Synthetic AI models"}
    
    results = {}
    
    # Predict delay probability
    clf_package = models['synthetic_ai']['delay_probability']
    if clf_package:
        clf = clf_package['model']
        clf_features = clf_package['features']
        
        # Prepare features for classifier
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
    
    # Predict delay days (if delayed)
    reg_package = models['synthetic_ai']['delay_days']
    if reg_package:
        reg = reg_package['model']
        reg_features = reg_package['features']
        
        # Prepare features for regressor
        reg_data = {feat: data.get(feat, 0) for feat in reg_features}
        X_reg = pd.DataFrame([reg_data])
        
        predicted_days = reg.predict(X_reg)[0]
        results['predicted_delay_days'] = round(float(max(0, predicted_days)), 1)
    
    # Calculate composite risk score
    delay_prob = results.get('delay_probability', 0) / 100
    predicted_days = results.get('predicted_delay_days', 0)
    
    # Risk score based on probability and expected delay
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
        results['recommendation'] = "HIGH RISK - Require advance payment or collateral"
    elif results['risk_tier'] == 'HIGH':
        results['recommendation'] = "ELEVATED RISK - Reduce credit terms, monitor closely"
    elif results['risk_tier'] == 'MEDIUM':
        results['recommendation'] = "MODERATE RISK - Standard terms with monitoring"
    else:
        results['recommendation'] = "LOW RISK - Proceed with normal credit terms"
    
    results['timestamp'] = datetime.now().isoformat()
    results['model_type'] = 'Synthetic AI Dataset'
    
    return results


def predict_lending_club(data):
    """
    Predict using LendingClub models (Loan risk assessment)
    
    Required features:
    - loan_amnt, dti, emp_length_years, state_encoded, int_rate, installment
    - annual_inc, delinq_2yrs, inq_last_6mths, open_acc, pub_rec, revol_bal
    - total_acc, Credit_Utilization, Default_Rate_By_State, Dispute_Count
    - collections_12_mths_ex_med, pub_rec_bankruptcies, term, grade, acc_now_delinq
    """
    
    if not load_lending_club_models():
        return {"error": "Failed to load LendingClub models"}
    
    results = {}
    loan_df = pd.DataFrame([data])
    
    # 1. Acceptance Prediction
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
    
    # 2. Default Prediction
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
    
    # 3. Delay Prediction
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
    
    # 4. Fraud Detection
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
    
    # 5. Composite Risk Score
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
    
    # 6. Final Recommendation
    acceptance_decision = results.get('acceptance', {}).get('decision', 'UNKNOWN')
    composite_tier = results['composite_risk']['tier']
    
    if acceptance_decision == 'REJECT':
        recommendation = "REJECT - Application does not meet acceptance criteria"
    elif composite_tier == 'CRITICAL':
        recommendation = "REJECT - Critical risk level detected"
    elif composite_tier == 'HIGH':
        recommendation = "REVIEW - Consider additional verification or higher rates"
    elif composite_tier == 'MEDIUM':
        recommendation = "APPROVE - Monitor closely during term"
    else:
        recommendation = "APPROVE - Standard terms apply"
    
    results['recommendation'] = recommendation
    results['timestamp'] = datetime.now().isoformat()
    results['model_type'] = 'LendingClub Dataset'
    
    return results


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.json
        model_type = data.get('model_type', '')
        input_data = data.get('input_data', {})
        
        if model_type == 'synthetic_ai':
            results = predict_synthetic_ai(input_data)
        elif model_type == 'lending_club':
            results = predict_lending_club(input_data)
        else:
            return jsonify({"error": f"Unknown model type: {model_type}"}), 400
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/model_info/<model_type>')
def model_info(model_type):
    """Get model information and required features"""
    
    if model_type == 'synthetic_ai':
        return jsonify({
            'name': 'Synthetic AI Dataset',
            'description': 'Payment delay prediction for companies based on historical transaction data',
            'features': {
                'delay_probability': [
                    {'name': 'avg_delay_days', 'type': 'number', 'description': 'Average historical delay days', 'default': 0},
                    {'name': 'max_delay_days', 'type': 'number', 'description': 'Maximum historical delay days', 'default': 0},
                    {'name': 'std_delay_days', 'type': 'number', 'description': 'Standard deviation of delay days', 'default': 0},
                    {'name': 'on_time_rate', 'type': 'number', 'description': 'On-time payment rate (0-1)', 'default': 0.8},
                    {'name': 'total_value', 'type': 'number', 'description': 'Total transaction value ($)', 'default': 100000},
                    {'name': 'avg_credit_days', 'type': 'number', 'description': 'Average credit days', 'default': 30}
                ],
                'delay_days': [
                    {'name': 'delayed_count', 'type': 'number', 'description': 'Number of delayed payments', 'default': 0},
                    {'name': 'total_txn', 'type': 'number', 'description': 'Total transactions', 'default': 10},
                    {'name': 'CreditDays', 'type': 'number', 'description': 'Current credit days', 'default': 30},
                    {'name': 'Amount', 'type': 'number', 'description': 'Current transaction amount ($)', 'default': 10000},
                    {'name': 'OutstandingAmount', 'type': 'number', 'description': 'Outstanding amount ($)', 'default': 0}
                ]
            },
            'outputs': ['Delay Probability', 'Predicted Delay Days', 'Risk Score', 'Recommendation']
        })
    
    elif model_type == 'lending_club':
        return jsonify({
            'name': 'LendingClub Dataset',
            'description': 'Comprehensive loan risk assessment including acceptance, default, delay, and fraud prediction',
            'features': [
                {'name': 'loan_amnt', 'type': 'number', 'description': 'Loan amount ($)', 'default': 15000},
                {'name': 'dti', 'type': 'number', 'description': 'Debt-to-income ratio (%)', 'default': 20},
                {'name': 'emp_length_years', 'type': 'number', 'description': 'Employment length (years)', 'default': 5},
                {'name': 'state_encoded', 'type': 'number', 'description': 'State code (0-50)', 'default': 5},
                {'name': 'int_rate', 'type': 'number', 'description': 'Interest rate (%)', 'default': 12},
                {'name': 'installment', 'type': 'number', 'description': 'Monthly installment ($)', 'default': 450},
                {'name': 'annual_inc', 'type': 'number', 'description': 'Annual income ($)', 'default': 65000},
                {'name': 'delinq_2yrs', 'type': 'number', 'description': 'Delinquencies in last 2 years', 'default': 0},
                {'name': 'inq_last_6mths', 'type': 'number', 'description': 'Credit inquiries (last 6 months)', 'default': 1},
                {'name': 'open_acc', 'type': 'number', 'description': 'Open credit accounts', 'default': 10},
                {'name': 'pub_rec', 'type': 'number', 'description': 'Public records', 'default': 0},
                {'name': 'revol_bal', 'type': 'number', 'description': 'Revolving balance ($)', 'default': 8000},
                {'name': 'total_acc', 'type': 'number', 'description': 'Total credit accounts', 'default': 15},
                {'name': 'Credit_Utilization', 'type': 'number', 'description': 'Credit utilization (%)', 'default': 35},
                {'name': 'Default_Rate_By_State', 'type': 'number', 'description': 'State default rate (%)', 'default': 15},
                {'name': 'Dispute_Count', 'type': 'number', 'description': 'Dispute count', 'default': 0},
                {'name': 'collections_12_mths_ex_med', 'type': 'number', 'description': 'Collections (last 12 months)', 'default': 0},
                {'name': 'pub_rec_bankruptcies', 'type': 'number', 'description': 'Bankruptcies', 'default': 0},
                {'name': 'term', 'type': 'number', 'description': 'Loan term (months)', 'default': 36},
                {'name': 'grade', 'type': 'number', 'description': 'Credit grade (1=A to 7=G)', 'default': 2},
                {'name': 'acc_now_delinq', 'type': 'number', 'description': 'Accounts now delinquent', 'default': 0}
            ],
            'outputs': ['Acceptance Decision', 'Default Probability', 'Delay Probability', 'Fraud Score', 'Composite Risk Score', 'Recommendation']
        })
    
    return jsonify({"error": "Unknown model type"}), 400


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'synthetic_ai_models': 'loaded' if models['synthetic_ai']['loaded'] else 'not loaded',
        'lending_club_models': 'loaded' if models['lending_club']['loaded'] else 'not loaded',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING RISK PREDICTION WEB APPLICATION")
    print("="*60)
    
    # Pre-load models
    print("\n📦 Pre-loading models...")
    load_synthetic_ai_models()
    load_lending_club_models()
    
    print("\n🌐 Starting server...")
    print("   URL: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
