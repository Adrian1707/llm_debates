from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.http import JsonResponse
import sys
from base64 import urlsafe_b64decode
from llm_debate.debate_agent import DebateAgent
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Loads .env file from current directory by default

def hello_world(request):
    agent = DebateAgent()
    agent.send_message('Foo')
    return HttpResponse("Hello World!")

urlpatterns = [
    path('', hello_world),  # root endpoint
]