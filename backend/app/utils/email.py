import smtplib
from email.message import EmailMessage

from flask import current_app


class EmailDeliveryError(Exception):
    """Raised when an email cannot be delivered."""


def is_email_configured():
    """Return True when SMTP credentials are available."""
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')

    return bool(
        current_app.config.get('MAIL_SERVER')
        and current_app.config.get('MAIL_PORT')
        and username
        and password
        and username != 'your-email@gmail.com'
        and password != 'your-app-password'
    )


def send_password_reset_otp(recipient_email, otp):
    """Send a password reset OTP using the configured SMTP server."""
    if not is_email_configured():
        raise EmailDeliveryError('Email service is not configured.')

    msg = EmailMessage()
    msg['Subject'] = 'Agrotrace Password Reset OTP'
    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER')
    msg['To'] = recipient_email
    msg.set_content(
        'Your Agrotrace password reset OTP is '
        f'{otp}. This OTP is valid for 10 minutes.'
    )

    server = current_app.config['MAIL_SERVER']
    port = current_app.config['MAIL_PORT']
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']
    use_tls = current_app.config.get('MAIL_USE_TLS', True)

    try:
        with smtplib.SMTP(server, port, timeout=20) as smtp:
            smtp.ehlo()
            if use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(msg)
    except Exception as exc:
        raise EmailDeliveryError('Failed to send OTP email.') from exc
