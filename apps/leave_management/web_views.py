from django.shortcuts import render
from .models import LeaveRequest  # adjust according to your model

def leave_list_view(request):
    """Show all leave requests"""
    leaves = LeaveRequest.objects.all()
    return render(request, "leave_management/leave_list.html", {"leaves": leaves})

def leave_create_view(request):
    """Page to create a new leave request"""
    # You can add form handling here later
    return render(request, "leave_management/leave_create.html")
