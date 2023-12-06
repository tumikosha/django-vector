from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views
from .views import SnippetListCreateView
from django.contrib.staticfiles.views import serve as serve_static

app_name = 'app'


def _static_butler(request, path, **kwargs):
    """
    Serve static files using the django static files configuration
    WITHOUT collectstatic. This is slower, but very useful for API
    only servers where the static files are really just for /admin

    Passing insecure=True allows serve_static to process, and ignores
    the DEBUG=False setting
    """
    return serve_static(request, path, insecure=True, **kwargs)


urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_request, name="register"),
    path("api/Snippet/", SnippetListCreateView.as_view(), name="snippet-list-create"),
    re_path(r'static/(.+)', _static_butler),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="app/robots.txt", content_type="text/plain"),
        name="robots"
    ),
]


