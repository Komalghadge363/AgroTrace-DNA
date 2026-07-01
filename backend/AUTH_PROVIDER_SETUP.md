# Gmail OTP and Google Sign-In Setup

This project now supports:

- Password reset OTP over Gmail SMTP
- Sign in with Google using Google Identity Services

Use the steps below to fill the required values in [`.env`](/d:/Agrotrace-DNA-main/backend/.env:1).

## 1. Gmail App Password for OTP emails

1. Sign in to the Google account that should send OTP emails.
2. Open Google Account security settings.
3. Turn on 2-Step Verification first. App passwords are available only after 2-Step Verification is enabled.
4. Open the App passwords page.
5. In "Select app", choose `Mail` or create a custom name like `Agrotrace OTP`.
6. Generate the app password.
7. Copy the 16-character password shown by Google.

Put these values in [`.env`](/d:/Agrotrace-DNA-main/backend/.env:1):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-real-gmail@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-real-gmail@gmail.com
MAIL_USE_TLS=True
```

Notes:

- Paste the app password without spaces.
- If you later change your Google account password, Google can revoke old app passwords. If OTP mail stops working, generate a new one.

## 2. Google Cloud client ID for "Continue with Google"

1. Open Google Cloud Console.
2. Create a new project, or select the project you want to use for Agrotrace.
3. Open `Google Auth Platform` and complete the branding or consent screen setup.
4. Set an app name, support email, and audience.
5. If your app is still in testing mode, add your Gmail accounts as test users.
6. Open `Clients`.
7. Click `Create Client`.
8. Choose `Web application`.
9. Give it a name like `Agrotrace Web Login`.
10. Add Authorized JavaScript origins for every frontend URL you use.

Recommended local origins:

```text
http://localhost
http://localhost:5500
http://127.0.0.1:5500
```

If you serve the frontend on another local port, add that exact origin too.

Then copy the generated client ID and put it in [`.env`](/d:/Agrotrace-DNA-main/backend/.env:1):

```env
GOOGLE_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
```

Notes:

- This implementation uses the JavaScript callback flow, so a redirect URI is not required for the current login page.
- `Continue with Google` will not work if you open the HTML file directly with `file:///...`. Serve the frontend on `http://localhost` or `http://127.0.0.1`.

## 3. Local run checklist

1. Update [`.env`](/d:/Agrotrace-DNA-main/backend/.env:1) with real Gmail and Google values.
2. Restart the backend after changing `.env`.
3. Serve the frontend from a local HTTP server.

Example:

```powershell
cd d:\Agrotrace-DNA-main\Agrotrace-DNA-main
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/login.html
```

## 4. Quick verification

- Forgot password:
  Enter a registered email on `login.html`, click `Forgot Password`, then `Send OTP`. The mail should arrive in that inbox.
- Google sign-in:
  Open `login.html` from a local HTTP origin, click the Google button, complete consent, and the app should redirect after login.
