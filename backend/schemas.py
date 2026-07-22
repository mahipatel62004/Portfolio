from marshmallow import Schema, fields, validate, ValidationError


class CreateInquirySchema(Schema):
    """Validates a new inquiry submitted from the public contact form."""

    fullName = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100, error="Full name must be 2-100 characters"),
    )
    email = fields.Email(required=True, validate=validate.Length(max=150))
    company = fields.String(
        required=False, allow_none=True, load_default="", validate=validate.Length(max=150)
    )
    subject = fields.String(
        required=True,
        validate=validate.Length(min=3, max=150, error="Subject must be 3-150 characters"),
    )
    message = fields.String(
        required=True,
        validate=validate.Length(min=10, max=3000, error="Message must be 10-3000 characters"),
    )
    # Honeypot field - must always arrive empty. Bots that auto-fill every
    # visible/hidden input will populate it, marking the submission as spam.
    website = fields.String(required=False, allow_none=True, load_default="")


class UpdateStatusSchema(Schema):
    status = fields.String(
        required=True, validate=validate.OneOf(["NEW", "READ", "REPLIED"])
    )


create_inquiry_schema = CreateInquirySchema()
update_status_schema = UpdateStatusSchema()

__all__ = ["create_inquiry_schema", "update_status_schema", "ValidationError"]
