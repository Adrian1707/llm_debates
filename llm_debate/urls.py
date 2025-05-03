from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_topic, name='submit_topic'),
    path('debate/', views.debate, name='debate'),
]
