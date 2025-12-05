# Vercel Deployment Troubleshooting

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'distutils'"

**Cause**: Python 3.12 removed distutils. Vercel is using Python 3.12 by default.

**Solution**: 
- Specify Python version in vercel.json (done ✅)
- Use `.python-version` file set to 3.11.4 (done ✅)
- Update requirements to use flexible versions (done ✅)

### Issue 2: "pip._vendor.pyproject_hooks._impl.BackendUnavailable"

**Cause**: Build dependencies missing for compiling packages from source.

**Solution**:
- Use pre-built wheels instead of source distributions
- Change exact versions to flexible versions (>=)
- Install build tools before pip install

### Issue 3: Build Takes Too Long / Times Out

**Cause**: Compiling numpy and pandas from source takes time.

**Solution**:
- Use serverless functions (api/index.py)
- Keep requirements minimal
- Use cached builds

### Issue 4: Model Files Not Found

**Cause**: Model files not included in repository or in wrong path.

**Solution**:
```bash
# Verify models are committed
git ls-files | grep models/

# Add if needed
git add -A models/
git commit -m "Add model files"
git push
```

### Issue 5: "413 Payload Too Large"

**Cause**: Total deployment size exceeds 50MB limit (model files too large).

**Solution**:
- Remove unnecessary models
- Use Git LFS for large files:
```bash
# Install Git LFS
brew install git-lfs
git lfs install

# Track model files
git lfs track "*.pkl"
git lfs track "*.joblib"

# Add and push
git add .gitattributes
git add models/
git commit -m "Use Git LFS for models"
git push
```

## Quick Fix Commands

```bash
# Force rebuild
vercel --prod --force

# Check current deployment
vercel logs

# View specific error
vercel logs --tail

# Redeploy
vercel redeploy

# Clear cache and rebuild
vercel env pull
vercel build --prod
```

## Environment Setup for Vercel

Add these in Vercel Dashboard > Project Settings > Environment Variables:

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

## Local Testing Before Deployment

```bash
# Test with Vercel CLI locally
vercel dev

# Then test at http://localhost:3000
```

## Monitoring After Deployment

1. Check Vercel Dashboard for deployment status
2. Monitor function logs: `vercel logs --tail`
3. Test endpoints:
   ```bash
   curl https://your-deployment.vercel.app/
   curl https://your-deployment.vercel.app/api/model_info/synthetic_ai
   curl https://your-deployment.vercel.app/api/health
   ```

## If All Else Fails

Deploy to alternative platforms:
- **Heroku**: `git push heroku main` (requires Procfile and runtime.txt)
- **Railway.app**: Push to GitHub, connect repository
- **Render**: Similar to Heroku, use Procfile
- **PythonAnywhere**: Upload via web interface
- **AWS Lambda**: Use serverless framework
- **Google Cloud Run**: Use Docker container
