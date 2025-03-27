from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('trainer/register/', views.trainer_register, name='trainer_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('become-trainer/', views.become_trainer, name='become_trainer'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<slug:course_slug>/', views.course_details, name='course_details'),
    path('courses/<slug:course_slug>/update/', views.course_update, name='course_update'),
    path('courses/<slug:course_slug>/delete/', views.course_delete, name='course_delete'),
]