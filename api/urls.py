from django.urls import path
from api.views import ScientistListView, ScientistDetailView, ComplaintListView, ComplaintVoteViewSet
from rest_framework.authtoken import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'complaint-votes', ComplaintVoteViewSet)

urlpatterns = [
    path('scientist/', ScientistListView.as_view(), name='scientist-list'),
    path('scientist/<int:scientist_id>/', ScientistDetailView.as_view(), name='scientist-detail'),
    path('get-user-token/', views.obtain_auth_token, name='get-user-token'),
    path('complaints/<int:pk>/', ComplaintListView.as_view(), name='complaint-retrieve-destroy-update'),
    path('complaints/', ComplaintListView.as_view(), name='complaint-list'),
]

urlpatterns += router.urls
