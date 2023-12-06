import datetime
import uuid

from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django import forms
from django.contrib.auth.models import User
from pgvector.django import VectorField
from django.utils.timezone import now

# encoder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
# STD_VECTOR_SIZE = encoder.get_sentence_embedding_dimension()
STD_VECTOR_SIZE = 384  # 1536 ? for open AI ada?  https://youtu.be/65uPqs-qttw?t=511https://youtu.be/65uPqs-qttw?t=511


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


# class Snippet222(models.Model):
#     """ Object for history of calculations"""
#     created = models.DateTimeField(auto_now_add=True)
#     code = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     result = models.TextField(null=True)
#     have_error = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['created']


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zip = models.CharField(max_length=8, null=True)
    title = models.TextField(null=True)
    summary = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = VectorField(dimensions=STD_VECTOR_SIZE, null=True)

    class Meta:
        ordering = ['created_at']

    # domain = forms.CharField(max_length=80)
    # web_page = forms.CharField(max_length=120)
    # embedding = VectorField(dimensions=STD_VECTOR_SIZE, null=True)
    # desc = models.TextField(null=True)
    # summary = models.TextField(null=True)
    # vertical = models.TextField(null=True)
    # email = models.TextField(null=True)
    # phone = models.TextField(null=True)
    # twitter = models.TextField(null=True)
    # tiktok = models.TextField(null=True)
    # facebook = models.TextField(null=True)
    # youtube = models.TextField(null=True)
    # google = models.TextField(null=True)
    # linkedin = models.TextField(null=True)
    # github = models.TextField(null=True)
    # city = models.TextField(null=True)
    # State = models.TextField(null=True)
    # zip = forms.CharField(max_length=8)
    # country = models.TextField(null=True)
    #
    # sales_revenue = forms.CharField(max_length=12)

    # class Meta:
    #     managed = True  # this class will not be managed by django migrations
    #     # db_table = "company_pg_embedding"
