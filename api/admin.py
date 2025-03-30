from django.contrib import admin
from api.models import Complaint, ComplaintType, RoadType, City, ComplaintVote

# Register your models here.
admin.site.register(Complaint)
admin.site.register(ComplaintType)
admin.site.register(ComplaintVote)
admin.site.register(RoadType)
admin.site.register(City)
