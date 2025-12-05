# Deployment Checklist

## Pre-Deployment

- [ ] All dependencies listed in `requirements.txt`
- [ ] Environment variables documented in `.env.example`
- [ ] `Procfile` configured for production server
- [ ] `runtime.txt` specifies Python version
- [ ] Code tested locally with `python app.py`
- [ ] Git repository initialized and committed
- [ ] `.gitignore` configured properly

## Local Testing

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test locally
python app.py

# Test with gunicorn (production server)
gunicorn app:app --bind 0.0.0.0:5000
```

## Deployment to Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create new app
heroku create your-app-name

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Set environment variables if needed
heroku config:set FLASK_ENV=production
```

## Deployment to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs
```

**Important Notes for Vercel:**
- Uses serverless functions (`api/index.py`)
- Requires model files in repository (`/frontend/models/`)
- Max function timeout: 60 seconds
- Max payload: 50MB
- Set `FLASK_ENV=production` in environment variables

## Deployment with Docker

```bash
# Build image
docker build -t ai-risk-prediction .

# Run container
docker run -p 5000:5000 ai-risk-prediction

# Or use docker-compose
docker-compose up
```

## Deployment to Cloud Platforms

### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-risk-prediction
gcloud run deploy ai-risk-prediction --image gcr.io/PROJECT-ID/ai-risk-prediction --platform managed --region us-central1
```

### AWS ECS
- Create ECR repository
- Push Docker image
- Create ECS service
- Configure load balancer

### Azure App Service
```bash
az webapp up --name ai-risk-prediction --resource-group myResourceGroup --runtime python:3.11
```

## Post-Deployment

- [ ] Verify application loads at `https://your-app-url`
- [ ] Test model selection and predictions
- [ ] Check browser console for errors
- [ ] Monitor application logs
- [ ] Set up auto-scaling if needed
- [ ] Configure custom domain if required
- [ ] Set up SSL/TLS certificate
- [ ] Enable error monitoring/logging service
- [ ] Set up backup for model files if necessary

## Troubleshooting

### Application Won't Start
```bash
# Check logs
heroku logs --tail

# Verify requirements are complete
pip install -r requirements.txt

# Test locally first
python app.py
```

### Models Not Loading
- Verify model file paths in `app.py`
- Check model file permissions
- Ensure models are included in deployment
- Check storage limits on deployment platform

### Performance Issues
- Monitor resource usage
- Scale up dyno/instance type if needed
- Implement caching strategies
- Consider async processing for predictions

### CORS/API Errors
- Verify CORS headers in Flask app
- Check browser console for detailed errors
- Ensure API endpoints are correct
- Test endpoints with curl/Postman

## Maintenance

- Keep dependencies updated
- Monitor application performance
- Review error logs regularly
- Test application functionality monthly
- Update models as needed
- Keep documentation current
