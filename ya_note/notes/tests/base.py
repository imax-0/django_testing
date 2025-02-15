from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='test_author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='test_not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Test title',
            text='Test text',
            slug='test-slug',
            author=cls.author
        )
        cls.homepage_url = reverse('notes:home')
        cls.note_detail_url = reverse('notes:detail', args=(cls.note.slug, ))
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug, ))
        cls.note_delete_url = reverse('notes:delete', args=(cls.note.slug, ))
        cls.note_add_url = reverse('notes:add')
        cls.note_list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
