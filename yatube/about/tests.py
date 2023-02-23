from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_names = {
            'author': '/about/author/',
            'tech': '/about/tech/'
        }
        for url_name, address in url_names.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
