from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matheus",
            password="123456Teste@",
        )

        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            cover=Book.CoverChoices.HARD,
            inventory=5,
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )

        self.client.force_authenticate(self.user)

    @patch("payments.services.stripe.checkout.Session.create")
    def test_create_payment(self, mock_session):
        mock_session.return_value.id = "session123"
        mock_session.return_value.url = (
            "https://checkout.stripe.com/test"
        )

        response = self.client.post(
            "/api/payments/",
            {
                "type": Payment.TypeChoices.PAYMENT,
                "borrowing": self.borrowing.id,
                "money_to_pay": "50.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Payment.objects.count(),
            1,
        )

    def test_list_payments(self):
        Payment.objects.create(
            borrowing=self.borrowing,
            type=Payment.TypeChoices.PAYMENT,
            money_to_pay=Decimal("50.00"),
        )

        response = self.client.get("/api/payments/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )
