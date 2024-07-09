from django.contrib.auth import get_user_model
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from rest_framework import serializers

#from recipes.utils import Base64ImageField
from drf_extra_fields.fields import Base64ImageField
from users.models import Subscription

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']

    def validate(self, data):
        avatar = data.get('avatar', None)
        if not avatar:
            raise serializers.ValidationError('Необходимо прикрепить аватар.')
        return data


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if 'request' in self.context and self.context[
            'request'
        ].user.is_authenticated:
            current_user = self.context['request'].user
            subscription_exists = Subscription.objects.filter(
                subscriber=current_user,
                subscription=obj
            ).exists()
            return subscription_exists
        return False

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed')


class UserCreateSerializer(UserCreateSerializer):

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        representation['id'] = instance.id
        return representation

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class UserResetPasswordSerializer(
    CurrentPasswordSerializer, PasswordSerializer
):

    class Meta:
        fields = ('new_password', 'current_password')
        model = User
