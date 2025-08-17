from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('upload/', views.material_upload, name='material_upload'),
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('<int:pk>/delete/', views.material_delete, name='material_delete'),
]
