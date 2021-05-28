# ref: https://realpython.com/getting-started-with-django-channels/ 202105
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.contrib import messages
from .models import apitest

# Create your views here.

def dboard(request):
    records = apitest.objects.count()
    #username = request.GET.get("name") #or "guest" #request.GET["name"] #request.GET.getlist("name")
    #return HttpResponse("Hello, {}!".format(name)) #"{vname1} {vname2}".format(vname1=var1,vname2=var2)
    return render(request, "api/dboard.html", {"records": records})

# User Handler
User = get_user_model()

@login_required(login_url='/login/') # @decorator to both our user list and log out views to restrict access only to registered users.
def user_handler(request):
    users = User.objects.select_related('apiuser')
    for user in users:
        user.status = 'Online' if hasattr(user, 'apiuser') else 'Offline'
    return render(request, 'api/user.html', {'users': users})

def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            #username = form.get_user() # not really authenticate
            #login(request, username)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if not user:
                messages.error(request,'username or password not correct')
                return redirect('/login/')
            else:
                #if user.is_active:
                login(request, user)
                #return HttpResponseRedirect(reverse('api:dboard', username)) #find name is 'dboard' under api app
                return redirect(reverse('api:user_handler'))
        else:
            messages.error(request, form.errors)
            return redirect('/login/')

    return render(request, 'api/login.html', {'form': form})

@login_required(login_url='/login/')
def log_out(request):
    logout(request)
    return redirect('/login/')

def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        else:
            messages.error(request, form.errors)
            return redirect(reverse('api:sign_up'))

    return render(request, 'api/signup.html', {'form': form})
