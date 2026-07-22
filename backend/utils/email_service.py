"""Email delivery for the portfolio inquiry system.

Two emails are sent per inquiry:

1. An internal notification to the site owner (RECEIVER_EMAIL) with a
   polished HTML summary of the inquiry. Reply-To is set to the visitor's
   address so hitting "Reply" in Gmail goes straight back to them.
2. An automatic confirmation email to the visitor letting them know their
   message was received.

Both are best-effort: a mail failure is logged but never raises, so a slow
or misconfigured SMTP server never breaks the public-facing form.
"""
from datetime import datetime
from markupsafe import escape

from flask import current_app
from flask_mail import Message

from extensions import mail


def _owner_email_html(inquiry, visitor_ip, sent_at):
    """Builds a modern, table-based HTML email for the site owner."""
    name = escape(inquiry.full_name)
    email = escape(inquiry.email)
    company = escape(inquiry.company) if inquiry.company else "—"
    subject = escape(inquiry.subject)
    # Preserve line breaks in the long-form requirements field.
    message = escape(inquiry.message).replace("\n", "<br>")

    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background-color:#f4f5f7;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f5f7;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 18px rgba(0,0,0,0.08);">
            <tr>
              <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:28px 32px;">
                <h1 style="margin:0;color:#ffffff;font-size:20px;">🚀 New Portfolio Inquiry</h1>
                <p style="margin:6px 0 0;color:#e5e0ff;font-size:13px;">You've received a new message from your portfolio site.</p>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 32px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;width:150px;vertical-align:top;">Name</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;font-weight:600;">{name}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;vertical-align:top;">Email</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;">{email}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;vertical-align:top;">Company</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;">{company}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;vertical-align:top;">Subject</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;">{subject}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;vertical-align:top;">Requirements</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;line-height:1.6;">{message}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#6b7280;font-size:13px;vertical-align:top;">Date &amp; Time</td>
                    <td style="padding:10px 0;border-bottom:1px solid #eef0f3;color:#111827;font-size:14px;">{sent_at}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 0;color:#6b7280;font-size:13px;vertical-align:top;">IP Address</td>
                    <td style="padding:10px 0;color:#111827;font-size:14px;">{escape(visitor_ip)}</td>
                  </tr>
                </table>
                <p style="margin:24px 0 0;font-size:12px;color:#9ca3af;">Reply directly to this email to respond to {name} — it will go straight to their inbox.</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def _visitor_email_html(inquiry):
    """Builds the auto-response HTML email sent back to the visitor."""
    name = escape(inquiry.full_name)

    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background-color:#f4f5f7;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f5f7;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 18px rgba(0,0,0,0.08);">
            <tr>
              <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:28px 32px;">
                <h1 style="margin:0;color:#ffffff;font-size:20px;">Thank You for Reaching Out</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 32px;color:#111827;font-size:14px;line-height:1.7;">
                <p style="margin:0 0 16px;">Hello {name},</p>
                <p style="margin:0 0 16px;">Thank you for contacting me. I have successfully received your inquiry.</p>
                <p style="margin:0 0 16px;">I appreciate your interest and will review your requirements carefully. I aim to respond within 24 hours.</p>
                <p style="margin:24px 0 0;">Best Regards,<br><strong>Mahi Patel</strong><br><span style="color:#6b7280;font-size:13px;">AI Developer | Machine Learning Engineer</span></p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def send_new_inquiry_email(inquiry, visitor_ip="Unknown"):
    """Notifies the portfolio owner of a new inquiry.

    Never raises - a slow or misconfigured mail server should not fail the
    inquiry submission. Returns True on success, False otherwise.
    """
    receiver_email = current_app.config.get("RECEIVER_EMAIL")
    if not receiver_email:
        current_app.logger.warning("RECEIVER_EMAIL not configured; skipping owner notification")
        return False

    sent_at = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

    try:
        msg = Message(
            subject=f"🚀 New Portfolio Inquiry from {inquiry.full_name}",
            recipients=[receiver_email],
            reply_to=inquiry.email,
            html=_owner_email_html(inquiry, visitor_ip, sent_at),
            body=(
                f"New Portfolio Inquiry\n\n"
                f"Name: {inquiry.full_name}\n"
                f"Email: {inquiry.email}\n"
                f"Company: {inquiry.company or '-'}\n"
                f"Subject: {inquiry.subject}\n\n"
                f"Project Requirements:\n{inquiry.message}\n\n"
                f"Date & Time: {sent_at}\n"
                f"IP Address: {visitor_ip}\n"
            ),
        )
        mail.send(msg)
        return True
    except Exception as exc:  # noqa: BLE001 - never let mail errors break the request
        current_app.logger.error(f"Failed to send owner notification email: {exc}")
        return False


def send_visitor_autoresponse(inquiry):
    """Sends an automatic confirmation email back to the visitor."""
    try:
        msg = Message(
            subject="Thank You for Contacting Mahi Patel",
            recipients=[inquiry.email],
            html=_visitor_email_html(inquiry),
            body=(
                f"Hello {inquiry.full_name},\n\n"
                f"Thank you for contacting me. I have successfully received your inquiry.\n\n"
                f"I appreciate your interest and will review your requirements carefully. "
                f"I aim to respond within 24 hours.\n\n"
                f"Best Regards,\nMahi Patel\nAI Developer | Machine Learning Engineer\n"
            ),
        )
        mail.send(msg)
        return True
    except Exception as exc:  # noqa: BLE001 - never let mail errors break the request
        current_app.logger.error(f"Failed to send visitor auto-response email: {exc}")
        return False
