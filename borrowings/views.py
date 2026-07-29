from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        "book",
        "user",
        "actual_return_date",
    )

    ordering_fields = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    )

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Borrowing.objects.all()

        return Borrowing.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
