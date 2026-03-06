from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer


class CreateOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(customer=request.user)

            return Response({
                "message": "Order created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.


class UserOrdersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        orders = Order.objects.filter(customer=request.user).order_by("-created_at")

        serializer = OrderSerializer(orders, many=True)

        return Response(
            {
                "message": "Orders fetched successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
