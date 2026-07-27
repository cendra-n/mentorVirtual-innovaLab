from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Country, Province, Locality
from .serializers import CountrySerializer, ProvinceSerializer, LocalitySerializer, ProvinceSearchSerializer
from rest_framework.response import Response
from rest_framework import status


class LocalityPagination(PageNumberPagination):
    """
    Con 'search' ahora disponible server-side, el frontend hace autocompletado
    en vez de cargar todo de una — no hace falta traer 200 por página, alcanza
    con una tanda chica de sugerencias (como cualquier typeahead).
    """
    page_size = 20
    page_query_param = 'page'

""" 
Vistas para la gestión de datos geográficos.

"""

@extend_schema(tags=['geo'], summary="Listado de países")
class CountryListView(ListAPIView):
    queryset = Country.objects.all().order_by('country_name')
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = None

@extend_schema(
    tags=['geo'], 
    summary="creación de provincias por país",
    description="Ingresa el nombre de una provincia para que de forma interna la asocie al país correspondiente mediante un POST."
)
class AssociateProvinceView(APIView):
    
    serializer_class = ProvinceSearchSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        search_name = serializer.validated_data['province_name']
        province_db = Province.objects.filter(province_name__icontains=search_name).first()

        if not province_db:
            return Response(
                {"mensaje": f"No se encontró ninguna provincia que coincida con '{search_name}' en la base de datos."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        result = {
            "province": province_db.province_name,
            "province_id": province_db.province_id,
            "country": province_db.country.country_name
        }

        return Response(result, status=status.HTTP_200_OK)
    
    
@extend_schema(tags=['geo'], summary="Listado de provincias por país")
class ProvinceListView(ListAPIView):
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    def get_queryset(self):
        qs = Province.objects.select_related('country').order_by('province_name')
        country_id = self.request.query_params.get('country')
        return qs.filter(country_id=country_id) if country_id else qs
    
@extend_schema(
    tags=['geo'],
    summary="Listado de localidades por provincia",
    description="El parámetro 'province' es OBLIGATORIO. Sin filtro, la tabla de localidades "
                "tiene miles de filas en todo el país — pedir el listado completo sin acotar "
                "es lo que colgaba Swagger/el backend antes. Admite 'search' para autocompletado "
                "por texto (necesario: con solo paginar, una provincia grande no entra en una "
                "página y el usuario nunca ve más allá de la primera tanda alfabética).",
    parameters=[
        OpenApiParameter(name='province', required=True, type=int, description='ID de la provincia (ver GET /api/auth/geo/provinces/list?country=<id>).'),
        OpenApiParameter(name='search', required=False, type=str, description='Texto para filtrar por nombre (autocompletado, ej: "cor").'),
    ]
)
class LocalityListView(ListAPIView):
    serializer_class = LocalitySerializer
    permission_classes = [AllowAny]
    pagination_class = LocalityPagination

    def get_queryset(self):
        province_id = self.request.query_params.get('province')
        if not province_id:
            # Nunca devolver el listado completo sin filtrar — es la causa
            # original del cuelgue. 400 explícito en vez de un queryset gigante.
            return Locality.objects.none()

        qs = Locality.objects.select_related('province__country').filter(province_id=province_id)

        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(locality_name__icontains=search)

        return qs.order_by('locality_name')

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('province'):
            return Response(
                {"province": "Este parámetro es obligatorio. Ej: /api/auth/geo/localities/?province=<id>"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)