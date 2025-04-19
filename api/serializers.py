import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from api.models import Complaint, ComplaintVote, City, ComplaintType
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from typing import TypedDict

class VoteCount(TypedDict):
    Y: int
    N: int

class ComplaintSerializerWrite(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Complaint
        fields = ['complaint_type', 'description', 'city', 'latitude', 'longitude', 'created_at', 'photo_base64']

    def save(self):
        complaint = Complaint.objects.create(
            complaint_type=self.validated_data['complaint_type'],
            description=self.validated_data['description'],
            city=self.validated_data['city'],
            latitude=self.validated_data['latitude'],
            longitude=self.validated_data['longitude'],
            altitude=0,
            accuracy=0,
            road_type=None,
            captura_id=self.validated_data.get('captura_id', None)
        )
        photo_base64_string = self.validated_data.get('photo_base64', None)
        if photo_base64_string:
            photo_file = ContentFile(base64.b64decode(photo_base64_string), name='temp.png')
            complaint.photo.save("test.png", photo_file)
        return complaint


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Ejemplo de votación',
            description='Crea una votación para indicar que la denuncia con id 0 SI se resolvió.',
            value={
                'vote_type': 'Y',
                'complaint_id': 0,
            },
            request_only=True
        ),
    ]
)
class ComplaintVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintVote
        fields = ['id', 'vote_type', 'complaint_id']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'code']

class ComplaintTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintType
        fields = ['id', 'name', 'code']

class ComplaintSerializerRead(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    city = CitySerializer()
    complaint_type = ComplaintTypeSerializer()

    class Meta:
        model = Complaint
        fields = ['id', 'complaint_type', 'description', 'city', 'latitude', 'longitude', 'photo', 'created_at', 'votes']
        depth = 1

    def get_votes(self, obj) -> VoteCount:
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
        
class AuthTokenRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()