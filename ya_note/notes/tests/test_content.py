from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import Note, NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.auth_user = User.objects.create(username='test_auth_user')
        cls.author = User.objects.create(username='test_author')
        cls.note = Note.objects.create(
            title='Test title',
            text='Test text',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        self.client.force_login(self.auth_user)
        response = self.client.get(url)
        self.assertFalse(self.note in response.context['object_list'])

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
        )
        for name, kwargs in urls:
            url = reverse(name, kwargs=kwargs)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
