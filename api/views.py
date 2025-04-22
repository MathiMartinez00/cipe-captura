from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, JSONParser
from api.models import Complaint, ComplaintVote, City, ComplaintType
from api.serializers import ComplaintTypeSerializer, ComplaintSerializerRead, ComplaintSerializerWrite, ComplaintVoteSerializer, CitySerializer, AuthTokenRequestSerializer
from app.utils import ComplaintsStatsReporter
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GetUserTokenView(ObtainAuthToken):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        description='Retorna el token de un usuario.',
        examples=[
            OpenApiExample(
                'Ejemplo',
                description="Consigue el token del usuario 'username' con la contraseña 'password'.",
                value={
                    'username': 'username',
                    'password': 'password',
                },
                media_type='application/json',
                request_only=True
            )
        ],
        request={'application/json': AuthTokenRequestSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        description="Lista los votos de las denuncias. Los votos tienen el campo 'vote_type' para indicar si las denuncias ya fueron resueltas (vote_type='Y') o no (vote_type='N').",
        parameters=[
            OpenApiParameter('complaint-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id de la denuncia.')
        ]
    ),
    create=extend_schema(
        description="Crea un voto para una denuncia. El voto tiene el campo 'vote_type' para indicar si ya se resolvió la denuncia (vote_type='Y') o no (vote_type='N')."
    )
)
class ComplaintVoteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ComplaintVote.objects.all()
    serializer_class = ComplaintVoteSerializer
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        queryset = ComplaintVote.objects.all()
        complaint_id = self.request.query_params.get('complaint-id', None)
        if complaint_id:
            queryset = queryset.filter(complaint_id=complaint_id)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, complaint_id=self.request.data['complaint'], vote_type=self.request.data['vote_type'])
        else:
            serializer.save(user=None, complaint_id=self.request.data['complaint'], vote_type=self.request.data['vote_type'])


@extend_schema_view(
    list=extend_schema(
        description='Lista todas las denuncias.',
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id de la denuncia.'),
            OpenApiParameter('complaint-type-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id del tipo de denuncia.'),
            OpenApiParameter('city-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id del tipo de la ciudad.'),
            OpenApiParameter('start-date', OpenApiTypes.DATE, OpenApiParameter.QUERY, description='Inicio de rango de fechas de la denuncia. Utilizado cuando se filtra por un rango de fechas. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
            OpenApiParameter('end-date', OpenApiTypes.DATE, OpenApiParameter.QUERY, description='Fin de rango de fechas de la denuncia. Utilizado cuando se filtra por un rango de fechas. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
        ],
    ),
    create=extend_schema(
        description="Crea una denuncia.",
        request={'multipart/form-data': ComplaintSerializerWrite}
    )
)
class ComplaintListCreateView(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Complaint.objects.all()
        search_params = self.request.query_params
        complaint_id = search_params.get('id', None)
        complaint_type_id = search_params.get('complaint-type-id', None)
        city_id = search_params.get('city-id', None)
        date = search_params.get('date', None)
        start_date = search_params.get('start-date', None)
        end_date = search_params.get('end-date', None)
        if complaint_id:
            queryset = queryset.filter(id=complaint_id)
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if complaint_type_id:
            queryset = queryset.filter(complaint_type_id=complaint_type_id)
        if date:
            queryset = queryset.filter(created_at__date=date)
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        return queryset

    # TODO: Add a created_by to the complaint.
    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.action == 'create':
            return ComplaintSerializerWrite
        return ComplaintSerializerRead



class DownloadComplaintsPerCityReportView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @extend_schema(
        description="Genera el reporte de las denuncias hechas por ciudad. El formato puede ser csv (report-format='csv') o json (report-format='json').",
        parameters=[
            OpenApiParameter('report-format', OpenApiTypes.STR, OpenApiParameter.QUERY, default='csv', description='Formato del reporte. Puede ser "csv" o "json".')
        ]
    )
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

    @extend_schema(
        description="Genera el reporte de las denuncias hechas por tipo de denuncia. El formato puede ser csv (report-format='csv') o json (report-format='json').",
        parameters=[
            OpenApiParameter('report-format', OpenApiTypes.STR, OpenApiParameter.QUERY, default='csv', description='Formato del reporte. Puede ser "csv" o "json".')
        ]
    )
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

    @extend_schema(
        description='Lista las ciudades.',
        parameters=[
            OpenApiParameter('id', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Id de la ciudad.')
        ]
    )
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

    @extend_schema(
        description='Lista los tipos de denuncia.',
        parameters=[
            OpenApiParameter('id', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Id del tipo de denuncia.')
        ],

    )
    def get(self, request):
        city_id = request.query_params.get('id', None)
        queryset = ComplaintType.objects.all()
        if city_id:
            queryset = queryset.filter(id=city_id)
        city_serializar = ComplaintTypeSerializer(queryset, many=True)
        return Response(city_serializar.data)