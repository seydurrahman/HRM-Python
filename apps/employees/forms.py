from django import forms
from .models import Employee
from apps.accounts.models import User

class EmployeeForm(forms.ModelForm):
    # User fields
    full_name_English = forms.CharField(max_length=30, required=True)
    full_name_Bangla = forms.CharField(max_length=60, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_confirmation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_grp': forms.Select(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'present_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reporting_manager': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'division': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_section': forms.TextInput(attrs={'class': 'form-control'}),
            'floor': forms.TextInput(attrs={'class': 'form-control'}),
            'line': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'weekend': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        self.fields['blood_group'].required = False
        self.fields['personal_email'].required = False
        self.fields['photo'].required = False
        self.fields['reporting_manager'].required = False
        
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

