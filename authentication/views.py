from django.shortcuts import render
from django.contrib.auth import login,logout,authenticate
# Create your views here.


def loginView(request):
    return render(request, 'authentication/login.html')

def logoutView(request):
    pass

def registerView(request):
    pass