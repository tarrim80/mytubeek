from django import forms
from django.contrib import admin

from ckeditor.widgets import CKEditorWidget

from about.models import Tech, About


class TechAdminForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание', widget=CKEditorWidget(
            config_name='ckeditor_post'
        ))


class TechAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_studied', 'number',)
    search_fields = ('title',)
    form = TechAdminForm
    empty_value_display = '-пусто-'


class AboutAdminForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание', widget=CKEditorWidget(
            config_name='ckeditor_post'
        ))


class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    form = AboutAdminForm
    empty_value_display = '-пусто-'


admin.site.register(Tech, TechAdmin)
admin.site.register(About, AboutAdmin)
