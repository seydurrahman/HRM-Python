from django import forms
from .models import Employee
from apps.accounts.models import (
    User, CompanyUnit, Division, Department,
    Section, SubSection, Floor, Line
)

class EmployeeForm(forms.ModelForm):
    # User fields
    full_name_English = forms.CharField(max_length=30, required=True)
    full_name_Bangla = forms.CharField(max_length=60, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "date_of_joining": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "date_of_confirmation": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "employee_id": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "blood_grp": forms.Select(attrs={"class": "form-control"}),
            "marital_status": forms.Select(attrs={"class": "form-control"}),
            "designation": forms.Select(attrs={"class": "form-control"}),
            "employment_type": forms.Select(attrs={"class": "form-control"}),
            "mobile_number": forms.TextInput(attrs={"class": "form-control"}),
            "personal_email": forms.EmailInput(attrs={"class": "form-control"}),
            "present_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "permanent_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "reporting_manager": forms.Select(attrs={"class": "form-control"}),
            "unit": forms.Select(attrs={"class": "form-control"}),
            "division": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "section": forms.Select(attrs={"class": "form-control"}),
            "sub_section": forms.Select(attrs={"class": "form-control"}),
            "floor": forms.Select(attrs={"class": "form-control"}),
            "line": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "weekend": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ----------------- CORRECTED -----------------
        # Start with empty cascading dropdowns
        self.fields["division"].queryset = Division.objects.none()
        self.fields["department"].queryset = Department.objects.none()
        self.fields["section"].queryset = Section.objects.none()
        self.fields["sub_section"].queryset = SubSection.objects.none()
        self.fields["floor"].queryset = Floor.objects.none()
        self.fields["line"].queryset = Line.objects.none()

        # Populate Units
        self.fields["unit"].queryset = CompanyUnit.objects.filter(is_active=True).order_by("name")

        data = self.data or None
        instance = getattr(self, 'instance', None)

        # If POST request, populate dependent fields
        if data:
            try:
                unit_id = data.get("unit")
                if unit_id:
                    self.fields["division"].queryset = Division.objects.filter(company_unit_id=unit_id, is_active=True).order_by("name")

                division_id = data.get("division")
                if division_id:
                    self.fields["department"].queryset = Department.objects.filter(division_id=division_id, is_active=True).order_by("name")

                department_id = data.get("department")
                if department_id:
                    self.fields["section"].queryset = Section.objects.filter(department_id=department_id, is_active=True).order_by("name")

                section_id = data.get("section")
                if section_id:
                    self.fields["sub_section"].queryset = SubSection.objects.filter(section_id=section_id, is_active=True).order_by("name")

                sub_section_id = data.get("sub_section")
                if sub_section_id:
                    self.fields["floor"].queryset = Floor.objects.filter(sub_section_id=sub_section_id, is_active=True).order_by("name")

                floor_id = data.get("floor")
                if floor_id:
                    self.fields["line"].queryset = Line.objects.filter(floor_id=floor_id, is_active=True).order_by("name")
            except (ValueError, TypeError):
                pass

        # If editing existing Employee instance, prepopulate cascading dropdowns
        elif instance and instance.pk:
            if instance.unit:
                self.fields["division"].queryset = Division.objects.filter(company_unit=instance.unit, is_active=True)
            if instance.division:
                self.fields["department"].queryset = Department.objects.filter(division=instance.division, is_active=True)
            if instance.department:
                self.fields["section"].queryset = Section.objects.filter(department=instance.department, is_active=True)
            if instance.section:
                self.fields["sub_section"].queryset = SubSection.objects.filter(section=instance.section, is_active=True)
            if instance.sub_section:
                self.fields["floor"].queryset = Floor.objects.filter(sub_section=instance.sub_section, is_active=True)
            if instance.floor:
                self.fields["line"].queryset = Line.objects.filter(floor=instance.floor, is_active=True)
        # ---------------------------------------------

        # Optional fields not required
        for f in ["blood_grp", "personal_email", "photo", "reporting_manager"]:
            if f in self.fields:
                self.fields[f].required = False

        # Add form-control class if missing
        for field_name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
