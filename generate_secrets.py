"""
generate_secrets.py

Creates or updates a .env file in the project root containing:
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET
- FLASK_SECRET_KEY (generated securely)

Usage:
    python generate_secrets.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET

If you omit client-id or client-secret the script will prompt for them.
"""
import secrets
import argparse
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"


def generate_flask_secret_key(length=48):
    return secrets.token_urlsafe(length)


def load_existing_env():
    if not ENV_PATH.exists():
        return {}
    data = {}
    for line in ENV_PATH.read_text().splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def save_env(d):
    lines = [f"{k}={v}" for k, v in d.items()]
    ENV_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote: {ENV_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", dest="client_id")
    parser.add_argument("--client-secret", dest="client_secret")
    args = parser.parse_args()

    existing = load_existing_env()

    client_id = args.client_id or existing.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = args.client_secret or existing.get("GOOGLE_OAUTH_CLIENT_SECRET")

    if not client_id:
        client_id = input("Enter GOOGLE_OAUTH_CLIENT_ID: ").strip()
    if not client_secret:
        client_secret = input("Enter GOOGLE_OAUTH_CLIENT_SECRET: ").strip()

    flask_secret = existing.get("FLASK_SECRET_KEY") or generate_flask_secret_key(48)

    payload = {
        "GOOGLE_OAUTH_CLIENT_ID": client_id,
        "GOOGLE_OAUTH_CLIENT_SECRET": client_secret,
        "FLASK_SECRET_KEY": flask_secret,
    }

    save_env(payload)


if __name__ == "__main__":
    main()
