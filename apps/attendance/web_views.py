from django.shortcuts import render
from .models import Attendance

def attendance_list_view(request):
    # Fetch attendance records
    attendances = Attendance.objects.all()
    return render(request, "attendance/attendance_list.html", {"attendances": attendances})

def attendance_create_view(request):
    # Attendance creation logic
    return render(request, "attendance/attendance_create.html")
