from re import L
from urllib import response
import pytest
import requests
from src.error import InputError, AccessError
from src.config import url
BASE_URL = url
#{token, img_url, x_start, y_start, x_end, y_end}
#TEST_IM = "http://upload.wikimedia.org/wikipedia/commons/8/8a/Banana-Single.jpg"
# TEST_IM = "https://wallpaperaccess.com/full/154009.jpg"
TEST_IM = "http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg"
TEST_PNG = "http://www.pngall.com/wp-content/uploads/2016/04/Banana-Free-Download-PNG.png"
#x: 1920
#y: 1080


@pytest.fixture
def clear_reg():
    print(f"{BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


@pytest.fixture
def add_u1():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email1@gmail.com", "password": "password1", "name_first": "first", "name_last": "last"})
    assert response.status_code == 200

    return response.json()  # returns token and auth user id


def test_non_retrival(clear_reg, add_u1):
    token1 = add_u1['token']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": "oogabooga", "x_start": 0, "y_start": 0, "x_end": 10, "y_end": 10})
    assert response.status_code == InputError.code


def test_valid_url_not_image(clear_reg, add_u1):
    token1 = add_u1['token']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": "https://en.wikipedia.org/wiki/Banana", "x_start": 0, "y_start": 0, "x_end": 10, "y_end": 10})
    assert response.status_code == InputError.code


def test_non_dimensionx(clear_reg, add_u1):
    token1 = add_u1['token']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": TEST_IM, "x_start": 0, "y_start": 0, "x_end": 9000, "y_end": 9000})
    assert response.status_code == InputError.code


def test_non_dimensiony(clear_reg, add_u1):
    token1 = add_u1['token']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": TEST_IM, "x_start": 0, "y_start": 0, "x_end": 10, "y_end": 9000})
    assert response.status_code == InputError.code


def test_inverted_inputs(clear_reg, add_u1):
    token1 = add_u1['token']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": TEST_IM, "x_start": 50, "y_start": 50, "x_end": 10, "y_end": 10})
    assert response.status_code == InputError.code


def test_not_jpg(clear_reg, add_u1):
    token1 = add_u1['token']
    print(token1)
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": TEST_PNG, "x_start": 0, "y_start": 0, "x_end": 10, "y_end": 10})
    assert response.status_code == InputError.code


def test_fine(clear_reg, add_u1):

    token1 = add_u1['token']
    u_id = add_u1['auth_user_id']
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1",
                             json={"token": token1, "img_url": TEST_IM, "x_start": 0, "y_start": 0, "x_end": 500, "y_end": 500})
    assert response.status_code == 200
    response2 = requests.get(
        f"{BASE_URL}/user/profile/v1", params={"token": token1, "u_id": 1})
    print(response2.json())
    imgurl = response2.json()
    print(imgurl['user']['profile_img_url'])

    response3 = requests.get(
        f"{BASE_URL}/imgurl/1.jpg")
    assert response3.status_code == 200

    response4 = requests.get(
        f"{BASE_URL}/user/profile/v1", params={"token": token1, "u_id": u_id})
    assert response4.status_code == 200
    print(response4.json())
    assert response4.json()[
        'user']['profile_img_url'] == "http://localhost:8080//imgurl/1.jpg"
