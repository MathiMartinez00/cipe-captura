from django.urls import path
from api.views import ComplaintTypeListView, ComplaintListCreateView, ComplaintVoteViewSet, DownloadComplaintsPerCityReportView, DownloadComplaintsPerComplaintTypeReportView, CityListView, GetUserTokenView
from rest_framework.authtoken import views
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.SimpleRouter()
router.register(r'complaint-votes', ComplaintVoteViewSet)
router.register(r'complaints', ComplaintListCreateView, 'complaints')

urlpatterns = [
    path('users/token/', GetUserTokenView.as_view(), name='get-user-token'),
    path('cities/', CityListView.as_view(), name='city-list'),
    path('complaint-types/', ComplaintTypeListView.as_view(), name='complaint-type-list'),
    path('reports/complaints-per-city/', DownloadComplaintsPerCityReportView.as_view(), name='api-complaints-per-city-report'),
    path('reports/complaints-per-complaint-type/', DownloadComplaintsPerComplaintTypeReportView.as_view(), name='api-complaints-per-complaint-type-report'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += router.urls
