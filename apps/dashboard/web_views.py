from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import LeaveRequest, LeaveBalance
from apps.payroll.models import Payroll

def home_view(request):
    """Home page - redirect based on authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return redirect('accounts:login')

@login_required
def dashboard_view(request):
    """Main dashboard - redirect based on role"""
    if request.user.is_admin or request.user.is_hr:
        return redirect('dashboard:admin_dashboard')
    else:
        return redirect('dashboard:employee_dashboard')

@login_required
def admin_dashboard_view(request):
    """Admin/HR Dashboard"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Employee Statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    new_employees_this_month = Employee.objects.filter(
        date_of_joining__month=current_month,
        date_of_joining__year=current_year
    ).count()
    
    # Attendance Today
    today_attendance = Attendance.objects.filter(date=today).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT')),
        absent=Count('id', filter=Q(status='ABSENT')),
        on_leave=Count('id', filter=Q(status='ON_LEAVE'))
    )
    
    # Leave Requests
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    
    # Department-wise employees
    employees_by_dept = Employee.objects.filter(
        is_active=True
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Recent employees
    recent_employees = Employee.objects.filter(
        is_active=True
    ).select_related('user', 'department').order_by('-date_of_joining')[:5]
    
    # Payroll stats
    payroll_stats = Payroll.objects.filter(
        month=current_month,
        year=current_year
    ).aggregate(
        total=Sum('net_salary'),
        processed=Count('id', filter=Q(status='PROCESSED')),
        paid=Count('id', filter=Q(status='PAID'))
    )
    
    context = {
        'total_employees': total_employees,
        'new_employees': new_employees_this_month,
        'today_attendance': today_attendance,
        'pending_leaves': pending_leaves,
        'employees_by_dept': employees_by_dept,
        'recent_employees': recent_employees,
        'payroll_stats': payroll_stats,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def employee_dashboard_view(request):
    """Employee Dashboard"""
    try:
        employee = request.user.employee_profile
    except:
        return render(request, 'dashboard/no_profile.html')
    
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # My Attendance
    my_attendance = Attendance.objects.filter(
        employee=employee,
        date__month=current_month,
        date__year=current_year
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT')),
        total_hours=Sum('total_hours')
    )
    
    # Today's Attendance
    today_attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    # Leave Balance
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')
    
    # My Leave Requests
    my_leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]
    
    # Upcoming holidays
    from apps.attendance.models import Holiday
    upcoming_holidays = Holiday.objects.filter(
        date__gte=today
    ).order_by('date')[:5]
    
    context = {
        'employee': employee,
        'my_attendance': my_attendance,
        'today_attendance': today_attendance,
        'leave_balances': leave_balances,
        'my_leave_requests': my_leave_requests,
        'upcoming_holidays': upcoming_holidays,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'dashboard/employee_dashboard.html', context)