import pytest
from datetime import date, datetime, timedelta
import pytz
from unittest.mock import patch

from app.utils.datetime_utils import Dates, PASS_DAYS, IST

def test_get_today():
    assert Dates.get_today() == date.today()

def test_get_next_date():
    assert Dates.get_next_date() == date.today() + timedelta(days=1)

def test_get_next_month():
    assert Dates.get_next_month() == date.today() + timedelta(days=30)

def test_expired_token():
    # Since the function uses datetime.utcnow(), we can't assert an exact datetime
    # Instead, we check if the returned datetime is approximately 18000 seconds in the future
    future_time = Dates.expired_token()
    assert future_time > datetime.utcnow()
    assert future_time < datetime.utcnow() + timedelta(seconds=18001) # Allow for slight time difference

@patch('app.utils.datetime_utils.datetime')
def test_get_client_today(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 7, 10, 10, 30, 0, tzinfo=pytz.timezone('America/Lima'))
    mock_datetime.strftime.return_value = "10/07/2024"
    assert Dates.get_client_today() == "10/07/2024"

def test_limit_password_change_within_limit():
    # Test when password change is within the limit (e.g., 5 days old)
    created_date = date.today() - timedelta(days=5)
    assert Dates.limit_password_change(created_date) == True

def test_limit_password_change_at_limit():
    # Test when password change is exactly at the limit (e.g., 15 days old)
    created_date = date.today() - timedelta(days=PASS_DAYS)
    assert Dates.limit_password_change(created_date) == True

def test_limit_password_change_outside_limit():
    # Test when password change is outside the limit (e.g., 20 days old)
    created_date = date.today() - timedelta(days=20)
    assert Dates.limit_password_change(created_date) == False
