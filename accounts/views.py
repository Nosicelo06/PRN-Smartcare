print("THIS IS MY VIEWS FILE")
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import StaffProfile

def home_view(request):
    return render(request, "accounts/home.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        surname = request.POST.get("surname")
        email = request.POST.get("email")
        cell_number = request.POST.get("cell_number")
        role = request.POST.get("role")
        password1 = request.POST.get("password1")
        confirmpassword = request.POST.get("confirmpassword")

        #check if passwords match
        if password1 != confirmpassword :
            messages.error(request, "Passwords do not match.")
            return redirect ("register")

        # check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("register")
            
        # Create a user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )
        user.is_active = False
        user.save()

        StaffProfile.objects.create(
            user=user,
            surname=surname,
            cell_number=cell_number,
            role=role,
        )
        messages.success(request, "Registration successful! Please check your email.")
        return redirect("login")

    return render(request, "accounts/register.html")