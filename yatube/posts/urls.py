from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from posts import views

app_name = 'posts'
urlpatterns = [
    path(
        '',
        cache_page(
            settings.CACHE_TIMEOUT_LISTVIEW, key_prefix='index_page'
        )(views.PostListView.as_view()),
        name='index'
    ),
    path(
        'group/<slug:slug>/',
        views.GroupListView.as_view(),
        name='group_list'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'follow/',
        views.FollowListView.as_view(),
        name='follow_index'
    ),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollowView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollowView.as_view(),
        name='profile_unfollow'
    ),
]
