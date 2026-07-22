from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from sqlalchemy import or_

from extensions import db, limiter
from models import Inquiry
from schemas import create_inquiry_schema, update_status_schema
from utils.email_service import send_new_inquiry_email, send_visitor_autoresponse
from utils.auth import admin_required

inquiries_bp = Blueprint("inquiries", __name__, url_prefix="/api/inquiries")


# ---------------------------------------------------------------------------
# PUBLIC: submit a new inquiry from the "Let's Connect" form
# ---------------------------------------------------------------------------
@inquiries_bp.route("", methods=["POST"])
@limiter.limit("5 per 15 minutes")
def create_inquiry():
    json_data = request.get_json(silent=True) or {}

    try:
        data = create_inquiry_schema.load(json_data)
    except ValidationError as err:
        return (
            jsonify({"success": False, "message": "Please check the form and try again.", "errors": err.messages}),
            400,
        )

    # Honeypot check - real visitors never fill this hidden field in.
    if data.get("website"):
        current_app.logger.info("Blocked spam submission via honeypot field")
        # Respond as if it succeeded so bots gain no signal, but do not save it.
        return jsonify({"success": True, "message": "Thanks! Your inquiry has been sent."}), 201

    try:
        inquiry = Inquiry(
            full_name=data["fullName"],
            email=data["email"],
            company=data.get("company") or None,
            subject=data["subject"],
            message=data["message"],
            status="NEW",
        )

        db.session.add(inquiry)
        db.session.commit()

        visitor_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "Unknown").split(",")[0].strip()

        owner_notified = send_new_inquiry_email(inquiry, visitor_ip)
        # The visitor confirmation is a nice-to-have - it never blocks the response,
        # since the inquiry is already safely stored either way.
        send_visitor_autoresponse(inquiry)

        if not owner_notified:
            return (
                jsonify({"success": False, "message": "Email could not be sent, but inquiry was saved."}),
                502,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Thank you! Your inquiry has been sent successfully.",
                    "data": inquiry.to_dict(),
                }
            ),
            201,
        )
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unhandled error while creating inquiry")
        return (
            jsonify({"success": False, "message": "Email could not be sent, but inquiry was saved."}),
            500,
        )


# ---------------------------------------------------------------------------
# ADMIN: list inquiries with search, filter, sort, pagination
# ---------------------------------------------------------------------------
@inquiries_bp.route("", methods=["GET"])
@admin_required
def list_inquiries():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "ALL").upper()
    sort = request.args.get("sort", "latest").lower()
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 20)), 1), 100)

    query = Inquiry.query

    if status in ("NEW", "READ", "REPLIED"):
        query = query.filter(Inquiry.status == status)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Inquiry.full_name.ilike(like),
                Inquiry.email.ilike(like),
                Inquiry.subject.ilike(like),
                Inquiry.message.ilike(like),
            )
        )

    query = query.order_by(
        Inquiry.created_at.asc() if sort == "oldest" else Inquiry.created_at.desc()
    )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify(
        {
            "success": True,
            "data": [item.to_dict() for item in items],
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "total": total,
                "totalPages": (total + page_size - 1) // page_size or 1,
            },
        }
    )


# ---------------------------------------------------------------------------
# ADMIN: fetch a single inquiry in full
# ---------------------------------------------------------------------------
@inquiries_bp.route("/<string:inquiry_id>", methods=["GET"])
@admin_required
def get_inquiry(inquiry_id):
    inquiry = Inquiry.query.get(inquiry_id)
    if not inquiry:
        return jsonify({"success": False, "message": "Inquiry not found"}), 404
    return jsonify({"success": True, "data": inquiry.to_dict(full=True)})


# ---------------------------------------------------------------------------
# ADMIN: mark as Read / Replied
# ---------------------------------------------------------------------------
@inquiries_bp.route("/<string:inquiry_id>/status", methods=["PATCH"])
@admin_required
def update_status(inquiry_id):
    inquiry = Inquiry.query.get(inquiry_id)
    if not inquiry:
        return jsonify({"success": False, "message": "Inquiry not found"}), 404

    json_data = request.get_json(silent=True) or {}
    try:
        data = update_status_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Invalid status", "errors": err.messages}), 400

    inquiry.status = data["status"]
    db.session.commit()

    return jsonify({"success": True, "message": "Status updated", "data": inquiry.to_dict(full=True)})


# ---------------------------------------------------------------------------
# ADMIN: delete an inquiry
# ---------------------------------------------------------------------------
@inquiries_bp.route("/<string:inquiry_id>", methods=["DELETE"])
@admin_required
def delete_inquiry(inquiry_id):
    inquiry = Inquiry.query.get(inquiry_id)
    if not inquiry:
        return jsonify({"success": False, "message": "Inquiry not found"}), 404

    db.session.delete(inquiry)
    db.session.commit()

    return jsonify({"success": True, "message": "Inquiry deleted"})
