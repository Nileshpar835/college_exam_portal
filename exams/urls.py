from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<int:quiz_id>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('result/<int:result_id>/', views.quiz_result, name='quiz_result'),
    path('results/', views.Result, name='results'),
]
