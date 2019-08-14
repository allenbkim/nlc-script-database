from django.contrib import admin
from django.urls import path
from . import views


app_name = 'search'
urlpatterns = [
    path('', views.index, name='index'),
    path('searchscripts/', views.search, name='searchscripts'),
    path('viewscript/', views.view_script, name='viewscript'),
]
