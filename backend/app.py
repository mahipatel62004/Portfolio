from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, migrate, mail, limiter
from routes.inquiries import inquiries_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensions -------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)

    CORS(app)

    # --- Blueprints ---------------------------------------------------------
    app.register_blueprint(inquiries_bp)

    # --- Health check -------------------------------------------------------
    @app.route("/api/health")
    def health():
        return jsonify({"success": True, "message": "API is running"})

    # --- Centralized error handling -----------------------------------------
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limited(_e):
        return (
            jsonify({"success": False, "message": "Too many requests. Please try again later."}),
            429,
        )

    @app.errorhandler(500)
    def server_error(_e):
        app.logger.exception("Unhandled server error")
        return jsonify({"success": False, "message": "Something went wrong. Please try again."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
