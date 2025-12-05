# AI Risk Prediction System

A comprehensive web application for machine learning-based risk prediction using two model types:
1. **Synthetic AI Dataset** - Payment delay prediction for companies
2. **LendingClub Dataset** - Loan risk assessment

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/suryaansh001/solv_ai_basic_demo.git
cd frontend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📦 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
```bash
brew install heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku app**
```bash
heroku create your-app-name
```

4. **Deploy**
```bash
git push heroku main
```

5. **View logs**
```bash
heroku logs --tail
```

### Environment Variables

Set the following environment variables in your deployment platform:

- `FLASK_ENV`: Set to `production` for production deployments
- `PORT`: Set by most platforms automatically (defaults to 5000 locally)

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
```

Build and run:
```bash
docker build -t ai-risk-prediction .
docker run -p 5000:5000 ai-risk-prediction
```

## 📋 Features

- 🎯 **Model Selection**: Choose between two ML models
- 📊 **Interactive Forms**: Dynamic form generation based on model requirements
- 📈 **Sample Data**: Pre-configured sample profiles for testing
- 📉 **Prediction Results**: Beautiful visualization of prediction outcomes
- 🎨 **Dark Theme**: Modern, professional UI with smooth animations
- ⚡ **Real-time Processing**: Fast API responses with caching headers

## 🏗️ Architecture

- **Backend**: Flask REST API with CORS support
- **Frontend**: Bootstrap 5 with custom CSS and vanilla JavaScript
- **Models**: Pre-trained ML models (Random Forest, Gradient Boosting, Neural Networks)
- **Data**: Model serialization with joblib

## 📝 API Endpoints

### Get Model Information
```
GET /api/model_info/<model_type>

Parameters:
- model_type: 'synthetic_ai' or 'lending_club'

Response:
{
  "description": "...",
  "features": [...]
}
```

### Make Predictions
```
POST /api/predict

Body:
{
  "model_type": "synthetic_ai" | "lending_club",
  "input_data": {...}
}

Response:
{
  "predictions": {...},
  "confidence": 0.95,
  "risk_level": "Low" | "High"
}
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask 2.3.3
- **Frontend**: HTML5, Bootstrap 5, JavaScript ES6+
- **ML**: pandas, numpy, joblib
- **Server**: Gunicorn
- **Deployment**: Heroku, Docker, Cloud Platforms

## 📦 Project Structure

```
frontend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile             # Heroku configuration
├── runtime.txt          # Python version
├── Dockerfile           # Docker configuration
├── .gitignore           # Git ignore patterns
├── README.md            # This file
└── templates/
    └── index.html       # Frontend application
```

## 🐛 Troubleshooting

### Models not loading
- Ensure model files exist in the configured directories
- Check file permissions and paths in `app.py`

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### CORS errors
- CORS is enabled in the Flask app
- Check browser console for specific error messages

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 👤 Author

Created for comprehensive risk assessment and machine learning model deployment.

## 🔗 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Heroku Deployment Guide](https://devcenter.heroku.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
