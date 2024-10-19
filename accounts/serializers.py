from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

class UserRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:

        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attr):

        password = attr.get('password', '')
        password2 = attr.get('password2', '')
        if password != password2:
            raise serializers.ValidationError('passwords do not match')
        return attr

    def create(self, validated_data):
        
        user = User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            password = validated_data['password']
        )

        return user

class LoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=60, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("invalid credentials try again")

        if not user.is_verified:
            raise AuthenticationFailed("email is not verified")
         
        user_tokens = user.tokens() 

        return {
            'email':user.email,
            'full_name':user.get_full_name,
            'access_token':str(user_tokens.get('access')),
            'refresh_token':str(user_tokens.get('refresh')),

        }    
    

class PasswordResetRequestSerializer(serializers.Serializer):
    email =serializers.EmailField(max_lenght=255)

    class Meta:
        fields = ['email']

    def validate(self, attr):
        email = attr.get('email') 
        if User.objects.filter(email=email).exists(): # check if user is in the database
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm')
        return super.validate(attr)        