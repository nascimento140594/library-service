from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
        )

        read_only_fields = (
            "id",
            "status",
            "session_url",
            "session_id",
            "created_at",
        )

    def validate(self, attrs):
        borrowing = attrs["borrowing"]

        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )

        payment_exists = Payment.objects.filter(
            borrowing=borrowing,
            status=Payment.StatusChoices.PENDING,
        ).exists()

        if payment_exists:
            raise serializers.ValidationError(
                "A pending payment already exists for this borrowing."
            )

        return attrs
