from rest_framework import serializers
from .models import Order


# class OrderSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Order
#         fields = [
#             'id',
#             'customer',
#             'grocery_items',
#             'note',
#             'latitude',
#             'longitude',
#             'status',
#             'created_at'
#         ]

#         read_only_fields = ['customer', 'status', 'created_at']



from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"

        read_only_fields = [
            'customer',
            'status',
            'created_at'
        ]