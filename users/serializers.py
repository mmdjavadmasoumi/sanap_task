# users/serializers.py
from rest_framework import serializers

class LoginErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=255)

from rest_framework import serializers
# users/serializers.py
class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    user_type = serializers.CharField(max_length=255)
    access = serializers.CharField(max_length=255)
    refresh = serializers.CharField(max_length=255)
