import pytest
from unittest.mock import patch
from app.utils import send_email, EmailData

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
