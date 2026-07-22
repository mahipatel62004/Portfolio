import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central app configuration, all values sourced from environment
    variables so no secrets are ever hardcoded."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:password@localhost:5432/mahi_portfolio",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLIENT_ORIGIN = os.environ.get("CLIENT_ORIGIN", "http://localhost:5500")

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # The inbox that receives new inquiries. RECEIVER_EMAIL is the primary
    # variable name; NOTIFY_EMAIL is kept as a fallback for backward
    # compatibility with earlier setups.
    RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") or os.environ.get("NOTIFY_EMAIL")
    NOTIFY_EMAIL = RECEIVER_EMAIL

    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "dev-admin-key-change-me")
