from django.shortcuts import render


def index(request):
  return render(request, 'search/index.html')

def search(request):
  return render(request, 'search/searchscripts.html')

def view_script(request):
  return render(request, 'search/viewscript.html')
