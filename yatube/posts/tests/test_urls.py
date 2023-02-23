from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.no_author = User.objects.create_user(username='NoAuthor')
        Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Описание тестовой группы'
        )

        Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_posts_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_names = {
            'index': '/',
            'group_list': '/group/test_group/',
            'profile': '/profile/Author/',
            'post_detail': '/posts/1/'
        }
        for url_name, address in url_names.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_follow_url_exists_at_desired_location_authorized(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """
        Страница /post_edit/ поста доступна авторизованному автору поста.
        """
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_not_exists_at_desired_location_authorized(self):
        """Страница редактирования поста недоступна не автору поста."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.no_author)
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertRedirects(
            response, '/')

    def test_profile_follow_url_right_redirected(self):
        """Запрос подписки на автора правильно перенаправлен."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.no_author)
        response = self.authorized_client.get(
            f'/profile/{PostsURLTests.user.username}/follow/'
        )
        self.assertRedirects(
            response, '/follow/')

    def test_profile_unfollow_url_right_redirected(self):
        """Запрос отписки от автора правильно перенаправлен."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.no_author)
        Follow.objects.create(
            user=self.no_author,
            author=self.user)
        response = self.authorized_client.get(
            f'/profile/{PostsURLTests.user.username}/unfollow/')
        self.assertRedirects(
            response, '/follow/')

    def test_null_url_throw_error_404(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get(None)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/Author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create.html',
            '/posts/1/delete/': 'posts/delete.html',
            '/create/': 'posts/create.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


class IndexPageCacheTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_TEST_ITEMS = 2
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Описание тестовой группы'
        )

        for i in range(1, cls.POSTS_TEST_ITEMS + 1):
            Post.objects.create(
                text=f'Тестовый текст поста №{i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_index_page(self):
        """Страница index_page кэшируется."""
        response = self.guest_client.get(reverse('posts:index'))
        post = Post.objects.get(id=self.POSTS_TEST_ITEMS)
        content = response.content
        post.delete()
        response_cache = self.guest_client.get(reverse('posts:index'))
        content_cache = response_cache.content
        self.assertEqual(
            content,
            content_cache,
            'Страница не кэширована'
        )
        cache.clear()
        response_no_cache = self.guest_client.get(reverse('posts:index'))
        content_no_cache = response_no_cache.content
        self.assertNotEqual(
            content_cache,
            content_no_cache,
            'Страница не обновлена'
        )
