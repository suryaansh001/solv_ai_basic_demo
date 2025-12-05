# Vercel Deployment Guide - Complete Solution

## ✅ Fixed Issues

The following issues have been resolved:

1. **Schema Validation Error** - Removed invalid `python` object from vercel.json
2. **Unmatched Function Pattern** - Removed api wrapper, using native Flask framework support
3. **Model Path Issues** - Models are now in `/models/` directory with relative paths
4. **Dependency Issues** - Updated requirements.txt with flexible version constraints

## 📋 Current Setup

### Files Configuration

```
frontend/
├── app.py                    # Flask application (entry point)
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration (FIXED)
├── runtime.txt              # Python version specification
├── .python-version          # Fallback Python version
├── Procfile                 # For alternative deployment platforms
├── Dockerfile               # For Docker deployment
├── docker-compose.yml       # Local Docker development
├── models/
│   ├── synthetic_ai/
│   │   ├── rf_delay_probability.pkl
│   │   └── rf_delay_days.pkl
│   └── lending_club/
│       ├── acceptance_model_v1.0.joblib
│       ├── default_model_v1.0.joblib
│       ├── delay_model_v1.0.joblib
│       └── fraud_model_v1.0.joblib
└── templates/
    └── index.html           # Frontend UI
```

### Key Configuration Changes

**vercel.json** (Current - Working):
```json
{
  "framework": "flask",
  "buildCommand": "pip install -r requirements.txt",
  "devCommand": "flask run",
  "env": {
    "FLASK_ENV": "production",
    "PYTHONUNBUFFERED": "1"
  }
}
```

**requirements.txt** (Current - Compatible):
- Flask==2.3.3
- flask-cors==4.0.0
- pandas>=1.5.0 (flexible version)
- numpy>=1.23.0 (flexible version)
- joblib>=1.3.0 (flexible version)

## 🚀 Deployment Steps

### 1. Manual Verification (Before Deployment)

```bash
# Navigate to frontend directory
cd frontend/

# Test locally
python app.py

# Should start on http://localhost:5000
```

### 2. Deploy to Vercel

**Option A: Via CLI**
```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

**Option B: Via GitHub**
1. Go to https://vercel.com
2. Click "New Project"
3. Select GitHub repository: `suryaansh001/solv_ai_basic_demo`
4. Set Root Directory: `frontend`
5. Click Deploy

### 3. Monitor Deployment

```bash
# View build logs
vercel logs

# View real-time logs
vercel logs --tail

# Check specific deployment
vercel deployments
```

## ✅ What Vercel Will Do

1. **Install Dependencies**
   - Reads `requirements.txt`
   - Installs Python packages using pip
   - No build tools needed (pre-built wheels)

2. **Build**
   - Runs `buildCommand`: `pip install -r requirements.txt`
   - Prepares Flask app

3. **Deploy**
   - Routes all traffic to Flask app
   - Uses native Python runtime
   - Models loaded from `/models/` directory

## 📊 Expected Deployment Output

```
✓ Deployment successful!
✓ Production: https://your-app-name.vercel.app
✓ Dashboard: https://vercel.com/dashboard

Health check:
✓ GET https://your-app-name.vercel.app/ → 200
✓ GET https://your-app-name.vercel.app/api/health → 200
✓ GET https://your-app-name.vercel.app/api/model_info/synthetic_ai → 200
```

## 🔍 Troubleshooting

### Build Fails: "No matching distribution found"

**Solution**: Update requirements with compatible versions
```bash
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Runtime Error: "Model files not found"

**Solution**: Verify models are in repository
```bash
# Check if models are tracked
git ls-files | grep models/

# Should see:
# models/synthetic_ai/rf_delay_days.pkl
# models/synthetic_ai/rf_delay_probability.pkl
# models/lending_club/*.joblib
```

### 413 Payload Too Large

**Cause**: Total deployment exceeds 50MB

**Solution**: Use Git LFS
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pkl"
git lfs track "*.joblib"

# Commit
git add .gitattributes models/
git commit -m "Use Git LFS for models"
git push
```

### CORS or API Errors

**Already Fixed**: CORS is enabled in app.py
```python
from flask_cors import CORS
CORS(app)
```

## 📝 Environment Variables (Optional)

If needed, set in Vercel Dashboard:

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

## 🎯 Testing After Deployment

```bash
# Replace with your actual Vercel URL
VERCEL_URL="your-app-name.vercel.app"

# Test home page
curl https://$VERCEL_URL/

# Test health check
curl https://$VERCEL_URL/api/health

# Test model info
curl https://$VERCEL_URL/api/model_info/synthetic_ai
curl https://$VERCEL_URL/api/model_info/lending_club

# Test prediction
curl -X POST https://$VERCEL_URL/api/predict \
  -H "Content-Type: application/json" \
  -d '{"model_type":"synthetic_ai","input_data":{"avg_delay_days":5}}'
```

## 🔄 Redeployment

To redeploy after changes:

```bash
# Push to main branch
git push origin main

# Vercel automatically redeploys (if GitHub connected)
# OR manually:
vercel --prod
```

## 📦 Alternative Deployment Options

If Vercel deployment continues to fail:

### Deploy to Heroku
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Deploy to Railway.app
1. Connect GitHub repository
2. Select `frontend` folder as root
3. Auto-deploys on push

### Deploy to PythonAnywhere
1. Upload code via web interface
2. Configure WSGI file
3. No model files size limitations

### Deploy to AWS Lambda
Use serverless framework or AWS SAM

### Deploy to Google Cloud Run
```bash
gcloud run deploy --source .
```

## 📞 Getting Help

- **Vercel Docs**: https://vercel.com/docs/concepts/frameworks/flask
- **Flask Docs**: https://flask.palletsprojects.com
- **GitHub Issues**: Report issues in repository

## ✨ Success Indicators

Your deployment is successful when:

✅ Home page loads at your Vercel URL
✅ Model cards are visible and clickable
✅ Form fields generate without errors
✅ Sample data loads correctly
✅ Predictions return valid results
✅ No errors in browser console
✅ No 500 errors in Vercel logs

---

**Last Updated**: December 6, 2025
**Status**: Ready for Production Deployment ✅
