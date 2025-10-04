from flask import Flask, redirect, url_for, render_template, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
import os
import csv
from datetime import datetime, timezone
from pathlib import Path
from flask import send_file, request, abort

# Load environment variables from .env (if present)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# Path for signup CSV
SIGNUPS_CSV = Path(__file__).parent / "signups.csv"

# Admin token for downloading signups remotely. Set ADMIN_TOKEN in your host env (Render/Heroku).
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")


def record_signup(user_info: dict):
    """Append a signup record to SIGNUPS_CSV.

    Fields: timestamp_utc_iso, id, email, name, picture
    """
    # Ensure directory exists (project root exists by definition)
    header = ["timestamp_utc", "id", "email", "name", "picture"]
    write_header = not SIGNUPS_CSV.exists()

    ts = datetime.now(timezone.utc).isoformat()

    row = [
        ts,
        user_info.get("id") or "",
        user_info.get("email") or "",
        user_info.get("name") or "",
        user_info.get("picture") or "",
    ]

    # If creating the file, write with UTF-8 BOM so Excel on Windows will detect UTF-8 correctly.
    if write_header:
        # 'utf-8-sig' writes a BOM at the start
        with SIGNUPS_CSV.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(row)
    else:
        # Append with normal utf-8
        with SIGNUPS_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

# Read Google OAuth credentials from environment variables. Set these before running.
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", None)
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", None)

# Only create and register the OAuth blueprint if credentials are provided.
oauth_configured = bool(GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET)
if oauth_configured:
    # Request scopes that match Google OpenID Connect userinfo scopes.
    # Using the full userinfo scope URIs plus 'openid' avoids scope-change warnings
    # where Google returns expanded scope names.
    blueprint = make_google_blueprint(
        client_id=GOOGLE_OAUTH_CLIENT_ID,
        client_secret=GOOGLE_OAUTH_CLIENT_SECRET,
        scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        redirect_to="profile",
    )
    app.register_blueprint(blueprint, url_prefix="/login")
else:
    blueprint = None


@app.route("/")
def index():
    return render_template("index.html", oauth_configured=oauth_configured)


@app.route("/debug/redirect-uri")
def debug_redirect_uri():
    """Return the exact redirect URI Flask-Dance will send to Google.

    Use this value to add to the Google Cloud Console -> OAuth 2.0 Client -> Authorized redirect URIs.
    """
    if not oauth_configured:
        return "OAuth not configured (no client id/secret)."
    # url_for requires an application context/request context for _external
    from flask import url_for

    try:
        uri = url_for("google.authorized", _external=True)
    except Exception as e:
        return f"Could not build redirect URI: {e}"
    return uri


@app.route("/profile")
def profile():
    # If user isn't authorized, redirect to the Google OAuth login flow
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.")
        return redirect(url_for("index"))

    user_info = resp.json()
    # keep a small subset in session for display/demo purposes
    session["user"] = {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }
    # Record the signup to CSV once per session
    if not session.get("signup_recorded"):
        try:
            record_signup(user_info)
            session["signup_recorded"] = True
        except Exception as e:
            # Don't block login if recording fails; log to console
            print(f"Failed to record signup: {e}")
    return render_template("profile.html", user=session.get("user"))


@app.route("/logout")
def logout():
    # Remove the OAuth token from the storage and clear session user
    try:
        # Flask-Dance stores tokens in the OAuth blueprint token storage
        del blueprint.token
    except Exception:
        pass
    session.pop("user", None)
    session.pop("google_oauth_token", None)
    # Allow recording a new signup after logout
    session.pop("signup_recorded", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/admin/download-signups")
def admin_download_signups():
    """Download the signups CSV.

    Protection: requires ADMIN_TOKEN env var to be set on the host. Provide the token
    either as a query parameter `?token=...` or as an Authorization header `Bearer ...`.
    """
    if not ADMIN_TOKEN:
        abort(403, "Admin download not configured on this host.")

    # Accept token in query or Authorization header
    token = request.args.get("token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token or token != ADMIN_TOKEN:
        abort(401)

    if not SIGNUPS_CSV.exists():
        abort(404, "No signups recorded yet.")

    # send_file will stream the file back as an attachment
    return send_file(
        SIGNUPS_CSV,
        as_attachment=True,
        download_name="signups.csv",
        mimetype="text/csv",
    )


if __name__ == "__main__":
    # When running locally set FLASK_DEBUG=1 or use debug=True here
    app.run(host="0.0.0.0", port=5000, debug=True)
