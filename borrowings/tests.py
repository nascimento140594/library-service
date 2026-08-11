from datetime import date, timedelta

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing


User = get_user_model()


class BorrowingInventoryTests(APITestCase):
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
            borrowed=0,
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_borrowing_increases_borrowed(self):
        response = self.client.post(
            "/api/borrowings/",
            {
                "book": self.book.id,
                "expected_return_date": (
                    date.today() + timedelta(days=7)
                ).isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.inventory,
            5,
        )

        self.assertEqual(
            self.book.borrowed,
            1,
        )

    def test_return_borrowing_decreases_borrowed(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=(
                date.today() + timedelta(days=7)
            ),
        )

        self.book.borrowed = 1
        self.book.save()

        response = self.client.patch(
            f"/api/borrowings/{borrowing.id}/",
            {
                "actual_return_date": date.today().isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.borrowed,
            0,
        )

    def test_cannot_borrow_when_all_books_are_borrowed(self):
        self.book.borrowed = self.book.inventory
        self.book.save()

        response = self.client.post(
            "/api/borrowings/",
            {
                "book": self.book.id,
                "expected_return_date": (
                    date.today() + timedelta(days=7)
                ).isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.borrowed,
            self.book.inventory,
        )
