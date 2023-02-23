import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment, Follow

from yatube.settings import POSTS_COUNT_ON_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PostViewTests.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostViewTests.post.author}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostViewTests.post.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostViewTests.post.id}'}
            ): 'posts/create.html',
            reverse(
                'posts:post_delete',
                kwargs={'post_id': f'{PostViewTests.post.id}'}
            ): 'posts/delete.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template, 'Используется неправильный шаблон'
                )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        check_post = response.context['page_obj'][0]
        self.check_context_attrs(check_post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{PostViewTests.group.slug}'}
        ))
        check_post = response.context['page_obj'][0]
        self.check_context_attrs(check_post)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': f'{PostViewTests.post.author}'}
        ))
        check_post = response.context['page_obj'][0]
        self.check_context_attrs(check_post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{PostViewTests.post.id}'}
        ))
        check_post = response.context['post']
        self.check_context_attrs(check_post)

    def check_context_attrs(self, check_post: Post) -> None:
        context_attrs = {
            check_post.text: self.post.text,
            check_post.author: self.post.author,
            check_post.group: self.post.group,
            check_post.image: self.post.image,
            check_post.id: self.post.id,
        }
        for check_post_attr, source_post_attr in context_attrs.items():
            with self.subTest(check_post_attr=check_post_attr):
                self.assertEqual(check_post_attr, source_post_attr)

    def test_post_detail_show_comments(self):
        """На странице post_detail отображаются комментарии к посту"""
        comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=PostViewTests.user,
            post=PostViewTests.post
        )
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{PostViewTests.post.id}'}
        ))
        self.assertEqual(response.context['post'], comment.post,
                         'Тестовый комментарий не выведен на страницу поста')

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{PostViewTests.post.id}'}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Выведено неправильное поле формы')
        self.assertTrue(response.context['is_edit'], 'Неверное значение флага')
        self.assertEqual(
            response.context['post'].id,
            self.post.id,
            'Выведен не тот пост'
        )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create',
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Выведено неправильное поле формы'
                )
        self.assertFalse(
            response.context['is_edit'], 'Неверное значение флага')

    def test_post_delete_show_correct_context(self):
        """Шаблон post_delete сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': PostViewTests.post.id}
        ))
        template_text = {
            'form_title': 'Подтверждение удаления',
        }
        for value, expected in template_text.items():
            with self.subTest(value=value):
                form_field = response.context[value]
                self.assertEqual(
                    form_field,
                    expected,
                    'Выведено неправильное значение контекста'
                )
        self.assertEqual(
            response.context['post'].id,
            self.post.id,
            'Попытка удаления не того поста'
        )


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.GROUPS_COUNT_FOR_TESTS: int = 2
        cls.POSTS_COUNT_FOR_TESTS: int = 13
        cls.POSTS_COUNT_ON_LAST_PAGE: int = (
            cls.POSTS_COUNT_FOR_TESTS % POSTS_COUNT_ON_PAGE
        )
        cls.NUMBER_OF_LAST_PAGE: int = (
            cls.POSTS_COUNT_FOR_TESTS // POSTS_COUNT_ON_PAGE + 1
        )
        cls.groups: list = []
        cls.posts: list = []
        cls.user = User.objects.create_user(username='auth')
        for i in range(1, cls.GROUPS_COUNT_FOR_TESTS + 1):
            cls.groups.append(Group.objects.create(
                title=f'Тестовая группа {i}',
                slug=f'test_slug{i}',
                description=f'Тестовое описание группы {i}',
            ))
        for i in range(1, cls.POSTS_COUNT_FOR_TESTS + 1):
            cls.posts.append(Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.groups[0],
            ))

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()
        self.paginator_page_reverse_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PaginatorTests.groups[0].slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorTests.user}
            ),
        )

    def test_pages_with_paginator(self):
        """Страницы с паджинатором сформированы корректно"""
        for reverse_name in self.paginator_page_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response_page = self.authorized_client.get(reverse_name)
                response_last_page = self.authorized_client.get(
                    reverse_name + f'?page={self.NUMBER_OF_LAST_PAGE}'
                )
                self.assertEqual(
                    len(response_page.context['page_obj']),
                    POSTS_COUNT_ON_PAGE,
                    'Первая страница содержит неверное количество постов'
                )
                self.assertEqual(
                    len(response_last_page.context['page_obj']),
                    self.POSTS_COUNT_ON_LAST_PAGE,
                    'Последняя страница содержит неверное количество постов'
                )

    def test_correct_group_post(self):
        """Пост не попал в группу, для которой не был предназначен"""
        response = self.authorized_client.get(
            self.paginator_page_reverse_names[1]
        )
        post_group = response.context['page_obj'][0].group
        self.assertNotEqual(
            post_group,
            PaginatorTests.groups[1],
            'Пост попал в группу, для которой не был предназначен'
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.user3 = User.objects.create_user(username='auth3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = (Post.objects.create(
            author=cls.user1,
            text='Тестовый пост',
            group=cls.group,
        ))

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)
        cache.clear()

    def test_create_followings(self):
        """
        Авторизованный пользователь может пописываться на других пользователей
        """

        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': FollowTests.user1}
        ))
        subscibe = Follow.objects.filter(
            user=FollowTests.user2,
            author=FollowTests.user1
        )
        self.assertTrue(
            subscibe.exists(),
            ('Авторизованный пользователь не смог'
             ' подписаться на автора тестового поста')
        )

    def test_remove_followings(self):
        """
        Авторизованный пользователь может удалять авторов из подписок
        """

        Follow.objects.create(
            user=FollowTests.user2,
            author=FollowTests.user1
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': FollowTests.user1}
        ))

        unsubscibe = Follow.objects.filter(
            user=FollowTests.user2,
            author=FollowTests.user1
        )
        self.assertFalse(
            unsubscibe.exists(),
            ('Авторизованный пользователь не смог '
             'удалить из подписок автора тестового поста')
        )

    def test_new_post_on_feed_follower(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан
        """

        Follow.objects.create(
            user=FollowTests.user2,
            author=FollowTests.user1,
        )

        response_follower = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertTrue(response_follower.context['following'],
                        ('Новая запись пользователя не появляется в '
                        'ленте того, кто на него подписан'))

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user3)
        response_unfollower = self.authorized_client.get(reverse(
            'posts:follow_index'))
        self.assertFalse(response_unfollower.context['following'],
                         ('Новая запись пользователя появляется в ленте тех, '
                         'кто на него не подписан'))

        self.assertNotEqual(
            response_follower.content,
            response_unfollower.content,
            'Ленты подписанного и неподписанного пользователей одинаковы'
        )
