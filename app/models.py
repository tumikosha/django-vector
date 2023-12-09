import datetime
import uuid

from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django import forms
from django.contrib.auth.models import User
from pgvector.django import VectorField, IvfflatIndex, HnswIndex
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


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocked = models.BooleanField(default=False)
    domain = models.TextField(null=True)
    name = models.TextField(null=True)
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    full_txt = models.TextField(null=True)
    summary = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    first_indexed = models.DateTimeField(auto_now_add=True)

    embedding = VectorField(dimensions=STD_VECTOR_SIZE, null=True)
    sales_revenue = models.CharField(max_length=12, null=True)
    revenue = models.CharField(max_length=12, null=True)
    employees = models.IntegerField(null=True)
    industry = models.TextField(null=True)  # vertical aka category
    logo = models.TextField(null=True)
    linkedin = models.TextField(null=True)
    facebook = models.CharField(max_length=40, null=True)
    youtube = models.TextField(null=True)  # models.CharField(max_length=60, null=True)
    vimeo = models.TextField(null=True)  # models.CharField(max_length=60, null=True)
    vk = models.CharField(max_length=40, null=True)
    instagram = models.CharField(max_length=40, null=True)
    google = models.CharField(max_length=40, null=True)
    threads = models.CharField(max_length=40, null=True)
    twitter = models.CharField(max_length=40, null=True)
    github = models.TextField(null=True)
    # calendly = models.TextField(null=True)
    calendly = models.JSONField(null=True)
    calendly_acc_num = models.IntegerField(null=True, default=None)
    calendly_events_num = models.IntegerField(null=True, default=None)
    calendly_open_days_num = models.IntegerField(null=True, default=None)
    emails = models.TextField(null=True)
    emails_json = models.JSONField(null=True)
    phones = models.TextField(max_length=40, null=True)
    phones_json = models.JSONField(null=True)
    zip = models.CharField(max_length=8, null=True)
    city = models.CharField(max_length=40, null=True)
    country = models.CharField(max_length=8, null=True)
    state = models.CharField(max_length=8, null=True)

    # First_Detected, Last_Found, First_Indexed, Last_Indexed, CIK_No, SIC_Code, Tickers, Exchanges, Period_Start, Period_End, Revenue, Operating_Income, Net_Income, Assets

    class Meta:
        ordering = ['created_at']
        indexes = [
            IvfflatIndex(
                name='company_ivff_index',
                fields=['embedding'],
                lists=100,
                opclasses=['vector_l2_ops']
            ),
            # or
            HnswIndex(
                name='company_hnsv_index',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            )
        ]

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
