from django.db import models

from about.models import About


class Contact(models.Model):
    contact = models.ForeignKey(
        About,
        verbose_name='Разработчик',
        help_text='Контактное лицо',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=50,
        verbose_name='Наименование ссылки',
        help_text='Назовите ресурс',
        blank=True,
        null=True,
    )
    link = models.URLField(
        verbose_name='URL-адрес',
        help_text='URL-адрес ресурса',
    )

    def __str__(self) -> str:
        return self.contact.user.get_full_name()

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
