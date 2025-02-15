from http import HTTPStatus

from .base import BaseTestCase


class TestRoutes(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.PUBLIC_URLS = (
            cls.homepage_url,
            cls.login_url,
            cls.logout_url,
            cls.signup_url,
        )
        cls.AUTHORIZED_URLS = (
            cls.note_add_url,
            cls.note_list_url,
            cls.success_url,
        )
        cls.AUTHOR_URLS = (
            cls.note_detail_url,
            cls.note_edit_url,
            cls.note_delete_url,
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступности публичных страниц анонимным пользователям"""
        for url in self.PUBLIC_URLS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверка доступности страниц для авторизованных пользователей"""
        for url in self.AUTHORIZED_URLS:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Проверка доступности приватных страниц авторам записей
        и недоступности другим пользователям
        """
        clietns_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for curr_client, status in clietns_statuses:
            for url in self.AUTHOR_URLS:
                with self.subTest(url=url):
                    response = curr_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа на страницу логина анонимных пользователей"""
        for url in self.AUTHORIZED_URLS + self.AUTHOR_URLS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{self.login_url}?next={url}')
