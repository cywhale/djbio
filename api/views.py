# ref: https://realpython.com/getting-started-with-django-channels/ 202105
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.contrib import messages
from .models import apitest

# Create your views here.

def dboard(req):
    records = apitest.objects.count()
    #username = req.GET.get("name") #or "guest" #req.GET["name"] #req.GET.getlist("name")
    #return HttpResponse("Hello, {}!".format(name)) #"{vname1} {vname2}".format(vname1=var1,vname2=var2)
    return render(req, "api/dboard.html", {"records": records})

# User Handler
User = get_user_model()

@login_required(login_url='/login/') # @decorator to both our user list and log out views to restrict access only to registered users.
def user(req):
    users = User.objects.select_related('apiuser')
    for user in users:
        user.status = 'Online' if hasattr(user, 'apiuser') else 'Offline'
    return render(req, 'api/user.html', {'users': users})

def login(req):
    form = AuthenticationForm()
    if req.method == 'POST':
        form = AuthenticationForm(data=req.POST)
        if form.is_valid():
            #username = form.get_user() # not really authenticate
            #login(req, username)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                #if user.is_active:
                auth_login(req, user)
                #return HttpResponseRedirect(reverse('api:dboard', username)) #find name is 'dboard' under api app
                return redirect(reverse('api:user'))
            else:
                messages.error(req,'username or password not correct')
                return redirect(reverse('api:login'))
        else:
            messages.error(req, form.errors)
            return redirect(reverse('api:login'))

    return render(req, 'api/login.html', {'form': form})

@login_required(login_url='/login/')
def logout(req):
    logout(req)
    return redirect(reverse('api:login'))

def signup(req):
    form = UserCreationForm()
    if req.method == 'POST':
        form = UserCreationForm(data=req.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('api:login'))
        else:
            messages.error(req, form.errors)
            return redirect(reverse('api:signup'))

    return render(req, 'api/signup.html', {'form': form})
