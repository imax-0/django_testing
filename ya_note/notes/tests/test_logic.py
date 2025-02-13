from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING, Note

User = get_user_model()


class TestLogic(TestCase):
    FORM_DATA = {
        'title': 'New test title',
        'text': 'New test text',
        'slug': 'new-test-slug'
    }

    def create_note(self):
        return Note.objects.create(
            title='Test title',
            text='Test text',
            slug='test-slug',
            author=self.author
        )

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='test_author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='test_not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.FORM_DATA['title'])
        self.assertEqual(new_note.text, self.FORM_DATA['text'])
        self.assertEqual(new_note.slug, self.FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.FORM_DATA)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = self.create_note()
        url = reverse('notes:add')
        self.FORM_DATA['slug'] = note.slug
        response = self.author_client.post(url, data=self.FORM_DATA)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.FORM_DATA.pop('slug')
        response = self.author_client.post(url, data=self.FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(
            Note.objects.get().slug,
            slugify(self.FORM_DATA['title'])
        )

    def test_other_user_cant_edit_note(self):
        note = self.create_note()
        url = reverse('notes:edit', kwargs={'slug': note.slug})
        response = self.not_author_client.post(url, data=self.FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        note = self.create_note()
        url = reverse('notes:delete', kwargs={'slug': note.slug})
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        note = self.create_note()
        url = reverse('notes:delete', kwargs={'slug': note.slug})
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
