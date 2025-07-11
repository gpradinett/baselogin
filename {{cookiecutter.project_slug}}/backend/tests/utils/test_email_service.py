import pytest
from app.utils import send_email, EmailData
from app.core.config import settings

def test_send_test_email():
    """
    Test to send a simple email to gpradinett@gmail.com to verify email service.
    """
    if not settings.emails_enabled:
        pytest.skip("Email sending is not enabled in settings.")

    email_to = "gpradinett@gmail.com"
    subject = "Test Email from Gemini CLI"
    html_content = "<p>This is a test email sent from the Gemini CLI to verify email service functionality.</p>"

    email_data = EmailData(html_content=html_content, subject=subject)

    try:
        send_email(email_to=email_to, email_data=email_data)
        print(f"✅ Test email sent successfully to {email_to}. Please check your inbox.")
    except Exception as e:
        pytest.fail(f"❌ Failed to send test email: {e}")

from unittest.mock import patch

def test_send_email_failure():
    """
    Test that send_email raises an exception when SMTP connection fails.
    """
    with patch('app.utils.email_utils.settings') as mock_settings:
        mock_settings.emails_enabled = True

        email_to = "test@example.com"
        subject = "Test Email Failure"
        html_content = "<p>This is a test email.</p>"
        email_data = EmailData(html_content=html_content, subject=subject)

        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("SMTP connection failed")
            with pytest.raises(Exception, match="SMTP connection failed"):
                send_email(email_to=email_to, email_data=email_data)
