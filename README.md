# Google Signup Webapp (Flask)

This is a minimal Flask app that demonstrates signing in with Google using Flask-Dance.

Setup

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create OAuth credentials in Google Cloud Console and set the following environment variables:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- (optional) `FLASK_SECRET_KEY`

Set them in PowerShell like:

```powershell
$env:GOOGLE_OAUTH_CLIENT_ID = 'your-client-id'
$env:GOOGLE_OAUTH_CLIENT_SECRET = 'your-client-secret'
$env:FLASK_SECRET_KEY = 'a-secret'
```

4. In the Google Console, set the authorized redirect URI to:

```
http://localhost:5000/login/google/authorized
```

5. Run the app:

```powershell
python app.py
```

Open http://localhost:5000 and click "Sign in with Google".

Notes

- This example uses the default token storage from Flask-Dance (in-memory). For production, configure a persistent token storage and HTTPS.
- The app stores only a small user object in the session for demonstration.
 
Deployment
----------

Option A — Render (recommended for quick deploy)

- Create a free account at https://render.com and connect your GitHub account.
- Push this repository to GitHub (see below). In Render, create a new Web Service from the repo.
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app

Option B — Heroku

- Create a Heroku app, set the environment variables in the Heroku dashboard, and push this repo.
- Ensure `Procfile` is present (included in this project).

Important

- After deploying, set `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `FLASK_SECRET_KEY` in the host's environment settings.
- Update Google Cloud Console Authorized redirect URI to use your deployed domain with the path `/login/google/authorized` (for example `https://your-app.onrender.com/login/google/authorized`).

Pushing to GitHub (manual)

1. Create an empty repository on GitHub using the website.
2. Locally, add the remote and push:

```powershell
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

