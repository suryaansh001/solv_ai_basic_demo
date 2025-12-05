"""
Vercel Serverless Handler
This allows the Flask app to run on Vercel as a serverless function
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export the Flask app for Vercel
handler = app
