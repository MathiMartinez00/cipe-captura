from django.urls import path
from api.views import ScientistController

urlpatterns = [
    path('scientist/', ScientistController.as_view(), name='scientist')
]