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
    news = News.objects.create(
        title='news_title',
        text='news_text'
    )
    return news


@pytest.fixture
def news_id_for_args(news):
    return (news.id, )


@pytest.fixture
def news_detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='comment_text'
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id, )


@pytest.fixture
def generate_all_news():
    curr_day = datetime.today()
    all_news = [
        News(
            title=f'News {idx}',
            text='news_text',
            date=curr_day - timedelta(days=idx)
        ) for idx in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(all_news)


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


@pytest.fixture
def comment_form_data():
    return {'text': 'new_comment_text'}
