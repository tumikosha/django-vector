from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django import forms
from django.contrib.auth.models import User


# Create your models here.


class UserForm(UserCreationForm):
    mobile = forms.CharField(max_length=15, min_length=10)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'mobile']


class Snippet(models.Model):
    """ Object for history of calculations"""
    created = models.DateTimeField(auto_now_add=True)
    code = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    result = models.TextField(null=True)
    have_error = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']