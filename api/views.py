# ref: https://realpython.com/getting-started-with-django-channels/ 202105
from django.shortcuts import render, redirect
from django.http import HttpResponse #, HttpResponseRedirect
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.contrib import messages
from .models import apitest
import logging #Logger

logger = logging.getLogger(__file__)

# Create your views here.

#def dboard(request): ## move to djapi.py
#    records = apitest.objects.count()
#    return render(request, "api/dboard.html", {"records": records})

# User Handler
User = get_user_model()

@login_required(login_url='/login/') # @decorator to both our user list and log out views to restrict access only to registered users.
def user_handler(request):
    users = User.objects.select_related('apiuser')
    for user in users:
        user.status = 'Online' if hasattr(user, 'apiuser') else 'Offline'
    return render(request, 'user/user.html', {'users': users})

def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            #logger.info("User Login Trial: %s", form.get_user()) #logger works here
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                #if user.is_active:
                login(request, user)
                #return HttpResponseRedirect(reverse('apitest:dboard', username)) #find name is 'dboard' under api app
                return redirect(reverse('apitest:user_handler'))
            else:
                logger.info("No User found!!") #If error occurs and usage of logger seems not work (in form.is_valid, loggers works well)
                #messages.info(request,'username or password not correct') #Django give its own error message in base.html messages template
                #return redirect('login') #stay here
        else:
            messages.error(request, form.errors) #Seems no effect??

    return render(request, 'user/login.html', {'form': form})

@login_required(login_url='/login')
def log_out(request):
    logout(request)
    return redirect('/login')

def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
        else:
            messages.error(request, form.errors) #Seems no effect??
            #return redirect(reverse('apitest:sign_up')) #stay here

    return render(request, 'user/signup.html', {'form': form})
