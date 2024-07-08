from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_FIRST_NAME,
                             MAX_LENGTH_LAST_NAME, MAX_LENGTH_PASSWORD,
                             MAX_LENGTH_USERNAME)
from users.validators import username_validator


class User(AbstractUser):
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL,
                              verbose_name='Адрес электронной почты',
                              unique=True)
    username = models.CharField(max_length=MAX_LENGTH_USERNAME,
                                unique=True,
                                validators=[username_validator],
                                verbose_name='Юзернейм')
    first_name = models.CharField(max_length=MAX_LENGTH_FIRST_NAME,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=MAX_LENGTH_LAST_NAME,
                                 verbose_name='Фамилия')
    password = models.CharField(max_length=MAX_LENGTH_PASSWORD,
                                verbose_name='Пароль')
    avatar = models.ImageField(upload_to='users/images',
                               verbose_name='Аватар пользователя',
                               default=None,
                               null=True)
    is_blocked = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписки',
        related_name='subscriptions'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчики',
        related_name='subscribers'
    )

    def __str__(self):
        return f"{self.subscriber}-{self.subscription}"

    class Meta:
        verbose_name = 'Подписчик',
        verbose_name_plural = 'Подписчики'
        unique_together = ('subscriber', 'subscription')
