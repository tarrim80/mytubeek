from django.urls import path
from about import views

app_name = 'about'

urlpatterns = [
    path('author/<int:pk>/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/<int:number>/', views.AboutTechView.as_view(), name='tech'),
]
