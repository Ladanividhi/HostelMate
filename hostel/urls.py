from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    gatepass_view, get_available_beds, profile_setup, room_details, 
    select_vacancy, signup_view, vacancy_list, view_gatepasses, 
    view_requests, welcome
)

urlpatterns = [
    path('profile-setup/', profile_setup, name='profile_setup'),
    path('room_details/', room_details, name='room_details'),
    path('view-requests/', view_requests, name='view_requests'),
    
    path("selection/", views.feedback_selection, name="feedback_selection"),
    path("form/", views.feedback_form, name="feedback_form"),
    path("submit/", views.submit_feedback, name="submit_feedback"),
    
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    
    path('feedback/', views.feedback_view, name='feedback'),  # Ensure name='feedback' exists
    path('requestbox/', views.requestbox_view, name='requestbox'),
    path("view_requests/", view_requests, name="view_requests"),
    path('view_past_feedbacks/', views.view_past_feedbacks, name='view_past_feedbacks'),
    
    path("vacancy/", vacancy_list, name="vacancy_list"),
    path("select-vacancy/", select_vacancy, name="select_vacancy"),
    path('signup/', signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('gatepass/', gatepass_view, name='gatepass'),
    path("view_gatepasses/", view_gatepasses, name="view_gatepasses"),
    path('feedback_analysis/', views.feedback_analysis, name='feedback_analysis'),
    
    path('requests/', views.view_all_requests, name='view_all_requests'),  # Ensure this exists
    path('vacancies/', views.view_all_vacancies, name='view_all_vacancies'),
    path('gatepasses/', views.view_all_gatepasses, name='view_all_gatepasses'),
    path('manage_users/', views.manage_users, name='manage_users'),
    
    path('get_available_beds/', get_available_beds, name='get_available_beds'),
    path('', welcome, name='welcome'),
]
