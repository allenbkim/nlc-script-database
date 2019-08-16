from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'search'
urlpatterns = [
    path('', views.index, name='index'),
    path('searchscripts/', views.search, name='searchscripts'),
    path('viewscript/', views.view_script, name='viewscript'),
    path('logout/', views.logout_search, name='logout'),
]
