from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from users.forms import CreationForm


User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Author')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_exists_at_desired_location(self):
        """Страница входа и регистрации доступна любому пользователю."""
        url_names = {
            'login': '/auth/login/',
            'signup': '/auth/signup/'
        }
        for url_name, address in url_names.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_urls_exists_at_desired_location_authorized(self):
        """Страница доступна авторизованному пользователю."""

        url_names = {
            'password_change': '/auth/password_change/',
            'password_change_done': '/auth/password_change/done/',
            'logout': '/auth/logout/',
            'password_reset': '/auth/password_reset/',
            'password_reset_done': '/auth/password_reset/done/',
            'password_reset_confirm': '/auth/reset/<uidb64>/<token>/',
            'password_reset_complete': '/auth/reset/done/',
        }
        for url_name, address in url_names.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


class UserSignupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user1')
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_user_create(self):
        """Валидная форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'User',
            'last_name': 'Second',
            'username': 'user2',
            'email': 'user2@yatube.com',
            'password1': 'Strongpassword',
            'password2': 'Strongpassword'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index'),
            msg_prefix='Неправильное перенаправление после '
            'создания пользователя'
        )
        self.assertEqual(
            User.objects.count(),
            users_count + 1,
            'Новый пользователь не создан'
        )
