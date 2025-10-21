# apps/accounts/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm, ChangePasswordForm
from django.contrib.auth.models import Group
from .models import CustomGroup


def web_login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data.get("remember_me", False)

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                next_url = request.GET.get("next", "dashboard:dashboard")
                return redirect(next_url)
            messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def web_register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.role = "EMPLOYEE"
            user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect("accounts:login")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def web_profile_view(request):
    context = {"user": request.user}
    try:
        context["employee"] = request.user.employee_profile
    except Exception:
        context["employee"] = None
    return render(request, "accounts/profile.html", context)


@login_required
def web_change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


def create_group(request):
    # Fetch all existing groups (active and inactive)
    groups = CustomGroup.objects.all().order_by("id")
    
    if request.method == "POST":
        name = request.POST.get("name")
        is_active = request.POST.get("is_active", True)  # Default to True

        if CustomGroup.objects.filter(name=name).exists():
            messages.error(request, "Group already exists!")
        else:
            CustomGroup.objects.create(
                name=name, 
                is_active=bool(is_active)
            )
            messages.success(request, "Group created successfully!")
            return redirect("accounts:group_list")

    context = {'groups': groups}
    return render(request, "groups/create_group.html", context)
@login_required
def toggle_group_status(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    group.is_active = not group.is_active
    group.save()
    
    status = "activated" if group.is_active else "deactivated"
    messages.success(request, f"Group {group.name} has been {status}!")
    return redirect("accounts:group_list")

@login_required
def group_list(request):
    groups = Group.objects.all().order_by("id")  # fetch all groups
    return render(request, "groups/group_list.html", {"groups": groups})
