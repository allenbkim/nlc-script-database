from django.contrib import admin
from django.urls import path
from . import views


app_name = 'search'
urlpatterns = [
  path('', views.search, name='index'),
  path('searchscripts/', views.search, name='searchscripts'),
  path('<int:pk>/', views.ScriptDetailView.as_view(), name='detail'),
  path('logout/', views.logout_search, name='logout'),
]
