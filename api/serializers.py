import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from api.models import Complaint, ComplaintVote, City
from django.db.models import Count

class ComplaintSerializerRead(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(required=False, allow_blank=True)
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = ['id', 'complaint_type', 'description', 'city', 'latitude', 'longitude', 'road_type', 'created_at', 'photo_base64', 'votes']
        depth = 1

    def get_votes(self, obj):
        votes = obj.votes.all()
        if votes:
            votes_count = {
                'Y': votes.filter(vote_type='Y').count(),
                'N': votes.filter(vote_type='N').count(),
            }
            return votes_count
        else:
            return {
                'Y': 0,
                'N': 0,
            }
            


class ComplaintSerializerWrite(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Complaint
        fields = ['complaint_type', 'description', 'city', 'latitude', 'longitude', 'road_type', 'created_at', 'photo_base64']

    def save(self):
        complaint = Complaint.objects.create(
            complaint_type=self.validated_data['complaint_type'],
            description=self.validated_data['description'],
            city=self.validated_data['city'],
            latitude=self.validated_data['latitude'],
            longitude=self.validated_data['longitude'],
            altitude=0,
            accuracy=0,
            road_type=self.validated_data.get('road_type', None),
            captura_id=self.validated_data.get('captura_id', None)
        )
        photo_base64_string = self.validated_data.get('photo_base64', None)
        if photo_base64_string:
            photo_file = ContentFile(base64.b64decode(photo_base64_string), name='temp.png')
            complaint.photo.save("test.png", photo_file)
        return complaint


class ComplaintVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintVote
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']