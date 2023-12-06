# -*- coding: utf-8 -*-
"""
File: app/views.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: Contain app views
"""
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response

from app.code import calculator
from app.forms import MathForm
from app.models import Snippet
from django.shortcuts import render
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages

from .serializers import SnippetSerializer
from app.models import Company


@csrf_exempt
def index(request) -> HttpResponse | TemplateResponse:
    """ SHOWS Home page and process MathForm
    if this is a POST request we need to process the form data   """
    result = " --"
    history = None

    if request.method == "POST":
        form = MathForm(request.POST or None)  # create a form instance and populate it with data from the request:

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            expression: str = form.cleaned_data["math"]
            have_error, result = calculator.calculate_expression(expression)
            if request.user.is_authenticated:
                snippet = Snippet.objects.create(code=expression, author=request.user,
                                                 have_error=have_error, result=result)

                history = Snippet.objects.filter(have_error=False).order_by('-created').all()[0:10]
            else:
                messages.error(request, "Because you are not logged expression is not saved to history ",
                               extra_tags="danger")
            if have_error:
                messages.error(request, "Result: " + str(result))
            else:
                messages.success(request, "Result: " + str(result))
            context = {"form": form, "history": history}
            return render(request, "app/index.html", context)
        else:  # form is not valid ?
            context = {"form": form, "history": history}
            return render(request, "app/index.html", context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MathForm(request.POST or None)
        rendered_form = form.render(template_name="app/math_form.html")

    if request.user.is_authenticated:
        history = Snippet.objects.order_by('-created').all()[0:10]

    # ---=== show embeddings ===---
    companies = Company.objects.all()[0:10]

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
