


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatMessage, Order
from django.contrib.auth import get_user_model

class DriverLocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.room_group_name = f"driver_{self.driver_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):

        data = json.loads(text_data)

        latitude = data["latitude"]
        longitude = data["longitude"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_location",
                "latitude": latitude,
                "longitude": longitude,
            }
        )


    async def send_location(self, event):

        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        }))







User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.user = self.scope["user"]

        # ✅ Convert LazyObject → real user
        if hasattr(self.user, "_wrapped"):
            self.user = self.user._wrapped

        print("🔥 Connected user:", self.user)

        # ✅ Allow for now (you can secure later)
        is_allowed = await self.is_user_allowed()

        if not is_allowed:
            await self.close()
            return

        self.room_group_name = f"chat_{self.order_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        user_id = data.get("user_id")

        if not message:
            return

        # ✅ Save message
        chat = await self.save_message(message,user_id)

        # ✅ Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": chat.message,
                "user_id": chat.sender.id,
                "username":chat.sender.first_name,
                "timestamp": str(chat.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def is_user_allowed(self):
        # 🔥 For now allow all
        return True

    @sync_to_async
    def save_message(self, message,user_id):
        order = Order.objects.get(id=self.order_id)

        # ✅ Ensure user is real instance
        user = User.objects.get(id=user_id)

        return ChatMessage.objects.create(
            sender=user,
            order=order,
            message=message
        )