from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.

def loginView(request):
    #   
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request,user)
                return HttpResponseRedirect('/')
            #else:
                                #INVALID PASSWORD
        elif request.method == 'GET':
            return render(request, 'authentication/login.html')


def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'authentication/logout.html')
    else:
        return redirect("/login")
    

def registerView(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:

        if request.method == 'POST':
            data = request.POST
            new = User(username= data['username'])
            new.set_password(data['password'])
            new.first_name = data['first_name']
            new.last_name = data['last_name']
            new.save()
            user = authenticate(username= data['username'], password= data['password'])
            if user: 
                login(request,user)
                return HttpResponseRedirect('/')
            
        elif request.method == 'GET':
            return render(request, 'authentication/register.html')