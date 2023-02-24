from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class Tech(models.Model):
    title = models.CharField(
        verbose_name='Технология',
        help_text='Название технологии',
        max_length=200
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание Технологии'
    )
    number = models.IntegerField(
        verbose_name='Порядковый номер',
        unique=True,
        db_index=True,
        help_text='Приоритет расстановки на странице',
    )
    is_studied = models.BooleanField(
        verbose_name='Изучено',
        help_text='Уже изучено или ещё в планах',
        default=False
    )

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('about:tech', kwargs={'number': self.number})

    class Meta:
        verbose_name = 'Технология'
        verbose_name_plural = 'Технологии'
        ordering = ('number',)


class About(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Разработчик',
        help_text='Автор сайта',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание Технологии'
    )
    photo = models.ImageField(
        upload_to='about/',
        verbose_name='Фотограия',
        help_text='Загрузите фото'
    )
    role = models.CharField(
        max_length=150,
        verbose_name='Специальность',
        help_text='Введите специальность',
        blank=True,
    )
    city = models.CharField(
        max_length=50,
        verbose_name='Город',
        help_text='Место проживания',
        blank=True,
    )

    def __str__(self) -> str:
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Разработчик'
        verbose_name_plural = 'Разработчики'
