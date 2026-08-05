import stripe

from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(payment):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": f"Library Service Payment #{payment.id}",
                    },
                    "unit_amount": int(payment.money_to_pay * 100),
                },
                "quantity": 1,
            }
        ],
        success_url="http://127.0.0.1:8000/api/payments/success/",
        cancel_url="http://127.0.0.1:8000/api/payments/cancel/",
    )

    return session
