# Generated by Django 4.1.7 on 2023-02-22 09:37

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_alter_comment_text_alter_post_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Текст поста', verbose_name='Текст'),
        ),
    ]
