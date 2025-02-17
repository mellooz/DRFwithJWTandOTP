from django.shortcuts import get_object_or_404, render
from .models import User , Profile
from .serializers import UserSerializer , MyTokenObtainPairSerializer , EmailVerificationSerializer ,ChangePasswordSerializerWithOtp , RegisterSerializer , ChangePasswordSerializer , OTPVerificationSerializer

from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
# for access and refresh token 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateAPIView
from .utils import send_otp_email
# Create your views here.
from django.contrib.auth.hashers import check_password
###################################################################



class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    After successful registration, an OTP is generated and sent to the user's email.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        user.profile.generate_otp()
        user.profile.save()
        send_otp_email(user)
        return Response({"message": "OTP has been sent to your email. Please verify your account."}, 
                        status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    """
    API endpoint for verifying OTP to activate a user account.
    """
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, email=email)
        profile = user.profile
        if profile.is_otp_valid(otp):
            profile.verified = True
            profile.otp = None  # Remove OTP after successful verification
            profile.save()
            token = MyTokenObtainPairSerializer.get_token(user)
            return Response(
                {
                    "message": "Account verified successfully",
                    "access": str(token.access_token),
                    "refresh": str(token)
                },
                status=status.HTTP_200_OK
            )
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)





# for login
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Standard login with username & password.
    """
    serializer_class = MyTokenObtainPairSerializer




class UserProfileView(RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user









# change password with old one
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update_password(request.user)
            token = MyTokenObtainPairSerializer.get_token(request.user)
            return Response(
                {
                    "message": "password updated",
                    "access": str(token.access_token),
                    "refresh": str(token)
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# ask for otp to change password
class RequestOTPView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        profile.generate_otp()
        send_otp_email(user)
        profile.save()
        if send_otp_email(user):
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send OTP email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# check otp then change password
class VerifyOTPForPasswordChangeView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if not profile.is_otp_valid(otp):
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        profile.otp_created_at = None
        profile.otp = None
        profile.save()
        change_password_serializer = ChangePasswordSerializerWithOtp(data=request.data, context={'user': user})
        if change_password_serializer.is_valid():
            change_password_serializer.update_password(user)
            token = MyTokenObtainPairSerializer.get_token(user)
            return Response(
                {
                    "message": "OTP verified successfully. You may now reset your password.",
                    "access": str(token.access_token),
                    "refresh": str(token)
                },
                status=status.HTTP_200_OK
            )











@api_view(['GET'])
def getRoutes(request):
    routes = [
        'token/',
        'token/refresh/',
        'token/blacklist/',
        'register/',
        'test/',
    ]
    return Response(routes)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = "Hello buddy"
        data = f'Congratulation your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)