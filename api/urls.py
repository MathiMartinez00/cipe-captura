from django.urls import path
from api.views import ScientistListView, ScientistDetailView, ComplaintListView, ComplaintVoteViewSet, DownloadComplaintsPerCityReportView, DownloadComplaintsPerComplaintTypeReportView
from rest_framework.authtoken import views
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.SimpleRouter()
router.register(r'complaint-votes', ComplaintVoteViewSet)

urlpatterns = [
    path('scientist/', ScientistListView.as_view(), name='scientist-list'),
    path('scientist/<int:scientist_id>/', ScientistDetailView.as_view(), name='scientist-detail'),
    path('get-user-token/', views.obtain_auth_token, name='get-user-token'),
    path('complaints/<int:pk>/', ComplaintListView.as_view(), name='complaint-retrieve-destroy-update'),
    path('complaints/', ComplaintListView.as_view(), name='complaint-list'),
    path('reports/complaints-per-city/', DownloadComplaintsPerCityReportView.as_view(), name='api-complaints-per-city-report'),
    path('reports/complaints-per-complaint-type/', DownloadComplaintsPerComplaintTypeReportView.as_view(), name='api-complaints-per-complaint-type-report'),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html', 'csv'])
