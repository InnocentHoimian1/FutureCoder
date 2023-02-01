from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('search/', views.search, name='search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('profile/', views.profilis, name='profile'),
    path('enrolled_courses/', views.EnrolledCoursesListView.as_view(), name='enrolled_courses'),
    path('user_progress', views.course_progress, name='user_progress'),
    path('user_progress/<int:course_id>/', views.course_progress, name='user_progress'),
    path('enrolled_courses/', views.EnrolledCoursesListView.as_view(), name='enrolled_courses')

]