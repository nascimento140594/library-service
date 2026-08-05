from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    payment_cancel,
    payment_success,
    stripe_webhook,
)

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path(
        "success/",
        payment_success,
        name="payment-success",
    ),
    path(
        "cancel/",
        payment_cancel,
        name="payment-cancel",
    ),
    path(
        "webhook/",
        stripe_webhook,
        name="stripe-webhook",
    ),
    path(
        "",
        include(router.urls),
    ),
]
