# from django.urls import path
# from .views import (CheckoutView,
#                    HomeListView,
#                    ProductDetailView,
#                    add_to_cart,
#                    remove_from_cart,
#                    OrderSummaryView,
#                    remove_single_item_from_cart,
#                    add_single_item_to_cart,
#                    PaymentView
#                    )
#
# app_name = 'Site'
#
# urlpatterns = [
#    path('', HomeListView.as_view(), name='homepage'),
#    path('checkout/', CheckoutView.as_view(), name='checkout'),
#    path('productpage/<slug>/', ProductDetailView.as_view(), name='productpage'),
#    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
#    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
#    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
#    path('remove_single_item_from_cart/<slug>/',
#         remove_single_item_from_cart, name='remove_single_item_from_cart'),
#    path('add_single_item_to_cart/<slug>/',
#         add_single_item_to_cart, name='add_single_item_to_cart'),
#    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
# ]

from django.urls import path
from .views import (AddCouponView, CheckoutView,
                    HomeListView,
                    ProductDetailView, RequestRefundView,
                    add_to_cart,
                    remove_from_cart,
                    OrderSummaryView,
                    remove_single_item_from_cart,
                    add_single_item_to_cart,
                    StripeIntentView,
                    CreateCheckoutSessionView,
                    AddCouponView,
                    PaymentView,
                    SuccessView,
                    RequestRefundView

                    )

app_name = 'Site'

urlpatterns = [
    path('', HomeListView.as_view(), name='homepage'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('productpage/<slug>/', ProductDetailView.as_view(), name='productpage'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug>/',
         remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('add_single_item_to_cart/<slug>/',
         add_single_item_to_cart, name='add_single_item_to_cart'),
    path('add_coupon/',
         AddCouponView.as_view(), name='add_coupon'),
    path('create-checkout-session', CreateCheckoutSessionView.as_view(),
         name='create-checkout-session'),
    path('create-payment-intent', StripeIntentView.as_view(),
         name='create-payment-intent'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('success/', SuccessView.as_view(), name='success'),
    path('request_refund/', RequestRefundView.as_view(), name='request_refund'),
]
