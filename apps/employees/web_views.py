from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import EmployeeForm
from .models import Employee
from django.contrib import messages
from apps.accounts.models import User, CompanyUnit, Division, Department, Section, SubSection, Floor, Line

@login_required
def employee_list_view(request):
    employees = Employee.objects.select_related(
        'user', 'department', 'designation'
    ).all().order_by('-date_of_joining')
    
    context = {
        'employees': employees
    }
    return render(request, "employees/employee_list.html", context)

@login_required
def employee_create_view(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("employees:list")
    else:
        form = EmployeeForm()
    return render(request, "employees/employee_create.html", {"form": form})

@login_required
def employee_update_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            try:
                # Update User information
                employee.user.first_name = form.cleaned_data['first_name']
                employee.user.last_name = form.cleaned_data['last_name']
                employee.user.email = form.cleaned_data['email']
                employee.user.save()
                
                form.save()
                messages.success(request, f'Employee {employee.employee_id} updated successfully!')
                return redirect('employees:list')
                
            except Exception as e:
                messages.error(request, f'Error updating employee: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with existing data
        form = EmployeeForm(instance=employee)
        form.fields['first_name'].initial = employee.user.first_name
        form.fields['last_name'].initial = employee.user.last_name
        form.fields['email'].initial = employee.user.email
    
    context = {
        'form': form,
        'employee': employee,
        'title': 'Update Employee'
    }
    return render(request, "employees/employee_create.html", context)

@login_required
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_id = employee.employee_id
        employee.delete()
        messages.success(request, f'Employee {employee_id} deleted successfully!')
        return redirect('employees:list')
    
    context = {
        'employee': employee
    }
    return render(request, "employees/employee_confirm_delete.html", context)

@login_required
def ajax_load_divisions(request):
    company_unit_id = request.GET.get('id_unit')
    divisions = Division.objects.filter(company_unit_id=company_unit_id, is_active=True).order_by('name') if company_unit_id else Division.objects.none()
    return JsonResponse({'id_division': [{'id': d.id, 'name': d.name} for d in divisions]})

@login_required
def ajax_load_departments(request):
    division_id = request.GET.get('id_division')
    departments = Department.objects.filter(division_id=division_id, is_active=True).order_by('name') if division_id else Department.objects.none()
    return JsonResponse({'id_department': [{'id': d.id, 'name': d.name} for d in departments]})

@login_required
def ajax_load_sections(request):
    department_id = request.GET.get('id_department')
    sections = Section.objects.filter(department_id=department_id, is_active=True).order_by('name') if department_id else Section.objects.none()
    return JsonResponse({'id_section': [{'id': s.id, 'name': s.name} for s in sections]})

@login_required
def ajax_load_sub_sections(request):
    section_id = request.GET.get('id_section')
    sub_sections = SubSection.objects.filter(section_id=section_id, is_active=True).order_by('name') if section_id else SubSection.objects.none()
    return JsonResponse({'id_sub_section': [{'id': ss.id, 'name': ss.name} for ss in sub_sections]})

@login_required
def ajax_load_floors(request):
    sub_section_id = request.GET.get('id_sub_section')
    floors = Floor.objects.filter(subsection_id=sub_section_id, is_active=True).order_by('name') if sub_section_id else Floor.objects.none()
    return JsonResponse({'id_floor': [{'id': f.id, 'name': f.name} for f in floors]})


@login_required
def ajax_load_lines(request):
    floor_id = request.GET.get('id_floor')
    lines = Line.objects.filter(floor_id=floor_id, is_active=True).order_by('name') if floor_id else Line.objects.none()
    return JsonResponse({'id_line': [{'id': l.id, 'name': l.name} for l in lines]})