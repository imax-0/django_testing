from notes.forms import NoteForm
from .base import BaseTestCase


class TestContent(BaseTestCase):

    def test_notes_list_for_author(self):
        """Проверка того, что автор видит свои записи"""
        response = self.author_client.get(self.note_list_url)
        self.assertTrue(self.note in response.context['object_list'])

    def test_notes_list_for_different_users(self):
        """Проверка того, что пользователи не видят чужие записи"""
        response = self.not_author_client.get(self.note_list_url)
        self.assertFalse(self.note in response.context['object_list'])

    def test_pages_contains_form(self):
        """Проверка отображения формы при добавлении и редактировании записи"""
        urls = (
            self.note_add_url,
            self.note_edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
