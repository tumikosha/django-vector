## Django stub project with
    Bootstrap 4 
    Tests for code, API & frontend pages
    API based on Restframefork
    Swagger UI for API
    Docker
    Static Files support by django
    Example Simple Calculator endpoint with history

## superuser
    login:admin
    password: pass123456

# Steps

## step 1
    django-admin startproject general  . 
    django-admin startapp app
    python manage.py migrate

# step 2 
# general/api/serializers.py
    from django.contrib.auth.models import User, Group
    from rest_framework import serializers
    
    
    class UserSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = User
            fields = ['url', 'username', 'email', 'groups']
    
    
    class GroupSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = Group
            fields = ['url', 'name']

## general/api/views.py
    from django.shortcuts import render

# Create your views here.
    from django.contrib.auth.models import User, Group
    from rest_framework import viewsets
    from rest_framework import permissions
    from api.serializers import UserSerializer, GroupSerializer
    
    
    class UserViewSet(viewsets.ModelViewSet):
        """
        API endpoint that allows users to be viewed or edited.
        """
        queryset = User.objects.all().order_by('-date_joined')
        serializer_class = UserSerializer
        permission_classes = [permissions.IsAuthenticated]
    
    
    class GroupViewSet(viewsets.ModelViewSet):
        """
        API endpoint that allows groups to be viewed or edited.
        """
        queryset = Group.objects.all()
        serializer_class = GroupSerializer
        permission_classes = [permissions.IsAuthenticated]

## general/urls.py
    
    """
    URL configuration for general project.
    
    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/4.2/topics/http/urls/
    Examples:
    Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    """
    from django.contrib import admin
    from django.urls import path
    # 
    # urlpatterns = [
    #     path('admin/', admin.site.urls),
    # ]
    
    from django.urls import include, path
    from rest_framework import routers
    from api import views
    
    router = routers.DefaultRouter()
    router.register(r'users', views.UserViewSet)
    router.register(r'groups', views.GroupViewSet)
    
    # Wire up our API using automatic URL routing.
    # Additionally, we include login URLs for the browsable API.
    urlpatterns = [
        path('', include(router.urls)),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        path('admin/', admin.site.urls),
    ]
    
 ## general/settings.py
    ...
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10
    }
    ....
    INSTALLED_APPS = [
        ...
        'rest_framework',
    ]

## general/settings.py
   ...
   ALLOWED_HOSTS = ['*']
   
## create admin user

  python manage.py createsuperuser --email admin@example.com --username admin
  
# https://learndjango.com/tutorials/django-login-and-logout-tutorial
    accounts/login/ [name='login']
    accounts/logout/ [name='logout']
    accounts/password_change/ [name='password_change']
    accounts/password_change/done/ [name='password_change_done']
    accounts/password_reset/ [name='password_reset']
    accounts/password_reset/done/ [name='password_reset_done']
    accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    accounts/reset/done/ [name='password_reset_complete']


# PG VECTOR
## configure engine in settings.py
    DATABASES = {
        # 'default': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME': BASE_DIR / 'db.sqlite3',
        # }
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'vector_db',
            'USER': "postgres",
            'PASSWORD': "postgres", # ? test
            'HOST': "localhost",
            'PORT': 5432,
        }
    }

### create vector_db via PgAdmin