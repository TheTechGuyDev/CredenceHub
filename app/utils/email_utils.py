"""
CredenceHub — Report Email Utility

Sends a generated PDF report (Construction Cost or Project Analysis) as an
email attachment via Flask-Mail.
"""

from flask import current_app
from flask_mail import Message
from app import mail

NAVY = "#0F2D5E"
GOLD = "#F5A623"


def _email_shell(preheader, heading, body_lines, sender_name):
    """Simple, email-client-safe HTML wrapper matching CredenceHub's branding."""
    body_html = "".join(f"<p style='margin:0 0 14px; font-size:14px; color:#333333; line-height:1.5;'>{line}</p>" for line in body_lines)
    return f"""
    <div style="display:none; max-height:0; overflow:hidden;">{preheader}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F4F6F8; padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; font-family:Arial,Helvetica,sans-serif;">
            <tr>
              <td style="background:{NAVY}; padding:20px 28px; border-top:4px solid {GOLD};">
                <span style="color:#ffffff; font-size:18px; font-weight:bold;">CredenceHub</span>
              </td>
            </tr>
            <tr>
              <td style="padding:28px;">
                <h2 style="margin:0 0 16px; font-size:18px; color:{NAVY};">{heading}</h2>
                {body_html}
              </td>
            </tr>
            <tr>
              <td style="padding:16px 28px; background:#F7FAFC; font-size:12px; color:#718096;">
                Sent via CredenceHub{f' by {sender_name}' if sender_name else ''}. This is an automated message.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """


def send_report_email(recipient, subject, heading, body_lines, pdf_buffer, pdf_filename,
                       sender_name=None, preheader=None):
    """
    Send a PDF report as an email attachment.

    Returns (success: bool, error: str | None)
    """
    try:
        msg = Message(subject=subject, recipients=[recipient])
        msg.html = _email_shell(
            preheader or subject, heading, body_lines, sender_name
        )

        pdf_buffer.seek(0)
        msg.attach(pdf_filename, 'application/pdf', pdf_buffer.read())

        mail.send(msg)
        return True, None
    except Exception as e:
        current_app.logger.error(f"Failed to send report email to {recipient}: {e}")
        return False, str(e)