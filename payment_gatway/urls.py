from django.urls import path
from . import views

app_name = 'payment_gatway'

urlpatterns = [
    # Cart Endpoints
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/count/', views.cart_count, name='cart_count'),

    # Checkout & Order Placement
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),

    # Stripe Endpoints
    path('payment/stripe/create-session/<uuid:access_token>/', views.stripe_create_session, name='stripe_create_session'),
    path('payment/stripe/success/', views.stripe_success, name='stripe_success'),
    path('payment/stripe/cancel/<uuid:access_token>/', views.stripe_cancel, name='stripe_cancel'),
    path('payment/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

    # PayPal Endpoints
    path('payment/paypal/create-order/<uuid:access_token>/', views.paypal_create_order, name='paypal_create_order'),
    path('payment/paypal/capture-order/', views.paypal_capture_order, name='paypal_capture_order'),

    # Order Confirmation & Status
    path('order/<uuid:access_token>/success/', views.order_success, name='order_success'),
]
