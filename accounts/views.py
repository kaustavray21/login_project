from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib import messages
from .forms import LoginForm
from django.views.decorators.cache import never_cache # Import the decorator

#... home_view remains the same ...
def home_view(request):
    return render(request, 'home.html')

@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect if user is already logged in
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect if user is already logged in

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    messages.error(request, "Admins must log in through the admin login page.")
                    return redirect('login')
                
                login(request, user)
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.login_count += 1
                profile.save()
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@never_cache
def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect if user is already logged in

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.login_count += 1
                    profile.save()
                    return redirect('dashboard')
                else:
                    messages.error(request, "You are not authorized to access this page.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'admin_login.html', {'form': form})

#... dashboard_view, logout_view, and admin_dashboard_view remain the same ...
@login_required
def dashboard_view(request):
    # This view is already protected by @login_required
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'login_count': profile.login_count
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    profiles = UserProfile.objects.all().exclude(user=request.user)
    context = {
        'profiles': profiles
    }
    return render(request, 'admin_dashboard.html', context)