from django.contrib import admin
from api.models import UserToken, Complaint, ComplaintType, RoadType, City

# Register your models here.
admin.site.register(UserToken)
admin.site.register(Complaint)
admin.site.register(ComplaintType)
admin.site.register(RoadType)
admin.site.register(City)
