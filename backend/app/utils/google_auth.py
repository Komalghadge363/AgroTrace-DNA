import requests

from flask import current_app


class GoogleAuthError(Exception):
    """Raised when Google sign-in verification fails."""


def is_google_login_configured():
    """Return True when a Google client ID is configured."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    return bool(
        client_id
        and client_id != 'your-google-web-client-id.apps.googleusercontent.com'
    )


def verify_google_id_token(credential):
    """Verify a Google ID token using Google's tokeninfo endpoint."""
    if not is_google_login_configured():
        raise GoogleAuthError('Google sign-in is not configured.')

    if not credential:
        raise GoogleAuthError('Missing Google credential.')

    response = requests.get(
        'https://oauth2.googleapis.com/tokeninfo',
        params={'id_token': credential},
        timeout=10
    )

    if response.status_code != 200:
        raise GoogleAuthError('Invalid Google credential.')

    payload = response.json()
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')

    if payload.get('aud') != client_id:
        raise GoogleAuthError('Google credential audience mismatch.')

    if payload.get('email_verified') not in ('true', True):
        raise GoogleAuthError('Google email is not verified.')

    issuer = payload.get('iss')
    if issuer not in ('accounts.google.com', 'https://accounts.google.com'):
        raise GoogleAuthError('Invalid Google credential issuer.')

    return payload
