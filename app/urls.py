from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('registration/edit/<str:scientist_slug>', views.edit_scientist, name='edit_scientist'),
    path('success/', views.success_registration),
    path('map/', views.map_scientists, name='map'),
    path('map/filter_map/', views.filter_map, name='filter_map'),
    path('user-registration/', views.user_registration, name='user_registration'),
    path('user-login/', views.user_login, name='user_login'),
    path('user-logout/', views.user_logout, name='user_logout'),
    path('view-user-info/', views.view_api_key, name='view_api_key'),
    path('graphs/', views.graphs_page, name='graphs'),
    path('reports/csv/complaints-per-city', views.complaints_per_city_csv_report, name='complaints-per-city-csv-report'),
    path('reports/json/complaints-per-city', views.complaints_per_city_json_report, name='complaints-per-city-json-report'),
    path('reports/csv/complaints-per-complaint-type', views.complaints_per_complaint_type_csv_report, name='complaints-per-complaint-type-csv-report'),
    path('reports/json/complaints-per-complaint-type', views.complaints_per_complaint_type_json_report, name='complaints-per-complaint-type-json-report'),
]
