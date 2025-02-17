# class RequestPasswordResetOTPView(APIView):
#     """
#     API endpoint for requesting an OTP to reset the password.
#     """
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         email = request.data.get("email")
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         user.profile.generate_otp()
#         user.profile.save()
#         send_otp_email(user)
#         return Response({"message": "OTP has been sent to your email."}, status=status.HTTP_200_OK)


# class ResetPasswordWithOTPView(APIView):
#     """
#     API endpoint for resetting password using OTP.
#     """
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         email = serializer.validated_data["email"]
#         otp = serializer.validated_data["otp"]
#         new_password = request.data.get("new_password")
#         if not email or not otp or not new_password:
#             return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(email=email)
#             profile = user.profile
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         if profile.is_otp_valid(otp):
#             user.set_password(new_password)
#             user.save()
#             profile.otp = None 
#             profile.save()
#             return Response({"message": "Password has been updated successfully"}, status=status.HTTP_200_OK)
#         return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)










# class LoginWithOTPView(APIView):
#     """
#     API endpoint for login using email and password.
#     Generates an OTP and sends it to the user's email.
#     """
#     permission_classes = [AllowAny]
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         if not user.check_password(password):
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         if not user.profile.verified:
#             return Response({"error": "Account not verified. Please verify with OTP."}, 
#                             status=status.HTTP_403_FORBIDDEN)
#         user.profile.generate_otp()
#         send_otp_email(user)
#         return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)



# class VerifyLoginOTPView(APIView):
#     """
#     API endpoint for verifying OTP after login.
#     Returns access and refresh tokens upon success.
#     """
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         email = serializer.validated_data["email"]
#         otp = serializer.validated_data["otp"]
#         try:
#             user = User.objects.get(email=email)
#             profile = user.profile
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         if profile.is_otp_valid(otp):
#             token = MyTokenObtainPairSerializer.get_token(user)
#             return Response(
#                 {
#                     "refresh": str(token),
#                     "access": str(token.access_token)
#                 },
#                 status=status.HTTP_200_OK
#             )
#         return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)






#









# class RequestPasswordChangeView(APIView):
#     """
#     User requests password change.
#     If old password is correct, change password directly.
#     If old password is missing or incorrect, send OTP.
#     """
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         user = request.user
#         serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         profile = user.profile
#         old_password = request.data.get("old_password")
#         if old_password and check_password(old_password, user.password):
#             serializer.update_password(user)
#             # Password updated without OTP
#             return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
#         profile.generate_otp()
#         profile.temp_password = serializer.validated_data["new_password"]
#         profile.save()
#         send_otp_email(user)
#         return Response({"message": "OTP sent to your email. Verify it to complete password change."}, status=status.HTTP_200_OK)



# class VerifyOTPForPasswordChangeView(APIView):
#     """
#     Verifies OTP and updates password if correct.
#     """
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         email = serializer.validated_data["email"]
#         otp = serializer.validated_data["otp"]
#         try:
#             user = User.objects.get(email=email)
#             profile = user.profile
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         if not profile.is_otp_valid(otp):
#             return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
#         if not profile.temp_password:
#             return Response({"error": "No password change request found"}, status=status.HTTP_400_BAD_REQUEST)
#         password_serializer = ChangePasswordSerializer(data={
#             "old_password": "",
#             "new_password": profile.temp_password,
#             "confirm_password": profile.temp_password
#         }, context={'request': request})

#         if password_serializer.is_valid():
#             password_serializer.update_password(user)
#         profile.temp_password = None
#         profile.otp = None
#         profile.save()

#         return Response({"message": "Password has been updated successfully"}, status=status.HTTP_200_OK)