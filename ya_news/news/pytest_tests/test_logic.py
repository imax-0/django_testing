from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


COMMENT_TEXT = 'test_comment_text'
COMMENT_FORM_DATA = {
    'text': COMMENT_TEXT
}


def db_cleanup():
    News.objects.all().delete
    Comment.objects.all().delete


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url
):
    """Проверка того, что анонимный юзер не может создать комментарий"""
    db_cleanup()
    client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    news_detail_url,
    author,
    news
):
    """Проверка того, что залогиненный юзер может создать комментарий"""
    db_cleanup()
    author_client.post(news_detail_url, data=COMMENT_FORM_DATA)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == COMMENT_TEXT


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(
    author_client,
    news_detail_url,
    bad_word
):
    """Проверка того, что нельзя создать комментарий с запрещённым словом"""
    db_cleanup()
    bad_words_data = {'text': f'Test {bad_word} text'}
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
    comment,
    comment_delete_url
):
    """Проверка того, что автор может удалить свой комментарий"""
    assert Comment.objects.count() == 1
    author_client.post(comment_delete_url)
    assert Comment.objects.count() == 0
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    comment,
    comment_delete_url
):
    """Проверка того, что пользователь не может удалить чужой комментарий"""
    assert Comment.objects.count() == 1
    response = not_author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.filter(id=comment.id).exists()
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.author == comment.author
    assert new_comment.created == comment.created
    assert new_comment.text == comment.text


def test_author_can_edit_comment(
    author_client,
    comment,
    comment_edit_url
):
    """Проверка того, что автор может отредактировать свой комментарий"""
    assert Comment.objects.count() == 1
    author_client.post(comment_edit_url, data=COMMENT_FORM_DATA)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.author == comment.author
    assert new_comment.created == comment.created
    assert new_comment.text == COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    comment_edit_url
):
    """Проверка того, что юзер не может отредактировать чужой комментарий"""
    assert Comment.objects.count() == 1
    response = not_author_client.post(comment_edit_url, data=COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.author == comment.author
    assert new_comment.created == comment.created
    assert new_comment.text == comment.text
