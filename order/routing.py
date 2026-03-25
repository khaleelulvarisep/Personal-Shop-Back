# from django.urls import re_path
# from .consumers import DriverLocationConsumer                     

# websocket_urlpatterns = [
#     re_path(r'ws/order/(?P<order_id>\d+)/$', DriverLocationConsumer.as_asgi()),
# ]




from django.urls import re_path
from .consumers import DriverLocationConsumer
from .consumers import ChatConsumer


websocket_urlpatterns = [
    re_path(r'ws/driver/(?P<driver_id>\d+)/$', DriverLocationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<order_id>\d+)/$', ChatConsumer.as_asgi()),
]
