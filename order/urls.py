from django.urls import path
from .views import CreateOrderView,UserOrdersView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path("my-orders/", UserOrdersView.as_view(), name="my_orders"),
]