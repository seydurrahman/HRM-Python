from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('HR', 'HR Manager'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    ]
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_hr(self):
        return self.role in ['ADMIN', 'HR']
    
    @property
    def is_manager(self):
        return self.role in ['ADMIN', 'HR', 'MANAGER']

class Department(models.Model):
    """Department Model"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_department'
    )
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
class Section(models.Model):
    """Section Model within Departments"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_sections'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sections'
        unique_together = ['name', 'department']
        ordering = ['department__name', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.department.name})"

class Designation(models.Model):
    """Designation/Job Title Model"""
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='designations'
    )
    level = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'designations'
        ordering = ['level', 'title']
        unique_together = ['title', 'department']
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CompanyUnit(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='company_units')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.group} - {self.name}"


class Division(models.Model):
    company_unit = models.ForeignKey(CompanyUnit, on_delete=models.CASCADE, related_name='divisions')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.company_unit} - {self.name}"


class DepartmentDept(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='departments_dept')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.division} - {self.name}"


class SectiotSec(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sections_sec')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.department} - {self.name}"


class SubSection(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='subsections')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.section} - {self.name}"


class Floor(models.Model):
    subsection = models.ForeignKey(SubSection, on_delete=models.CASCADE, related_name='floors')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subsection} - {self.name}"


class Line(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='lines')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.floor} - {self.name}"
