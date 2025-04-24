from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
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
        summary='Retorna el token de un usuario',
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
        summary='Lista todos los votos hechos en la aplicación.',
        description='Los votos tienen el campo "vote_type" para indicar si las denuncias ya fueron resueltas (vote_type="Y") o no (vote_type="N"). Se puede utilizar el parámetro "complaint-id" para listar las votaciones sobre una denuncia.',
        parameters=[
            OpenApiParameter('complaint-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id de la denuncia.')
        ]
    ),
    create=extend_schema(
        summary='Realiza una votación sobre el estado de una denuncia.',
        description='El voto tiene el campo "vote_type" para indicar si ya se resolvió la denuncia (vote_type="Y") o no (vote_type="N").'
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
        summary='Lista todas las denuncias.',
        description='Lista todas las denuncias según el rango de fechas dado ("start-date" y "end-date"), la ciudad ("city-id") o el tipo de denuncia ("complaint-type-id"). ' \
        'El campo "photo" de la entidad es el enlace dentro de la página para ver la foto de la denuncia y descargarla, ' \
        'sin embargo, tener en cuenta que denuncias hechas en 2024 pueden tener enlaces pero no fotos disponibles ya que pudieron haber sido borradas. ' \
        'El campo "votes" tiene la cuenta de los votos realizados sobre la denuncia para determinar si se resolvió (llave "Y") o no (llave "N").',
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id de la denuncia.'),
            OpenApiParameter('complaint-type-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id del tipo de denuncia.'),
            OpenApiParameter('city-id', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Id de la ciudad.'),
            OpenApiParameter('start-date', OpenApiTypes.DATE, OpenApiParameter.QUERY, description='Inicio de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
            OpenApiParameter('end-date', OpenApiTypes.DATE, OpenApiParameter.QUERY, description='Fin de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
        ],
    ),
    create=extend_schema(
        summary='Crea una denuncia.',
        description='Para crear una denuncia se necesitará la ubicación de esta, para esto se puede utilizar alguna aplicación de mapas como Google Maps o OpenStreetMap.',
        request={'application/json': ComplaintSerializerWrite}
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
        summary='Retorna el reporte de la cantidad de denuncias hechas por ciudad.',
        description='El formato del reporte está determinado por el campo "report-format" que puede ser "csv" o "json" y acepta los parámetros "start-date" y "end-date" para determinar que denuncias utilizar para recopilar los datos.',
        parameters=[
            OpenApiParameter('report-format', OpenApiTypes.STR, OpenApiParameter.QUERY, default='csv', description='Formato del reporte. Puede ser "csv" o "json".'),
            OpenApiParameter('start-date', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Inicio de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
            OpenApiParameter('end-format', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Fin de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").')
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
        summary='Retorna el reporte de la cantidad de denuncias hechas por tipo de denuncia.',
        description='El formato del reporte está determinado por el campo "report-format" que puede ser "csv" o "json" y acepta los parámetros "start-date" y "end-date" para determinar que denuncias utilizar para recopilar los datos.',
        parameters=[
            OpenApiParameter('report-format', OpenApiTypes.STR, OpenApiParameter.QUERY, default='csv', description='Formato del reporte. Puede ser "csv" o "json".'),
            OpenApiParameter('start-date', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Inicio de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").'),
            OpenApiParameter('end-format', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Fin de rango de fechas de las denuncias. Debe seguir el formato YYYY-mm-dd (Ejemplo: "2024-11-05").')
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
        summary='Lista las ciudades.',
        description='Representa una ciudad que se asocia a una denuncia por medio de su id. Los campos "code" y "color" son utilizados para realizar los gráficos en la web.',
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
        summary='Lista los tipos de denuncia.',
        description='Representa un tipo de denuncia que se asocia a una denuncia por medio de su id. Los campos "code" y "color" son utilizados para realizar los gráficos en la web.',
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