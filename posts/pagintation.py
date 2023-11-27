from rest_framework.pagination import PageNumberPagination

class TenPagintation(PageNumberPagination):
    page_size = 20

class FivePagintation(PageNumberPagination):
    page_size = 5