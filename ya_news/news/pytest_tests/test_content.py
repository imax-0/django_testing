import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, homepage_url, generate_all_news):
    """Проверка отображения на главной странице нужного количества новостей."""
    response = client.get(homepage_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, homepage_url, generate_all_news):
    """Проверка сортировки новостей на главной странице по дате создания."""
    response = client.get(homepage_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news_detail_url, generate_all_news):
    """Проверка сортировки комментариев на странице новости по дате."""
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_timestamps = [comment.created for comment in news.comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news_detail_url):
    """
    Проверка того, что анонимному пользователю
    не отображается форма для создания комментария.
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_detail_url):
    """
    Проверка того, что авторизованному пользователю
    отображается форма для создания комментария.
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context.get('form', None), CommentForm)
