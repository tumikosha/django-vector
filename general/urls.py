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
from django.views.generic import TemplateView
from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view


router = routers.DefaultRouter()
# Uncomment this to see other endpoints
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'Snippet', views.SnippetViewSet, "snippets")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include('app.urls')),
    # path('api/', include(router.urls), ),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("swagger-ui/",
         TemplateView.as_view(template_name="swagger-ui.html", extra_context={"schema_url": "openapi-schema"}),
         name="swagger-ui"),
    path('openapi/',
         get_schema_view(title="Calculator project",
                         description="API for all things …",
                         version="1.0.0"
                         ), name='openapi-schema'
         )
]

urlpatterns += router.urls
