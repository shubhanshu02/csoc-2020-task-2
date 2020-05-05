from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.http import Http404
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError



def loginView(request):
    # If user is already logged in, redirect to Home
    if request.user.is_authenticated:
        return redirect("/")
    else:
        # The request is POST, process the information
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            # If any field is empty, return back to login page
            if len(username) == 0 or len(password) == 0:
                messages.info(request, "No field can be left empty")
                return render(request, 'authentication/login.html')

            # Else authenticate the user
            user = authenticate(username=username, password=password)
            # If user is not none:
            if user:
                login(request,user)
                return HttpResponseRedirect('/')
            # If authentication fails, invalid credentials were sent
            else:             
                messages.info(request, "Invalid Credentials!")
                return render(request, 'authentication/login.html')

        # Else if it is GET, open login page
        elif request.method == 'GET':
            return render(request, 'authentication/login.html')
        # Just in case
        else:
            raise Http404


def logoutView(request):
    # If user is logged in, logout
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'authentication/logout.html')
    # Else redirect to login page
    else:
        return redirect("/login")
    

def registerView(request):
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('/')
    else:
        # If request method is POST, signup
        if request.method == 'POST':
            data = request.POST
            query = [ data['username'], data['password'], data['first_name'], data['last_name'] ]
            fields = ['Username', 'Password', 'First Name', 'Last Name']
            # Check if any field is empty
            for element in query:
                # If empty field is found, return back with message
                if (len(element) == 0):
                    messages.info(request, fields[query.index(element)] + " cannot be left empty")
                    return render(request, 'authentication/register.html')

            # Check if username is already present
            users = User.objects.all()
            usrnames = []
            for usr in users:
                usrnames.append(usr.username)
            if query[0] in usrnames:
                messages.info(request, "This username already exists")
                return render(request, 'authentication/register.html')
            
            # Validate password
            try:
                password_validation.validate_password(query[1])
            except ValidationError as e:
                messages.info(request, e.messages[0])
                return render(request, 'authentication/register.html')

            # Create a new user
            new = User(username= query[0])
            # Set password
            new.set_password(query[1])
            # Set the name of the user
            new.first_name = query[2]
            new.last_name = query[3]
            # Save the User model object
            new.save()

            # Authenticate the user and login
            user = authenticate(username= data['username'], password= data['password'])
            login(request,user)
            return HttpResponseRedirect('/')

        # If request method is GET, open signup page
        elif request.method == 'GET':
            return render(request, 'authentication/register.html')
        else:
            raise Http404