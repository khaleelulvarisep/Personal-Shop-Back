from django.urls import path
from .views import DeliveryLoginAPIView

urlpatterns = [
path("login/", DeliveryLoginAPIView.as_view()),   

]