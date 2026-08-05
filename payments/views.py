from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import stripe

from rest_framework import status, viewsets
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.services import create_checkout_session


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.all()

        return Payment.objects.filter(
            borrowing__user=user
        )

    def perform_create(self, serializer):
        borrowing = serializer.validated_data["borrowing"]

        if (
            not self.request.user.is_staff
            and borrowing.user != self.request.user
        ):
            raise PermissionError(
                "You cannot create payments for another user."
            )

        payment = serializer.save()

        session = create_checkout_session(payment)

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(serializer)

        payment = serializer.instance

        response_serializer = self.get_serializer(
            payment
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


def payment_success(request):
    return HttpResponse(
        "Payment completed successfully!"
    )


def payment_cancel(request):
    return HttpResponse(
        "Payment was canceled."
    )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        try:
            payment = Payment.objects.get(
                session_id=session["id"]
            )
        except Payment.DoesNotExist:
            return HttpResponse(status=404)

        payment.status = Payment.StatusChoices.PAID
        payment.save()

    return HttpResponse(status=200)
