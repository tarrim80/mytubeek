import os
from core.permissions import AuthorPermissionMixin
from core.views import PaginatorListView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, FormView, UpdateView

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


class PostListView(PaginatorListView):
    queryset = Post.objects.annotate(
        author_posts_count=Count('author__posts', distinct=True),
        group_posts_count=Count('group__posts', distinct=True)
    ).select_related('group', 'author').order_by('-created')
    template_name = 'posts/index.html'
    extra_context = {'index_page': True,
                     'title': 'Последние обновления',
                     }


class GroupListView(PaginatorListView):
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        return Post.objects.select_related('author').annotate(
            author_posts_count=Count('author__posts', distinct=True)
        ).filter(group__slug=self.kwargs['slug']).order_by('-created')

    def get_object(self):
        return get_object_or_404(Group, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_object()
        return context


class ProfileListView(PaginatorListView):
    template_name = 'posts/profile.html'

    def get_queryset(self):
        return Post.objects.annotate(
            group_posts_count=Count('group__posts', distinct=True)
        ).select_related('group', 'author').filter(
            author__username=self.kwargs['username']
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs['username'])
        user = self.request.user
        if user.is_authenticated:
            my_posts_flag = author == user
            context['my_posts_flag'] = my_posts_flag
            following = Follow.objects.select_related(
                'author', 'user'
            ).filter(author=author, user=user).exists()
            context['following'] = following
        context['author'] = author
        context['profile'] = True
        return context


class PostDetailView(DetailView):
    template_name = 'posts/post_detail.html'

    def get_object(self):
        return get_object_or_404(Post.objects.annotate(
            author_posts_count=Count('author__posts', distinct=True),
            group_posts_count=Count('group__posts', distinct=True)
        ).prefetch_related('comments__author'), id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(self.request.POST or None)
        return context


class PostCreateView(LoginRequiredMixin, FormView):
    template_name = 'posts/create.html'
    form_class = PostForm
    extra_context = {'is_edit': False}

    def get_success_url(self):
        return reverse_lazy('posts:profile',
                            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)


class PostUpdateView(AuthorPermissionMixin, UpdateView):
    model = Post
    fields = ('text', 'group', 'image',)
    pk_url_kwarg = 'post_id'
    template_name = "posts/create.html"
    extra_context = {'is_edit': True}

    def get_success_url(self):
        return reverse_lazy('posts:post_detail',
                            kwargs={'post_id': self.get_object().id})


class PostDeleteView(AuthorPermissionMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = "posts/delete.html"
    success_url = '/'
    extra_context = {'form_title': 'Подтверждение удаления'}

    def post(self, request, *args, **kwargs):
        if self.get_object().image:
            os.remove(self.get_object().image.path)
        return super().post(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, FormView):
    form_class = CommentForm

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('posts:post_detail',
                            kwargs={'post_id': self.get_object().id})

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = self.get_object()
        comment.save()
        return super().form_valid(form)


class FollowListView(LoginRequiredMixin, PaginatorListView):
    template_name = 'posts/follow.html'

    def get_queryset(self):
        return Post.objects.annotate(
            author_posts_count=Count('author__posts', distinct=True),
            group_posts_count=Count('group__posts', distinct=True)
        ).select_related('author', 'group').filter(
            author__following__user=self.request.user
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['following'] = self.get_queryset().exists()
        context['index'] = False
        context['title'] = 'Посты избранных авторов'
        return context


class ProfileFollowView(LoginRequiredMixin, View):
    def dispatch(self, request, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        author = get_object_or_404(User, username=kwargs['username'])
        if author != request.user:
            Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:follow_index')


class ProfileUnfollowView(LoginRequiredMixin, View):
    def dispatch(self, request, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        get_object_or_404(
            Follow,
            user=request.user,
            author__username=kwargs['username']
        ).delete()
        return redirect('posts:follow_index')
