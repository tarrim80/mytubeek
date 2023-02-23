from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from ckeditor.widgets import CKEditorWidget

from about.models import Tech


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

    def description(self, obj):
        return mark_safe(self, obj.description)

    description.short_description = 'Описание'


admin.site.register(Tech, TechAdmin)
