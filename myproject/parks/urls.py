from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.personal_space_view, name='personal_space'),
    path('api/update_status/', views.esp_update_status, name='esp_update_status'),
    path('toggle/<int:zone_id>/', views.toggle_zone, name='toggle_zone'),
    path('logs/', views.system_logs, name='system_logs'),
    path('service-mode/', views.enable_service_mode, name='enable_service_mode'),


]
