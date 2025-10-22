# apps/accounts/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm, ChangePasswordForm
from django.contrib.auth.models import Group
from .models import CustomGroup,CompanyUnit,Division,Section,SubSection,Floor,Line
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST



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
    groups = CustomGroup.objects.all().order_by("id")  # fetch all groups
    return render(request, "groups/group_list.html", {"groups": groups})


@login_required
def create_unit(request):
    groups = CustomGroup.objects.filter(is_active=True).order_by("name")
    units = CompanyUnit.objects.select_related('group').all().order_by("id")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        group_id = request.POST.get("group_id")
        code = (request.POST.get("code") or "").strip()
        is_active = request.POST.get("is_active") in ("on", "1", "true", "True")

        if not name:
            messages.error(request, "Unit name is required.")
        elif not group_id or not group_id.isdigit():
            messages.error(request, "Please select a valid group.")
        else:
            group = get_object_or_404(CustomGroup, id=int(group_id))
            # prevent duplicate unit names within the same group
            if CompanyUnit.objects.filter(name__iexact=name, group=group).exists():
                messages.error(request, "A unit with this name already exists in the selected group.")
            else:
                # create unit (include code/is_active if model supports them)
                cu_kwargs = {"name": name, "group": group}
                if code:
                    cu_kwargs["code"] = code
                # only set is_active if the model has that field; safe to pass if present
                try:
                    CompanyUnit.objects.create(**cu_kwargs, is_active=is_active)
                except TypeError:
                    # fallback: model may not accept is_active keyword
                    CompanyUnit.objects.create(**cu_kwargs)
                messages.success(request, "Company / Unit created successfully!")
                return redirect("accounts:create_unit")

    context = {"units": units, "groups": groups}
    return render(request, "unit/create_unit.html", context)

@login_required
def unit_list(request):
    search_query = request.GET.get("q", "").strip()
    group_filter = request.GET.get("group", "").strip()

    # Base queryset
    units = CompanyUnit.objects.select_related("group").order_by("id")

    # Optional filtering by search or group
    if search_query:
        units = units.filter(name__icontains=search_query)
    if group_filter:
        units = units.filter(group_id=group_filter)

    # Pagination (10 units per page)
    paginator = Paginator(units, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "units": page_obj,
        "search_query": search_query,
        "group_filter": group_filter,
    }
    return render(request, "unit/unit_list.html", context)

@login_required
@require_POST
def toggle_unit_status(request, unit_id):
    unit = get_object_or_404(CompanyUnit, id=unit_id)
    unit.is_active = not unit.is_active
    unit.save()
    return JsonResponse({
        "success": True,
        "new_status": unit.is_active
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomGroup, CompanyUnit, Division

@login_required
def create_division(request):
    groups = CustomGroup.objects.filter(is_active=True).order_by("name")
    units = CompanyUnit.objects.filter(is_active=True).order_by("name")
    divisions = Division.objects.select_related("company_unit", "group").all().order_by("id")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        group_id = request.POST.get("group_id")
        unit_id = request.POST.get("unit_id")
        code = (request.POST.get("code") or "").strip()
        is_active = request.POST.get("is_active") in ("on", "1", "true", "True")

        if not name:
            messages.error(request, "Division name is required.")
        elif not group_id or not group_id.isdigit():
            messages.error(request, "Please select a valid group.")
        elif not unit_id or not unit_id.isdigit():
            messages.error(request, "Please select a valid unit.")
        else:
            group = get_object_or_404(CustomGroup, id=int(group_id))
            company_unit = get_object_or_404(CompanyUnit, id=int(unit_id))

            # prevent duplicate division names within same group & unit
            if Division.objects.filter(name__iexact=name, group=group, company_unit=company_unit).exists():
                messages.error(request, "A division with this name already exists in the selected group and unit.")
            else:
                division_kwargs = {"name": name, "group": group, "company_unit": company_unit}
                if code:
                    division_kwargs["code"] = code
                try:
                    Division.objects.create(**division_kwargs, is_active=is_active)
                except TypeError:
                    Division.objects.create(**division_kwargs)

                messages.success(request, "Division created successfully!")
                return redirect("accounts:division_list")

    context = {"units": units, "groups": groups, "divisions": divisions}
    return render(request, "division/create_division.html", context)

@login_required
def division_list(request):
    divisions = Division.objects.select_related("group", "company_unit").order_by("id")

    paginator = Paginator(divisions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"divisions": page_obj}
    return render(request, "division/division_list.html", context)

@login_required
def get_units_by_group(request):
    group_id = request.GET.get("group_id")
    if not group_id:
        return JsonResponse({"units": []})

    units = CompanyUnit.objects.filter(group_id=group_id, is_active=True).values("id", "name")
    return JsonResponse({"units": list(units)})