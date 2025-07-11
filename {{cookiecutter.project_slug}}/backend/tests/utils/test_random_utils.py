import pytest
from unittest.mock import patch

from app.utils.random_utils import RandomDigits

@patch('app.utils.random_utils.random')
def test_four_digits(mock_random):
    mock_random.randint.return_value = 1234
    assert RandomDigits.four_digits() == "1234"
    mock_random.randint.assert_called_once_with(1000, 9999)

@patch('app.utils.random_utils.random')
def test_six_digits(mock_random):
    mock_random.randint.return_value = 123456
    assert RandomDigits.six_digits() == "123456"
    mock_random.randint.assert_called_once_with(100000, 999999)
