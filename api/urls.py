from django.urls import path
from api.views import ScientistListView, ScientistDetailView, GetUserToken, ComplaintListView
from rest_framework.authtoken import views

urlpatterns = [
    path('scientist/', ScientistListView.as_view(), name='scientist-list'),
    path('scientist/<int:scientist_id>/', ScientistDetailView.as_view(), name='scientist-detail'),
    path('get-user-token/', views.obtain_auth_token, name='get-user-token'),
    path('complaints/<int:pk>/', ComplaintListView.as_view(), name='complaint-retrieve-destroy-update'),
    path('complaints/', ComplaintListView.as_view(), name='complaint-list'),
]
