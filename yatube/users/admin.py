
from django.contrib import admin

from users.models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact', 'title', 'link',)
    search_fields = ('contact',)
    empty_value_display = '-пусто-'


admin.site.register(Contact, ContactAdmin)
