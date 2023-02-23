import shutil
import tempfile
from typing import Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_post_create(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовое создание поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': f'{PostFormTests.user}'}),
            msg_prefix='Неправильное перенаправление после создания поста'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Новая запись не создалась'
        )
        self.check_post_exists(
            form_data,
            'Неверные аттрибуты созданного поста'
        )

    def test_post_edit(self):
        """Валидная форма редактирует существующий пост"""
        uploaded = SimpleUploadedFile(
            name='small_create.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        uploaded2 = SimpleUploadedFile(
            name='small_edit.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=uploaded
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактированный текст',
            'group': self.post.group.id,
            'image': uploaded2,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}),
            msg_prefix='Неправильное перенаправление '
            'после редактирования поста'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'При редактировании поста изменилось количество постов'
        )
        self.check_post_exists(
            form_data,
            'Неверные аттрибуты редактированного поста'
        )

    def check_post_exists(self, form_data: Dict[str, str], msg: str) -> None:
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            author=self.user,
            group=form_data['group'],
            image=f'posts/{form_data["image"]}'
        ).exists(), msg)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_comment_create_authorized_user(self):
        """Авторизованный пользователь создает новый комментарий."""
        comments_count = self.post.comments.count()

        form_data = {
            'text': 'Тестовое создание комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}),
            msg_prefix=('Неправильное перенаправление '
                        'после создания комментария')
        )
        self.assertEqual(
            self.post.comments.count(),
            comments_count + 1,
            'Новый комментарий не создался'
        )
        self.assertTrue(
            self.post.comments.filter(
                post__id=self.post.id,
                author=self.user,
                text=form_data['text']
            ).exists(),
            'Неверные аттрибуты созданного комментария'
        )

    def test_comment_create_guest_user(self):
        """Неавторизованный пользователь не может создать новый комментарий"""
        comments_count = self.post.comments.count()

        form_data = {
            'text': 'Тестовое создание комментария',
            'author': self.user,
        }
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            self.post.comments.count(),
            comments_count,
            'Новый комментарий создался'
        )
