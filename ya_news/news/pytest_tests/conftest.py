from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not_author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='news_title',
        text='news_text'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='comment_text'
    )


@pytest.fixture
def homepage_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id, ))


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id, ))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id, ))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def generate_all_news():
    current_day = datetime.today()
    News.objects.bulk_create(
        [
            News(
                title=f'News {idx}',
                text='news_text',
                date=current_day - timedelta(days=idx)
            ) for idx in range(settings.NEWS_COUNT_ON_HOME_PAGE)
        ]
    )


@pytest.fixture
def generate_all_comments(news, author):
    now = timezone.now()
    for idx in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {idx}'
        )
        comment.created = now + timedelta(days=idx)
        comment.save()
