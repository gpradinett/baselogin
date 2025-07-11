import pytest

from app.utils.text_utils import TextFormat

def test_remove_html_with_html_tags():
    html_text = "<p>Hello <b>World</b>!</p>"
    expected_text = "Hello World!"
    assert TextFormat.remove_html(html_text) == expected_text

def test_remove_html_without_html_tags():
    plain_text = "Hello World!"
    expected_text = "Hello World!"
    assert TextFormat.remove_html(plain_text) == expected_text

def test_remove_html_with_empty_string():
    empty_string = ""
    expected_text = ""
    assert TextFormat.remove_html(empty_string) == expected_text

def test_remove_html_with_none_input():
    none_input = None
    expected_text = ""
    assert TextFormat.remove_html(none_input) == expected_text

def test_remove_html_with_complex_html():
    complex_html = "<div><p>Line 1</p><br>Line 2</div>"
    expected_text = "Line 1Line 2"
    assert TextFormat.remove_html(complex_html) == expected_text
