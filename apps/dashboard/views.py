from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import LeaveRequest
from apps.payroll.models import Payroll

class DashboardAPIView(APIView):
    """Dashboard Overview Statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        # Employee Statistics
        total_employees = Employee.objects.filter(is_active=True).count()
        new_employees_this_month = Employee.objects.filter(
            date_of_joining__month=current_month,
            date_of_joining__year=current_year
        ).count()
        
        employees_by_department = Employee.objects.filter(
            is_active=True
        ).values('department').annotate(count=Count('id'))
        
        employees_by_type = Employee.objects.filter(
            is_active=True
        ).values('employment_type').annotate(count=Count('id'))
        
        # Attendance Statistics
        today_attendance = Attendance.objects.filter(date=today).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            on_leave=Count('id', filter=Q(status='ON_LEAVE'))
        )
        
        # Leave Statistics
        pending_leave_requests = LeaveRequest.objects.filter(
            status='PENDING'
        ).count()
        
        approved_leaves_this_month = LeaveRequest.objects.filter(
            status='APPROVED',
            start_date__month=current_month,
            start_date__year=current_year
        ).count()
        
        # Payroll Statistics
        payroll_stats = Payroll.objects.filter(
            month=current_month,
            year=current_year
        ).aggregate(
            total_payroll=Sum('net_salary'),
            avg_salary=Avg('net_salary'),
            processed=Count('id', filter=Q(status='PROCESSED')),
            paid=Count('id', filter=Q(status='PAID'))
        )
        
        # Upcoming Events (next 7 days)
        next_week = today + timedelta(days=7)
        from apps.attendance.models import Holiday
        upcoming_holidays = Holiday.objects.filter(
            date__gte=today,
            date__lte=next_week
        ).values('name', 'date')
        
        # User-specific data
        user_data = {}
        if hasattr(request.user, 'employee_profile'):
            employee = request.user.employee_profile
            
            # My attendance this month
            my_attendance = Attendance.objects.filter(
                employee=employee,
                date__month=current_month,
                date__year=current_year
            ).aggregate(
                total_days=Count('id'),
                present=Count('id', filter=Q(status='PRESENT')),
                total_hours=Sum('total_hours')
            )
            
            # My leave balance
            from apps.leave_management.models import LeaveBalance
            my_leave_balance = LeaveBalance.objects.filter(
                employee=employee,
                year=current_year
            ).values('leave_type__name', 'remaining_days')
            
            # My pending requests
            my_pending_requests = LeaveRequest.objects.filter(
                employee=employee,
                status='PENDING'
            ).count()
            
            user_data = {
                'my_attendance': my_attendance,
                'my_leave_balance': list(my_leave_balance),
                'my_pending_requests': my_pending_requests
            }
        
        return Response({
            'overview': {
                'total_employees': total_employees,
                'new_employees_this_month': new_employees_this_month,
                'employees_by_department': list(employees_by_department),
                'employees_by_type': list(employees_by_type)
            },
            'attendance': {
                'today': today_attendance,
            },
            'leave': {
                'pending_requests': pending_leave_requests,
                'approved_this_month': approved_leaves_this_month
            },
            'payroll': payroll_stats,
            'upcoming_holidays': list(upcoming_holidays),
            'user_data': user_data
        })

class ReportsAPIView(APIView):
    """Generate Various Reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        report_type = request.query_params.get('type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        employee_id = request.query_params.get('employee_id')
        
        if report_type == 'attendance':
            return self.attendance_report(start_date, end_date, employee_id)
        elif report_type == 'leave':
            return self.leave_report(start_date, end_date, employee_id)
        elif report_type == 'payroll':
            return self.payroll_report(start_date, end_date, employee_id)
        elif report_type == 'employee':
            return self.employee_report()
        else:
            return Response({'error': 'Invalid report type'}, status=400)
    
    def attendance_report(self, start_date, end_date, employee_id):
        """Attendance Report"""
        filters = Q()
        if start_date:
            filters &= Q(date__gte=start_date)
        if end_date:
            filters &= Q(date__lte=end_date)
        if employee_id:
            filters &= Q(employee_id=employee_id)
        
        attendances = Attendance.objects.filter(filters).values(
            'employee__employee_id',
            'employee__user__first_name',
            'employee__user__last_name',
            'employee__department__name'
        ).annotate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status='PRESENT')),
            absent_days=Count('id', filter=Q(status='ABSENT')),
            leave_days=Count('id', filter=Q(status='ON_LEAVE')),
            total_hours=Sum('total_hours'),
            overtime_hours=Sum('overtime_hours')
        )
        
        return Response({
            'report_type': 'attendance',
            'data': list(attendances)
        })
    
    def leave_report(self, start_date, end_date, employee_id):
        """Leave Report"""
        filters = Q()
        if start_date:
            filters &= Q(start_date__gte=start_date)
        if end_date:
            filters &= Q(end_date__lte=end_date)
        if employee_id:
            filters &= Q(employee_id=employee_id)
        
        leaves = LeaveRequest.objects.filter(filters).values(
            'employee__employee_id',
            'employee__user__first_name',
            'employee__user__last_name',
            'leave_type__name'
        ).annotate(
            total_requests=Count('id'),
            approved=Count('id', filter=Q(status='APPROVED')),
            rejected=Count('id', filter=Q(status='REJECTED')),
            pending=Count('id', filter=Q(status='PENDING')),
            total_days=Sum('total_days', filter=Q(status='APPROVED'))
        )
        
        return Response({
            'report_type': 'leave',
            'data': list(leaves)
        })
    
    def payroll_report(self, start_date, end_date, employee_id):
        """Payroll Report"""
        filters = Q()
        if employee_id:
            filters &= Q(employee_id=employee_id)
        
        # For payroll, use month/year filters
        month = timezone.now().month
        year = timezone.now().year
        if start_date:
            from datetime import datetime
            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            month = date_obj.month
            year = date_obj.year
        
        payrolls = Payroll.objects.filter(
            filters, month=month, year=year
        ).values(
            'employee__employee_id',
            'employee__user__first_name',
            'employee__user__last_name',
            'employee__department__name'
        ).annotate(
            gross_salary=Sum('gross_earnings'),
            deductions=Sum('total_deductions'),
            net_salary=Sum('net_salary')
        )
        
        return Response({
            'report_type': 'payroll',
            'month': month,
            'year': year,
            'data': list(payrolls)
        })
    
    def employee_report(self):
        """Employee Demographics Report"""
        data = {
            'by_department': list(
                Employee.objects.filter(is_active=True).values(
                    'department'
                ).annotate(count=Count('id'))
            ),
            'by_designation': list(
                Employee.objects.filter(is_active=True).values(
                    'designation__title'
                ).annotate(count=Count('id'))
            ),
            'by_employment_type': list(
                Employee.objects.filter(is_active=True).values(
                    'employment_type'
                ).annotate(count=Count('id'))
            ),
            'by_gender': list(
                Employee.objects.filter(is_active=True).values(
                    'gender'
                ).annotate(count=Count('id'))
            ),
            'total_active': Employee.objects.filter(is_active=True).count(),
            'total_inactive': Employee.objects.filter(is_active=False).count()
        }
        
        return Response({
            'report_type': 'employee',
            'data': data
        })