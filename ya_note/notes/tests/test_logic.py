from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING, Note
from .base import BaseTestCase


class TestLogic(BaseTestCase):
    FORM_DATA = {
        'title': 'New test title',
        'text': 'New test text',
        'slug': 'new-test-slug'
    }

    def db_cleanup(self):
        Note.objects.all().delete()

    def test_user_can_create_note(self):
        """Проверка того, что пользователь может создать запись"""
        self.db_cleanup()
        self.author_client.post(
            self.note_add_url,
            data=self.FORM_DATA
        )
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.FORM_DATA['title'])
        self.assertEqual(new_note.text, self.FORM_DATA['text'])
        self.assertEqual(new_note.slug, self.FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Проверка того, что анонимный пользователь не может создать запись"""
        self.db_cleanup()
        self.client.post(self.note_add_url, data=self.FORM_DATA)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        """
        Проверка того, что при попытке создать запись с неуникальным слагом,
        запись не создастся
        """
        self.assertEqual(Note.objects.count(), 1)
        self.FORM_DATA['slug'] = self.note.slug
        response = self.author_client.post(
            self.note_add_url,
            data=self.FORM_DATA
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note.title)
        self.assertEqual(new_note.text, self.note.text)
        self.assertEqual(new_note.slug, self.note.slug)
        self.assertEqual(new_note.author, self.note.author)

    def test_empty_slug(self):
        """
        Проверка того, что при создании записи с пустым слагом,
        запись создастся
        """
        self.db_cleanup()
        self.FORM_DATA.pop('slug')
        self.author_client.post(
            self.note_add_url,
            data=self.FORM_DATA
        )
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(
            Note.objects.get().slug,
            slugify(self.FORM_DATA['title'])
        )

    def test_other_user_cant_edit_note(self):
        """Проверка того, что пользователь не может изменить чужую запись"""
        self.assertEqual(Note.objects.count(), 1)
        response = self.not_author_client.post(
            self.note_edit_url,
            data=self.FORM_DATA
        )
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(new_note.title, self.note.title)
        self.assertEqual(new_note.text, self.note.text)
        self.assertEqual(new_note.slug, self.note.slug)
        self.assertEqual(new_note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Проверка того, что автор может удалить собственную запись"""
        self.assertEqual(Note.objects.count(), 1)
        self.author_client.post(self.note_delete_url)
        self.assertEqual(Note.objects.count(), 0)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_other_user_cant_delete_note(self):
        """Проверка того, что пользователь не может удалить чужую запись"""
        self.assertEqual(Note.objects.count(), 1)
        response = self.not_author_client.post(self.note_delete_url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(new_note.title, self.note.title)
        self.assertEqual(new_note.text, self.note.text)
        self.assertEqual(new_note.slug, self.note.slug)
        self.assertEqual(new_note.author, self.note.author)
