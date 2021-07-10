from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class AccountType(models.Model):
    """Account type to be used for accounts"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    calculate = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    """Account to keep tracking of operations"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    acctype = models.ForeignKey(
        AccountType,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Tag to be attached to operations"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name


class Operation(models.Model):
    """Operation object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    tags = models.ManyToManyField('Tag')
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
