from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from posts.models import Post, Group, Comment, Follow


from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget


def format_field(self, field):
    return mark_safe(field)


class PostAdminForm(forms.ModelForm):
    text = forms.CharField(
        label='Текст', widget=CKEditorUploadingWidget(
            config_name='ckeditor_post'
        ))


class CommentAdminForm(forms.ModelForm):
    text = forms.CharField(
        label='Текст', widget=CKEditorWidget(
            config_name='ckeditor_comment'
        ))

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'format_text', 'created', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('created', 'group', 'author',)
    list_editable = ('group',)
    form = PostAdminForm
    empty_value_display = '-пусто-'

    def format_text(self, obj):
        return mark_safe(obj.text)

    format_text.short_description = 'Текст'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug', 'group_post_count',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'

    def group_post_count(self, obj) -> int:
        return obj.posts.count()
    group_post_count.short_description = 'Количество записей'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'format_text', 'format_post', 'author', 'created')
    search_fields = ('text',)
    list_filter = ('created', 'author')
    form = CommentAdminForm
    empty_value_display = '-пусто-'

    def format_text(self, obj):
        return format_field(self, obj.text)

    format_text.short_description = 'Текст'

    def format_post(self, obj):
        return format_field(self, obj.post)

    format_post.short_description = 'Пост'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
