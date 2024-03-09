from django.urls import path
from api.views import ScientistListView, ScientistDetailView

urlpatterns = [
    path('scientist/', ScientistListView.as_view(), name='scientist-list'),
    path('scientist/<int:scientist_id>/', ScientistDetailView.as_view(), name='scientist-detail')
]