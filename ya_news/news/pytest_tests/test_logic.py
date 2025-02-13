from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url,
    comment_form_data
):
    client.post(news_detail_url, comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    news_detail_url,
    comment_form_data,
    author,
    news
):
    response = author_client.post(news_detail_url, comment_form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == comment_form_data['text']


def test_user_cant_use_bad_words(author_client, news_detail_url):
    bad_words_data = {'text': f'Test {BAD_WORDS[0]} text'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client,
    comment_id_for_args,
    news_detail_url
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    comment_id_for_args
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client,
    comment_id_for_args,
    comment_form_data,
    news_detail_url
):
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment_id_for_args,
    comment_form_data
):
    old_comment = Comment.objects.get()
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get()
    assert old_comment.text == new_comment.text
