# Procfile for Heroku/Render deployment
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 facecheck_bot:app
worker: python facecheck_bot.py




