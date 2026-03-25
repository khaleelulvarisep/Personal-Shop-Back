from django.urls import path
from .views import CreateOrderView,UserOrdersView,AllOrdersAPIView,NearbyOrdersAPIView,OrderDetailAPIView,AcceptOrderAPIView,DriverAcceptedOrdersAPIView,ChatMessageListAPIView,ChatMessagesAPIView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path("my-orders/", UserOrdersView.as_view(), name="my_orders"),
    path("orders/", AllOrdersAPIView.as_view(), name="all-orders"),
    path("nearby-orders/", NearbyOrdersAPIView.as_view()),
    path("order/<int:order_id>/", OrderDetailAPIView.as_view()),
    path("accept/<int:order_id>/", AcceptOrderAPIView.as_view()),
    path("driver/orders/",DriverAcceptedOrdersAPIView.as_view(),name="driver-orders"),
    # path("chat/<int:order_id>/", ChatMessageListAPIView.as_view()),
    path("chat/<int:order_id>/", ChatMessagesAPIView.as_view()),


    

]