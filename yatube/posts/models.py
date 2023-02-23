from django.db import models
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from ckeditor_uploader.fields import RichTextUploadingField

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название',
        help_text='Название группы',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        help_text='Уникальный адрес группы',
        unique=True
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    text = RichTextUploadingField(
        config_name='ckeditor_post',
        verbose_name='Текст',
        help_text='Текст поста'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Создатель записи'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой относится пост'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Изображение',
        help_text='Загрузите изображение'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        default_related_name = 'posts'

    def __str__(self) -> str:
        return mark_safe(f'{self.text[:15]}...')


class Comment(CreatedModel):
    text = models.TextField(
        max_length=5000,
        verbose_name='Текст',
        help_text='Текст комментария'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Комментатор',
        help_text='Создатель комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        help_text='Пост, к которому относится комментарий'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self) -> str:
        return mark_safe(f'{self.text[:15]}...')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Пользователь, который оформил подписку',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор контента',
        help_text='Пользователь, на которого оформлена подписка',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follower'
            ),
        )

    def __str__(self) -> str:
        return (f'{self.user} подписан на посты {self.author}')
