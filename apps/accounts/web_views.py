# apps/accounts/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm, ChangePasswordForm
from django.contrib.auth.models import Group
from .models import CustomGroup,CompanyUnit,Division,Department, Section,SubSection,Floor,Line
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

# Create Division
@login_required
def create_division(request):
    groups = CustomGroup.objects.filter(is_active=True).order_by('name')
    
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        group_id = request.POST.get("group_id")
        unit_id = request.POST.get("unit_id")
        is_active = request.POST.get("is_active") in ("on", "1", "true", "True")
        
        if not all([name, group_id, unit_id]):
            messages.error(request, "Please fill all required fields.")
            return redirect("accounts:create_division")
            
        try:
            company_unit = CompanyUnit.objects.get(id=unit_id, group_id=group_id)
            
            # ✅ use correct field name: company_unit
            if Division.objects.filter(name__iexact=name, company_unit=company_unit).exists():
                messages.error(request, "A division with this name already exists in the selected unit.")
                return redirect("accounts:create_division")
                
            # ✅ also assign company_unit instead of unit
            division = Division.objects.create(
                name=name,
                code=code,
                group_id=group_id,
                company_unit=company_unit,
                is_active=is_active
            )
            messages.success(request, "Division created successfully!")
            return redirect("accounts:division_list")
            
        except CompanyUnit.DoesNotExist:
            messages.error(request, "Invalid company unit selected.")
        except Exception as e:
            messages.error(request, f"Error creating division: {str(e)}")
    
    return render(request, "division/create_division.html", {
        "groups": groups
    })

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

@login_required
def toggle_division_status(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    division.is_active = not division.is_active
    division.save()
    messages.success(
        request,
        f"Division '{division.name}' is now {'Active' if division.is_active else 'Inactive'}."
    )
    return redirect("accounts:division_list")

# Create Department
@login_required
def create_department(request):
    groups = CustomGroup.objects.filter(is_active=True).order_by("name")
    units = CompanyUnit.objects.filter(is_active=True).order_by("name")
    divisions = Division.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        group_id = request.POST.get("group_id")
        unit_id = request.POST.get("unit_id")
        division_id = request.POST.get("division_id")
        code = (request.POST.get("code") or "").strip()
        is_active = request.POST.get("is_active") in ("on", "1", "true", "True")

        if not name:
            messages.error(request, "Department name is required.")
        elif not group_id or not group_id.isdigit():
            messages.error(request, "Please select a valid group.")
        elif not unit_id or not unit_id.isdigit():
            messages.error(request, "Please select a valid unit.")
        elif not division_id or not division_id.isdigit():
            messages.error(request, "Please select a valid division.")
        else:
            group = get_object_or_404(CustomGroup, id=int(group_id))
            company_unit = get_object_or_404(CompanyUnit, id=int(unit_id))
            division = get_object_or_404(Division, id=int(division_id))

            # prevent duplicate department names within same division
            if Department.objects.filter(name__iexact=name, division=division).exists():
                messages.error(request, "A department with this name already exists in the selected division.")
            else:
                dept_kwargs = {
                    "name": name,
                    "group": group,
                    "company_unit": company_unit,
                    "division": division,
                    "is_active": is_active,
                }
                if code:
                    dept_kwargs["code"] = code
                Department.objects.create(**dept_kwargs)
                messages.success(request, "Department created successfully!")
                return redirect("accounts:department_list")

    context = {"groups": groups, "units": units, "divisions": divisions}
    return render(request, "department/create_department.html", context)


@login_required
def department_list(request):
    departments = Department.objects.select_related("group", "company_unit", "division").order_by("id")
    paginator = Paginator(departments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"departments": page_obj}
    return render(request, "department/department_list.html", context)


@login_required
def get_divisions_by_unit(request):
    unit_id = request.GET.get("unit_id")
    if not unit_id:
        return JsonResponse({"divisions": []})
    divisions = Division.objects.filter(company_unit_id=unit_id, is_active=True).values("id", "name")
    return JsonResponse({"divisions": list(divisions)})


@login_required
def toggle_department_status(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    department.is_active = not department.is_active
    department.save()
    messages.success(
        request,
        f"Department '{department.name}' is now {'Active' if department.is_active else 'Inactive'}."
    )
    return redirect("accounts:department_list")


@login_required
def create_section(request):
    groups = CustomGroup.objects.filter(is_active=True).order_by("name")
    units = CompanyUnit.objects.filter(is_active=True).order_by("name")
    divisions = Division.objects.filter(is_active=True).order_by("name")
    departments = Department.objects.filter(is_active=True).order_by("name")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        code = (request.POST.get("code") or "").strip()
        department_id = request.POST.get("department_id")
        is_active = request.POST.get("is_active") in ("on", "1", "true", "True")

        errors = []
        if not name:
            errors.append("Section name is required.")
        if not department_id or not department_id.isdigit():
            errors.append("Please select a valid department.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            department = get_object_or_404(Department, id=int(department_id))

            # Prevent duplicate section names in the same department
            if Section.objects.filter(name__iexact=name, department=department).exists():
                messages.error(request, "A section with this name already exists in the selected department.")
            else:
                section = Section.objects.create(
                    name=name,
                    code=code,
                    department=department,
                    is_active=is_active,
                )
                messages.success(request, f"Section '{section.name}' created successfully!")
                return redirect("accounts:section_list")

    context = {
        "groups": groups,
        "units": units,
        "divisions": divisions,
        "departments": departments,
    }
    return render(request, "section/create_section.html", context)


# -----------------------------
# ✅ List Sections
# -----------------------------
@login_required
def section_list(request):
    sections = Section.objects.select_related(
        "department",
        "department__division",
        "department__division__company_unit",
        "department__division__company_unit__group"
    ).order_by("id")

    paginator = Paginator(sections, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"sections": page_obj}
    return render(request, "section/section_list.html", context)


# -----------------------------
# ✅ AJAX: Get divisions & departments by unit
# -----------------------------
@login_required
def get_divisions_and_departments_by_unit(request):
    unit_id = request.GET.get("unit_id")

    if not unit_id:
        return JsonResponse({"divisions": [], "departments": []})

    divisions = Division.objects.filter(company_unit_id=unit_id, is_active=True).values("id", "name")
    departments = Department.objects.filter(division__in=divisions, is_active=True).values("id", "name")

    return JsonResponse({
        "divisions": list(divisions),
        "departments": list(departments)
    })


# -----------------------------
# ✅ AJAX: Get departments by division
# -----------------------------
@login_required
def get_departments_by_division(request):
    division_id = request.GET.get("division_id")

    if not division_id:
        return JsonResponse({"departments": []})

    departments = Department.objects.filter(division_id=division_id, is_active=True).values("id", "name")
    return JsonResponse({"departments": list(departments)})


# -----------------------------
# ✅ Toggle Section Active/Inactive
# -----------------------------
@login_required
@require_POST
def toggle_section_status(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    section.is_active = not section.is_active
    section.save(update_fields=["is_active"])

    status_text = "activated" if section.is_active else "deactivated"
    messages.success(request, f"Section '{section.name}' has been {status_text} successfully.")
    return redirect("accounts:section_list")