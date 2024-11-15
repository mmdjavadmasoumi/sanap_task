
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _  # Add this import at the top of the file

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number and password:
            user = authenticate(request=self.context.get('request'), username=phone_number, password=password)

            if not user:
                raise serializers.ValidationError(_('No active account found with the given credentials'))

            refresh = self.get_token(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'user_type': user.get_user_type_display(),
            }

            return data
        else:
            raise serializers.ValidationError(_('Must include "phone_number" and "password"'))

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
