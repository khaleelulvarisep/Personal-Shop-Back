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
from .models import ChatMessage
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


# class ChatMessageSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source="sender.email")

#     class Meta:
#         model = ChatMessage
#         fields = ["id", "message", "username", "timestamp"]





from rest_framework import serializers

class ChatMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="sender.id")
    username = serializers.CharField(source="sender.email")

    class Meta:
        model = ChatMessage
        fields = ["id", "message", "user_id", "username", "timestamp"]