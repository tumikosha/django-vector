from datetime import datetime

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response

from app.code.calculator import calculate_expression
from app.models import Snippet, Company


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CurrentUserDefaultWithErr(serializers.CurrentUserDefault):
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class SnippetSerializer(serializers.ModelSerializer):
    """ serializer without  calculation"""
    # author = PrimaryKeyRelatedField(queryset=User.objects.all())
    author = PrimaryKeyRelatedField(read_only=True,
                                    # default=serializers.CurrentUserDefault(), help_text="primary key",
                                    default=CurrentUserDefaultWithErr(), help_text="primary key",

                                    )

    class Meta:
        model = Snippet
        fields = ['id', 'created', 'code', 'author', 'have_error', 'result']
        read_only_fields = ['author', 'created', 'have_error', 'result']

    def create(self, validated_data):
        snippet = Snippet.objects.create(**validated_data)

        try:
            snippet.author = self.context['request'].user
        except:
            raise AuthenticationFailed()  # You could also use PermissionDenied to return 403
        snippet.have_error, snippet.result = calculate_expression(validated_data['code'])
        snippet.save()
        return snippet


class CompanySerializer(serializers.ModelSerializer):
    # author = PrimaryKeyRelatedField(queryset=User.objects.all())
    # author = PrimaryKeyRelatedField(read_only=True,
    #                                 # default=serializers.CurrentUserDefault(), help_text="primary key",
    #                                 default=CurrentUserDefaultWithErr(), help_text="primary key",
    #                                 )

    class Meta:
        model = Snippet
        fields = ['uuid_id', 'title']
        # read_only_fields = ['author', 'created', 'have_error', 'result']

    def create(self, validated_data):
        company = Company.objects.create(**validated_data)
        company.title = "random title"
        company.save()
        return company
