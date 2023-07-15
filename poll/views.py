from django.shortcuts import render

# Create your views here.

def base(request):
    return render(request, "poll/base.html")

def home(request):
    return render(request, "poll/home.html", {'title': 'Home'})
    