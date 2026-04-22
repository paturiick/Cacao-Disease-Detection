from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = RegisterSerializer.Meta.model.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {
            "full_name": request.user.full_name,
            "email": request.user.email,
        }
        if request.user.profile_picture:
            data["profile_picture"] = request.user.profile_picture.url
        return Response(data)

    def patch(self, request):
        user = request.user
        
        # Update text fields
        if 'full_name' in request.data:
            user.full_name = request.data['full_name']
        if 'email' in request.data:
            user.email = request.data['email']
        if 'password' in request.data and request.data['password']:
            user.set_password(request.data['password'])
            
        # Update image
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        return Response({"detail": "Profile updated successfully"})