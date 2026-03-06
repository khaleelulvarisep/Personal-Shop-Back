import logging
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import LoginSerializer, RegisterSerializer, VerifyOTPSerializer
from .tasks import send_otp_email_task


OTP_VALIDITY_MINUTES = 10
logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        defaults = {
            "first_name": serializer.validated_data["first_name"],
            "last_name": serializer.validated_data["last_name"],
            "phone": serializer.validated_data.get("phone"),
            "role": serializer.validated_data.get("role", "customer"),
            "is_active": False,
            "is_verified": False,
        }

        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        user.first_name = defaults["first_name"]
        user.last_name = defaults["last_name"]
        user.phone = defaults["phone"]
        user.role = defaults["role"]
        user.is_active = False
        user.is_verified = False
        user.set_password(serializer.validated_data["password"])
        user.generate_otp()

        try:
            task = send_otp_email_task.apply_async(
                args=(user.email, user.otp, OTP_VALIDITY_MINUTES),
                retry=False,
            )
        except Exception:
            logger.exception("Failed to enqueue OTP email task for %s", user.email)
            return Response(
                {"error": "Failed to queue OTP email. Please try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "message": "OTP queued for email delivery. Please verify to complete registration.",
                "email": user.email,
                "new_user": created,
                "task_id": task.id,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        if user.otp != serializer.validated_data["otp"]:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.otp_created_at:
            return Response(
                {"error": "OTP not found. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > user.otp_created_at + timedelta(minutes=OTP_VALIDITY_MINUTES):
            return Response(
                {"error": "OTP has expired. Please register again to get a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.is_verified = True
        user.otp = None
        user.otp_created_at = None
        user.save(update_fields=["is_active", "is_verified", "otp", "otp_created_at"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Email verified successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_verified or not user.is_active:
            return Response(
                {"error": "Account is not verified. Please verify OTP first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
