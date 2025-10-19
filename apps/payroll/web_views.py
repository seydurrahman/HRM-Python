from django.shortcuts import render
from .models import Payroll  # adjust according to your model

def payroll_list_view(request):
    """Display all payroll records"""
    payrolls = Payroll.objects.all()
    return render(request, "payroll/payroll_list.html", {"payrolls": payrolls})

def payroll_create_view(request):
    """Create a new payroll entry"""
    # Add form handling later
    return render(request, "payroll/payroll_create.html")
