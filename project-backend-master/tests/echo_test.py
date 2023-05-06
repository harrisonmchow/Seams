'''Echo File'''
import pytest


from src.error import InputError
import requests
from src.config import url
BASE_URL = url


def test_echo_http():
    assert requests.get(
        f"{BASE_URL}/echo", {"data": "1"}).json() == {"data": "1"}
    assert requests.get(
        f"{BASE_URL}/echo", {"data": "abc"}).json() == {"data": "abc"}
    assert requests.get(
        f"{BASE_URL}/echo", {"data": "trump"}).json() == {"data": "trump"}


def test_echo_except_http():
    assert requests.get(
        f"{BASE_URL}/echo", {"data": "echo"}).status_code == InputError.code
