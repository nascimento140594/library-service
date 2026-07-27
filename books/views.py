from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        "cover",
    )

    search_fields = (
        "title",
        "author",
    )

    ordering_fields = (
        "title",
        "author",
        "inventory",
    )

    ordering = (
        "title",
    )
