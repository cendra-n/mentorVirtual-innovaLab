from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
import math

class CustomPagination(PageNumberPagination):
    page_size = 10  # Mantenemos 10 registros por página
    page_query_param = 'page'

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except Exception:
            # Si entran aquí (ej. página 3 vacía), calculamos cuántas páginas existen realmente
            total_count = queryset.count()
            total_pages = math.ceil(total_count / self.page_size) if total_count > 0 else 1
            
            # Lanzamos tu mensaje de excepción con la cantidad exacta N disponible
            raise NotFound(detail=f"Error página vacía, solo hay {total_pages} páginas cargadas hasta el momento")

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        
        # Inyectamos de forma nativa 'total_pages' en el Response Body
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,  
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })