from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee
from .forms import EmployeeForm
from apps.accounts.models import User

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
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create User first
                user = User.objects.create_user(
                    username=form.cleaned_data['employee_id'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password='temp123'  # Default password
                )
                
                # Create Employee instance but don't save yet
                employee = form.save(commit=False)
                employee.user = user
                employee.created_by = request.user
                employee.save()
                
                messages.success(request, f'Employee {employee.employee_id} created successfully!')
                return redirect('employees:list')
                
            except Exception as e:
                messages.error(request, f'Error creating employee: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'title': 'Create Employee'
    }
    return render(request, "employees/employee_create.html", context)

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