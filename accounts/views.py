print("THIS IS MY VIEWS FILE")
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

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
            return redirect("patients:list")
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

        # Check if passwords match
        if password1 != confirmpassword:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check if email already exists
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

        # Create staff profile
        StaffProfile.objects.create(
            user=user,
            surname=surname,
            cell_number=cell_number,
            role=role,
        )

        # Create verification link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verification_link = f"http://127.0.0.1:8000/verify/{uid}/{token}/"

        # Send verification email
        send_mail(
            "Verify your PRN SmartCare account",
            f"Hello {first_name},\n\n"
            f"Please click the link below to verify your email:\n\n"
            f"{verification_link}\n\n"
            f"Thank you,\nPRN SmartCare",
            "noreply@prnsmartcare.com",
            [email],
        )

        messages.success(
            request,
            "Registration successful! Please check your email."
        )

        return redirect("login")

    return render(request, "accounts/register.html")

def verify_email(request, uidb64, token):
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Your email has been verified! You can now log in.")
        return redirect("login")

    messages.error(request, "The verification link is invalid or has expired.")
    return redirect("login")