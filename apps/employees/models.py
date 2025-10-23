from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User,CompanyUnit, Department, Designation, Section
from multiselectfield import MultiSelectField
from django_countries.fields import CountryField

class Employee(models.Model):
    """Employee Model - Main employee information"""
    
    EMPLOYMENT_TYPE = [
        ('PERMANENT', 'Permanent'),
        ('CONTRACT', 'Contract'),
        ('PART_TIME', 'Part Time'),
        ('INTERN', 'Intern'),
        ('PROBATION', 'Probation'),
        ('MTO', 'Management Trainee Officer')
    ]

    EMPLOYEE_TYPE = [
        ('MANAGEMENT', 'Management'),
        ('MANAGEMENT_STAFF', 'Management Staff'),
        ('GENERAL_STAFF', 'General Staff'),
        ('WORKER', 'Worker'),
    ]

    EMPLOYEE_CATEGORY = [
        ('OT', 'Overtime'),
        ('NON_OT', 'Non Overtime'),
    ]
    WORK_SHIFT = [
        ('GENERAL-8', 'General-8'),
        ('GENERAL-10', 'General-10'),
        ('GENERAL-12', 'General-12'),
        ('DAY-8', 'Day-8'),
        ('DAY-10', 'Day-10'),
        ('DAY-12', 'Day-12'),
        ('NIGHT-8', 'Night-8'),
        ('NIGHT-10', 'Night-10'),
        ('NIGHT-12', 'Night-12'),
    ]
    WEEKEND = [
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
    ]
    MARITAL_STATUS = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    GENDER = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]
    BLOOD_GROUP = (
        ("A+", "A+"),
        ("B+", "B+"),  # Changed from "A+" to "B+"
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("A-", "A-"),
        ("B-", "B-"),
        ("O+", "O+"),  # Added O+ and O- if needed
        ("O-", "O-"),
    )
    BANK_NAME = [
        ('DHAKA_BANK', 'Dhaka Bank'),
        ('BRAC_BANK', 'BRAC Bank'),
        ('NCC_BANK', 'NCC Bank'),
        ('CITY_BANK', 'City Bank'),
        ('STANDARD_CHARTERED', 'Standard Chartered'),
        ('DUTCH_BANGLA', 'Dutch Bangla'),
        ('ISLAMIC_BANK', 'Islamic Bank'),
    ]


    # User relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')

    # Employee Information
    # Name from forms: full_name_English, full_name_Bangla, email
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
    unit = models.ForeignKey(CompanyUnit, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    division = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    sub_section = models.CharField(max_length=100, blank=True, null=True)
    floor = models.CharField(max_length=50, blank=True, null=True)
    line = models.CharField(max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)

    # Basic Information
    date_of_birth = models.DateField()
    father_name = models.CharField(max_length=100)
    father_name_Bangla = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100)
    mother_name_Bangla = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    nationality = CountryField(default="BD")
    nid_number = models.CharField(max_length=50, unique=True)
    nid_image = models.FileField(upload_to='nid_images/', null=True, blank=True)
    birth_Reg= models.CharField(max_length=50, blank=True, null=True)
    birth_Reg_image = models.FileField(upload_to='birth_reg_images/', null=True, blank=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_image = models.FileField(upload_to='passport_images/', null=True, blank=True)
    personal_email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER, default="Male")
    blood_grp = models.CharField(max_length=10, choices=BLOOD_GROUP)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS)
    country = models.CharField(max_length=100, default='Bangladesh')
    division= models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    thana = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)
    post_office_Bangla = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10)
    village = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255, blank=True, null=True)
    address_line_Bangla = models.CharField(max_length=255, blank=True, null=True)
    # city = models.CharField(max_length=100)
    # state = models.CharField(max_length=100)
    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_name_Bangla = models.CharField(max_length=100, blank=True, null=True)
    nominee_relation = models.CharField(max_length=50, blank=True, null=True)
    nominee_mobile = models.CharField(max_length=15, blank=True, null=True)
    nominee_nid = models.CharField(max_length=50, blank=True, null=True)
    nominee_dob = models.DateField(null=True, blank=True)
    nominee_country = models.CharField(max_length=100, blank=True, null=True, default='Bangladesh')
    nominee_division= models.CharField(max_length=100, blank=True, null=True)
    nominee_district = models.CharField(max_length=100, blank=True, null=True)
    nominee_thana = models.CharField(max_length=100, blank=True, null=True)
    nominee_post_office = models.CharField(max_length=100, blank=True, null=True)
    nominee_post_office_Bangla = models.CharField(max_length=100, blank=True, null=True)
    nominee_postal_code = models.CharField(max_length=10, blank=True, null=True)
    nominee_village = models.CharField(max_length=100, blank=True, null=True)
    nominee_photo = models.FileField(upload_to='nominee_photos/', null=True, blank=True)
    nominee_nid_image = models.FileField(upload_to='nominee_nid_images/', null=True, blank=True)
    
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    emergency_contact_relation = models.CharField(max_length=50)

    local_guardian_name = models.CharField(max_length=100, blank=True, null=True)
    local_guardian_number = models.CharField(max_length=15, blank=True, null=True)
    local_guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    local_guardian_address = models.CharField(max_length=255, blank=True, null=True)

    Indentity_sign = models.CharField(max_length=255, blank=True, null=True)
    weight = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    height = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    
    # Employment Details
    device_id = models.CharField(max_length=50, blank=True, null=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='PERMANENT')
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE, default='WORKER')
    employee_category = models.CharField(max_length=10, choices=EMPLOYEE_CATEGORY, default='OT')
    group = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    date_of_joining = models.DateField()
    date_of_confirmation = models.DateField(null=True, blank=True)
    probation_period_months = models.IntegerField(default=6)
    reporting_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    work_shift = models.CharField(max_length=50, blank=True, null=True, choices=WORK_SHIFT, default='GENERAL-8')
    weekend = MultiSelectField(max_length=50, blank=True, null=True, choices=WEEKEND, default='FRIDAY')
    disburse_type = models.CharField(max_length=50, blank=True, null=True)
    mfs_number = models.CharField(max_length=50, blank=True, null=True)
    # mobile number field is already defined above
    # email field is in User model
    work_location = models.CharField(max_length=100, blank=True, null=True)
    bgmea_id = models.CharField(max_length=50, blank=True, null=True)
    bkmea_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True, null=True, choices=BANK_NAME)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    amount_in_bank = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tin_number = models.CharField(max_length=50, blank=True, null=True)

    software_user = models.BooleanField(default=False)
    panel_user = models.BooleanField(default=False)
    transport = models.BooleanField(default=False)
    food_allowance = models.BooleanField(default=False)
    

    #  Job Experience
    company_name = models.CharField(max_length=200, blank=True, null=True)
    # department from above
    job_title = models.CharField(max_length=100)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True, null=True)
    reason_for_leaving = models.CharField(max_length=100)
    experienced = models.CharField(max_length=100)
    experienced_certificate= models.ImageField(null=True)
    remarks= models.CharField(max_length=200)

    # Salary Info
    # effective date from joining date
    salary_policy = models.CharField(max_length=50)
    gross_salary = models.CharField(max_length=100)
    basic_salary = models.CharField(max_length=100)
    house_rent = models.CharField(max_length=100)
    transport_allowance = models.CharField(max_length=100)
    mobile_bill = models.CharField(max_length=100)
    food_allowance = models.CharField(max_length=100)
    medical_allowance = models.CharField(max_length=100)
    other_conveyence = models.CharField(max_length=100)
    attendance_bonus = models.CharField(max_length=100)
    tax_deduction = models.CharField(max_length=100)
    insurance = models.CharField(max_length=100)
    stamp = models.CharField(max_length=100)
    salary_mode = models.CharField(max_length=100)
    # tin number coming from above
    pF_applicable = models.BooleanField(default=False)
    late_deduct = models.BooleanField(default=False)
    transport_deduct = models.BooleanField(default=False)
    food_deduct = models.BooleanField(default=False)

    # Educations
    degree_Name =models.CharField(max_length=50)
    institue =models.CharField(max_length=50)
    board =models.CharField(max_length=50)
    subject =models.CharField(max_length=50)
    passing_year =models.CharField(max_length=50)
    result =models.CharField(max_length=50)
    # certificate come from below
    certificate = models.FileField(upload_to='', null=True, blank=True)

    # Leave info
    # at present static file but late we collect from other entry from django.db import models

    # Training & Certificate
    training_name = models.CharField(max_length=100)
    institue_name = models.CharField(max_length=100)
    duration_Month = models.CharField(max_length=50)
    score = models.CharField(max_length=50)
    




    # Status
    is_active = models.BooleanField(default=True)
    resignation_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    exit_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_employees'
    )
    
    class Meta:
        db_table = 'employees'
        ordering = ['-date_of_joining']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['department', 'designation']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def years_of_service(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_joining.year

class EducationRecord(models.Model):
    """Employee Education Records"""
    
    DEGREE_LEVELS = [
        ('HIGH_SCHOOL', 'High School'),
        ('DIPLOMA', 'Diploma'),
        ('BACHELOR', 'Bachelor'),
        ('MASTER', 'Master'),
        ('PHD', 'PhD'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education_records')
    degree_level = models.CharField(max_length=20, choices=DEGREE_LEVELS)
    degree_title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'education_records'
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.degree_title}"

class WorkExperience(models.Model):
    """Previous Work Experience"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_experiences')
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    responsibilities = models.TextField()
    reason_for_leaving = models.TextField(blank=True)
    
    class Meta:
        db_table = 'work_experiences'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.company_name}"

class Dependent(models.Model):
    """Employee Dependents/Family Members"""
    
    RELATIONSHIP = [
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='dependents')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP)
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=15, blank=True)
    is_emergency_contact = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dependents'
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.name} ({self.relationship})"