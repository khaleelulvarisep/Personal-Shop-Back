from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic


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


class AllOrdersAPIView(APIView):

    def get(self, request):

        orders = Order.objects.filter(status="pending").order_by("-created_at")

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)    



class NearbyOrdersAPIView(APIView):

    def get(self, request):

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if not lat or not lng:
            return Response({"error": "Location required"}, status=400)

        partner_location = (float(lat), float(lng))

        orders = Order.objects.filter(status="pending")

        nearby_orders = []

        for order in orders:

            order_location = (order.latitude, order.longitude)

            distance = geodesic(partner_location, order_location).km

            if distance <= 5:   # within 5km

                order_data = OrderSerializer(order).data
                order_data["distance"] = round(distance, 2)

                nearby_orders.append(order_data)

        nearby_orders.sort(key=lambda x: x["distance"])

        return Response(nearby_orders, status=status.HTTP_200_OK)      

class OrderDetailAPIView(APIView):

    def get(self, request, order_id):

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)          
