from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Complaint, ComplaintVote, City, ComplaintType
from api.serializers import ComplaintTypeSerializer, ComplaintSerializerRead, ComplaintSerializerWrite, ComplaintVoteSerializer, CitySerializer
from app.models import Scientist
from app.utils import ComplaintsStatsReporter
import logging
import json
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ScientistListView(View):

    def get(self, request, *args, **kwargs):
        scientists = [s.serialize() for s in Scientist.objects.all()]
        return JsonResponse(scientists, safe=False)

    def post(self, request, *args, **kwargs):
        try:
            scientist_data = json.loads(request.body)
            scientist = Scientist.objects.create(**scientist_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'Scientist already registered.'}, status=400)
        return JsonResponse(scientist.serialize(), safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ScientistDetailView(View):

    def get(self, request, scientist_id, *args, **kwargs):
        try:
            scientist = Scientist.objects.get(id=scientist_id)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)
        return JsonResponse(scientist.serialize(), safe=False)

    def put(self, request, scientist_id, *args, **kwargs):
        try:
            scientist_data = json.loads(request.body)
            scientist = Scientist.objects.get(id=scientist_id)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)

        Scientist.objects.filter(id=scientist.id).update(**scientist_data)
        return JsonResponse({'message': 'Scientist updated successfully!'})

    def delete(self, request, scientist_id, *args, **kwargs):
        try:
            scientist = Scientist.objects.get(id=scientist_id)
        except Scientist.DoesNotExist:
            return JsonResponse({'error': 'Scientist not found.'}, status=404)
        scientist.delete()
        return JsonResponse({'message': 'Scientist deleted successfully!'})


@method_decorator(csrf_exempt, name='dispatch')
class GetUserToken(View):
    requires_auth = False

    def post(self, request, *args, **kwargs):
        try:
            credentials = json.loads(request.body)
            user = User.objects.get(username=credentials['username'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        if check_password(credentials['password'], user.password):
            return JsonResponse({'token': user.usertoken.bearer_token})

        return JsonResponse({'message': 'Invalid credentials.'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ComplaintVoteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ComplaintVote.objects.all()
    serializer_class = ComplaintVoteSerializer
    permission_classes = []
    authentication_classes = []

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, complaint_id=self.request.data['complaint'], vote_type=self.request.data['vote_type'])
        else:
            serializer.save(user=None, complaint_id=self.request.data['complaint'], vote_type=self.request.data['vote_type'])

class ComplaintListView(generics.ListCreateAPIView, generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Complaint.objects.all()
        search_params = self.request.query_params
        complaint_id = search_params.get('id', None)
        complaint_type_id = search_params.get('complaint-type-id', None)
        date = search_params.get('date', None)
        start_date = search_params.get('start-date', None)
        end_date = search_params.get('end-date', None)
        if complaint_id:
            queryset = queryset.filter(id=complaint_id)
        if complaint_type_id:
            queryset = queryset.filter(complaint_type_id=complaint_type_id)
        if date:
            queryset = queryset.filter(created_at__date=date)
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ComplaintSerializerRead
        if self.request.method == 'POST':
            return ComplaintSerializerWrite
        else:
            return ComplaintSerializerRead


class DownloadComplaintsPerCityReportView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        format = request.query_params.get('report-format', 'csv')
        start_date = request.query_params.get('start-date', None)
        end_date = request.query_params.get('end-date', None)
        complaints_reporter = ComplaintsStatsReporter(start_date, end_date)
        if format == 'csv':
            return complaints_reporter.generate_complaints_per_city_csv_report()
        elif format == 'json':
            return complaints_reporter.generate_complaints_per_city_json_report()
        else:
            return complaints_reporter.get_error_response()
        
class DownloadComplaintsPerComplaintTypeReportView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        format = request.query_params.get('report-format', 'csv')
        start_date = request.query_params.get('start-date', None)
        end_date = request.query_params.get('end-date', None)
        complaints_reporter = ComplaintsStatsReporter(start_date, end_date)
        if format == 'csv':
            return complaints_reporter.generate_complaints_per_complaint_count_csv_report()
        elif format == 'json':
            return complaints_reporter.generate_complaints_per_complaint_count_json_report()
        else:
            return complaints_reporter.get_error_response()
        
class CityListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = CitySerializer

    def get(self, request):
        city_id = request.query_params.get('id', None)
        queryset = City.objects.all()
        if city_id:
            queryset = queryset.filter(id=city_id)
        city_serializar = CitySerializer(queryset, many=True)
        return Response(city_serializar.data)
    
class ComplaintTypeListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ComplaintTypeSerializer

    def get(self, request):
        city_id = request.query_params.get('id', None)
        queryset = ComplaintType.objects.all()
        if city_id:
            queryset = queryset.filter(id=city_id)
        city_serializar = ComplaintTypeSerializer(queryset, many=True)
        return Response(city_serializar.data)