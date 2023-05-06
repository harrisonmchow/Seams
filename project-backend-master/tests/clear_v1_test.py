'''
This test fle aims to validate the functionality of the clear/v1
http route using pytest.

Functions:
    test_status_code_clear_v1()
    test_return_type_clear_v1()
    
'''
import pytest
import requests
from src.config import url

BASE_URL = url


def test_status_code_clear_v1():
    '''
    Verifies that clear/v1 returns a 200 status code.
    '''
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


def test_return_type_clear_v1():
    '''
    Verifies that clear/v1 returns a dictionary
    '''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    response_data = response.json()

    assert isinstance(response_data, dict) is True
