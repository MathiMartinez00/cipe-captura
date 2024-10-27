from django.core.files.base import ContentFile
from rest_framework import serializers
from api.models import Complaint, ComplaintVote
import base64


class ComplaintSerializerRead(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        depth = 1


class ComplaintSerializerWrite(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Complaint
        fields = '__all__'

    def save(self):
        complaint = Complaint.objects.create(
            complaint_type=self.validated_data['complaint_type'],
            description=self.validated_data['description'],
            city=self.validated_data['city'],
            latitude=self.validated_data['latitude'],
            longitude=self.validated_data['longitude'],
            altitude=self.validated_data['altitude'],
            accuracy=self.validated_data['accuracy'],
            road_type=self.validated_data.get('road_type', None),
        )
        photo_base64_string = self.validated_data.get('photo_base64', None)
        if photo_base64_string:
            photo_file = ContentFile(base64.b64decode(photo_base64_string), name='temp.png')
            complaint.photo.save("test.png", photo_file)
        return complaint


class ComplaintVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintVote
        fields = '__all__'