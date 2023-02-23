from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django.forms import ModelForm, CharField

from posts.models import Comment, Post


class PostForm(ModelForm):
    # text = CharField(label='Текст', widget=CKEditorUploadingWidget(
    #     config_name='ckeditor_post'))

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        # widgets = {
        #     'text': CKEditorUploadingWidget(
        #         attrs={
        #             'placeholder': ('Введите текст сообщения '
        #                             '(не более 5000 знаков)...')}
        #     ),
        # }


class CommentForm(ModelForm):
    text = CharField(label='Текст', widget=CKEditorWidget(
        config_name='ckeditor_comment'))

    class Meta:
        model = Comment
        fields = ('text',)
        # widgets = {
        #     'text': CKEditorWidget()(
        #         attrs={
        #             'rows': 3,
        #             'placeholder': ('Введите текст комментария '
        #                             '(не более 5000 знаков)...')
        #         }
        #     ),
        # }
