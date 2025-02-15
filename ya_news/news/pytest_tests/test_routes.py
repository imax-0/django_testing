from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


PUBLIC_URLS = (
    pytest.lazy_fixture('homepage_url'),
    pytest.lazy_fixture('news_detail_url'),
    pytest.lazy_fixture('login_url'),
    pytest.lazy_fixture('logout_url'),
    pytest.lazy_fixture('signup_url'),
)


PRIVATE_URLS = (
    pytest.lazy_fixture('comment_edit_url'),
    pytest.lazy_fixture('comment_delete_url'),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    PUBLIC_URLS
)
def test_pages_availability(client, url):
    """Проверка доступности анонимному пользователю публичных страниц."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url',
    PRIVATE_URLS
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, url
):
    """
    Проверка доступности авторизованному пользователю
    и недоступности анонимному пользователю приватных страниц.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    PRIVATE_URLS
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """
    Проверка редиректа анонимного пользователя на страницу логина
    при попытке захода на приватную страницу
    """
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
