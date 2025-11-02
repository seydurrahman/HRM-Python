from django import forms
from .models import Employee
from apps.accounts.models import User, CompanyUnit, Division, Department, Section, SubSection, Floor, Line


class EmployeeForm(forms.ModelForm):
    # User fields
    full_name_English = forms.CharField(max_length=30, required=True)
    full_name_Bangla = forms.CharField(max_length=60, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_of_joining": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_of_confirmation": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "employee_id": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "blood_grp": forms.Select(attrs={"class": "form-control"}),
            "marital_status": forms.Select(attrs={"class": "form-control"}),
            "designation": forms.Select(attrs={"class": "form-control"}),
            "employment_type": forms.Select(attrs={"class": "form-control"}),
            "mobile_number": forms.TextInput(attrs={"class": "form-control"}),
            "personal_email": forms.EmailInput(attrs={"class": "form-control"}),
            "present_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "permanent_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "reporting_manager": forms.Select(attrs={"class": "form-control"}),
            "unit": forms.Select(attrs={"class": "form-control"}),
            "division": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "sub_section": forms.TextInput(attrs={"class": "form-control"}),
            "floor": forms.TextInput(attrs={"class": "form-control"}),
            "line": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "weekend": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # company units: show only active ones
        self.fields["unit"].queryset = CompanyUnit.objects.filter(
            is_active=True
        ).order_by("name")

        # start with no divisions shown
        self.fields["division"].queryset = Division.objects.none()

        # If POSTed (form submission), filter divisions by selected unit in request.POST
        if "unit" in self.data:
            try:
                unit_id = int(self.data.get("unit"))
                self.fields["division"].queryset = Division.objects.filter(
                    unit_id=unit_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass  # invalid input; leave empty

        # If editing an existing Employee instance, populate division queryset with that unit
        elif self.instance and getattr(self.instance, "unit", None):
            unit = self.instance.unit
            self.fields["division"].queryset = Division.objects.filter(
                unit=unit, is_active=True
            ).order_by("name")

        # keep the rest of your existing init modifications (class styling, optional fields)
        try:
            self.fields["blood_group"].required = False
            self.fields["personal_email"].required = False
            self.fields["photo"].required = False
            self.fields["reporting_manager"].required = False
        except KeyError:
            # ignore if fields aren't present or named differently
            pass

        for field_name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
