from django.db import models
from django.urls import reverse


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
