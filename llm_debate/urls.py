from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.http import JsonResponse
import sys
from base64 import urlsafe_b64decode
import os
import json
from dotenv import load_dotenv
from . import views

load_dotenv()  # Loads .env file from current directory by default

urlpatterns = [
    path('', views.submit_topic, name='submit_topic'),
    path('debate/', views.debate, name='debate'),
]
