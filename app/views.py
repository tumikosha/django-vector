# -*- coding: utf-8 -*-
"""
File: app/views.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: Contain app views
"""
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from pgvector.django import L2Distance
from rest_framework import generics, status
from rest_framework.response import Response

from app.code import calculator
from app.forms import SearchForm
from app.models import Snippet
from django.shortcuts import render

from util import common
from util import common
from util.common import final
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages

from .serializers import SnippetSerializer
from app.models import Company
from django.core.paginator import Paginator

PAGE_SIZE = 100


@csrf_exempt
def index(request) -> HttpResponse | TemplateResponse:
    """ SHOWS Home page and process SearchForm
    if this is a POST request we need to process the form data   """
    result = " --"
    history = None

    if request.method == "POST":
        form = SearchForm(request.POST or None)  # create a form instance and populate it with data from the request:

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            input_str: str = form.cleaned_data["query"]
            print("# --> input_str:", input_str)
            # have_error, result = calculator.calculate_expression(expression)
            companies = None
            if request.user.is_authenticated:
                vector = common.encoder.encode(input_str).tolist()
                # companies = Company.objects.order_by(L2Distance('embedding', vector))[:PAGE_SIZE]
                companies = Company.objects.annotate(
                    distance=L2Distance('embedding', vector)
                ).order_by(L2Distance('embedding', vector))

                paginator = Paginator(companies, per_page=2)
                page = 2
                page_object = paginator.get_page(page)
                page_object.adjusted_elided_pages = paginator.get_elided_page_range(page)
                # print("distances:", [cmp.distance for cmp in companies])
                companies = final(companies)
                context = {"form": form, "companies": companies, "page_obj": page_object}
                return render(request, "app/index.html", context)

            else:
                vector = common.encoder.encode(input_str).tolist()
                # companies = Company.objects.order_by(L2Distance('embedding', vector))[:PAGE_SIZE]
                companies = Company.objects.annotate(
                    distance=L2Distance('embedding', vector)
                ).order_by(L2Distance('embedding', vector))[:PAGE_SIZE]

                messages.error(request, "We found 33 more people matching your request<br>"
                                        "To get more relevant results and unlock extra data sources, you need to sign in",
                               extra_tags="danger")

            # messages.error(request, "Result: " + str(result))
            # messages.success(request, "Result: " + str(result))
            companies = final(companies)
            context = {"form": form, "companies": companies}
            return render(request, "app/index.html", context)
        else:  # form is not valid ?
            context = {"form": form, "companies": None}
            return render(request, "app/index.html", context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm(request.POST or None)
        rendered_form = form.render(template_name="app/search_form.html")

    if request.user.is_authenticated:
        history = Snippet.objects.order_by('-created').all()[0:PAGE_SIZE]

    # ---=== show embeddings ===---

    companies = Company.objects.all()[0:PAGE_SIZE]
    companies = final(companies)

    context = {"form": rendered_form, "history": history, "companies": companies}
    return TemplateResponse(request, 'app/index.html', context)


def register_request(request) -> HttpResponse | TemplateResponse:
    """ process user registration via NewUserForm """
    if request.method == "POST":
        form = NewUserForm(request.POST or None)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful")
            context = {"register_form": form}
            return render(request=request, template_name="registration/register.html", context=context)

        messages.error(request, "Unsuccessful registration. Invalid information.")
        context = {"register_form": form}
        return render(request=request, template_name="registration/register.html", context=context)
    else:
        form = NewUserForm(request.POST)
        rendered_form = form.render(template_name="app/reg_form.html")
        context = {"form": rendered_form}
        return TemplateResponse(request, "registration/register.html", context)

    form = NewUserForm()


class SnippetListCreateView(generics.ListCreateAPIView):
    """ VIEW  responsible for API  '/api/Snippet'  endpoint"""
    # queryset = Snippet.objects.all() # standard way do not support auth check
    serializer_class = SnippetSerializer

    def create(self, request, *args, **kwargs) -> Response:
        """ do calc and insert Snippet object into database for history"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return super(generics.ListCreateAPIView, self).create(request, args, kwargs)

    def list(self, request, *args, **kwargs) -> Response:
        """return history of calculations"""
        if not request.user.is_authenticated:  # Check authentication here
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # redefine the order and filtering
        queryset = Snippet.objects.filter(author=request.user.id).all().order_by('-created')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
