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
