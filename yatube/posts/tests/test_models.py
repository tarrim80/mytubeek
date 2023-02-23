from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post, Comment, Follow


User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name(self):
        field_verboses = {
            'title': 'Название',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(
                        field).verbose_name, expected_value
                )

    def test_help_text(self):
        field_help_text = {
            'title': 'Название группы',
            'slug': 'Уникальный адрес группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text, expected_value
                )


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, состоящий более, чем из 15 символов',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(f'{self.post.text[:15]}...', str(self.post))

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата и время создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field).verbose_name, expected_value
                )

    def test_help_text(self):
        field_help_text = {
            'text': 'Текст поста',
            'created': 'Дата и время вносятся атоматически',
            'author': 'Создатель записи',
            'group': 'Группа, к которой относится пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_post = User.objects.create_user(username='post_author')
        cls.user_comment = User.objects.create_user(username='comment_autor')
        cls.post = Post.objects.create(
            author=cls.user_post,
            text='Тестовый пост, состоящий более, чем из 15 символов',
        )
        cls.comment = Comment.objects.create(
            author=cls.user_comment,
            post=cls.post,
            text='Тестовый комментарий тестового поста'
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(f'{self.comment.text[:15]}...', str(self.comment))

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата и время создания',
            'author': 'Комментатор',
            'post': 'Пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(
                        field).verbose_name, expected_value
                )

    def test_help_text(self):
        field_help_text = {
            'text': 'Текст комментария',
            'created': 'Дата и время вносятся атоматически',
            'author': 'Создатель комментария',
            'post': 'Пост, к которому относится комментарий',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    expected_value
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth_follower')
        cls.user2 = User.objects.create_user(username='auth_following')
        cls.follow = Follow.objects.create(
            author=cls.user2,
            user=cls.user1,
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(
            f'{self.user1} подписан на посты {self.user2}', str(self.follow))

    def test_verbose_name(self):
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор контента',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(
                        field).verbose_name, expected_value
                )

    def test_help_text(self):
        field_help_text = {
            'user': 'Пользователь, который оформил подписку',
            'author': 'Пользователь, на которого оформлена подписка',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(
                        field).help_text, expected_value
                )
