from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 15  # Itens por página
    page_size_query_param = 'rows_per_page'  # Permite ao cliente definir o número de itens
    max_page_size = 100  # Limite máximo de itens por página
