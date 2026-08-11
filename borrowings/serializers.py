from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

        read_only_fields = (
            "id",
            "borrow_date",
            "user",
        )

    def validate_book(self, value):
        if self.instance is None and value.borrowed >= value.inventory:
            raise serializers.ValidationError(
                "This book is out of stock."
            )

        return value

    def validate(self, attrs):
        borrow_date = (
            self.instance.borrow_date
            if self.instance
            else attrs.get("borrow_date")
        )

        expected_return_date = attrs.get(
            "expected_return_date"
        )
        actual_return_date = attrs.get(
            "actual_return_date"
        )

        if (
            expected_return_date
            and borrow_date
            and expected_return_date < borrow_date
        ):
            raise serializers.ValidationError(
                {
                    "expected_return_date": (
                        "Expected return date cannot be "
                        "earlier than borrow date."
                    )
                }
            )

        if (
            actual_return_date
            and borrow_date
            and actual_return_date < borrow_date
        ):
            raise serializers.ValidationError(
                {
                    "actual_return_date": (
                        "Actual return date cannot be "
                        "earlier than borrow date."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        book = validated_data["book"]

        book.borrowed += 1
        book.save()

        return Borrowing.objects.create(
            **validated_data
        )

    def update(self, instance, validated_data):
        actual_return_date = validated_data.get(
            "actual_return_date"
        )

        if (
            actual_return_date
            and instance.actual_return_date is not None
        ):
            raise serializers.ValidationError(
                {
                    "actual_return_date": (
                        "This borrowing has already been returned."
                    )
                }
            )

        if (
            actual_return_date
            and instance.actual_return_date is None
        ):
            book = instance.book

            if book.borrowed > 0:
                book.borrowed -= 1
                book.save()

        return super().update(
            instance,
            validated_data,
        )
