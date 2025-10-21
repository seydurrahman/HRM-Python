from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation
from .models import User

class LoginForm(forms.Form):
    """User Login Form"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True,
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        })
    )
    remember_me = forms.BooleanField(
        label='Remember me',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class RegisterForm(forms.ModelForm):
    """User Registration Form"""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ChangePasswordForm(PasswordChangeForm):
    """Change Password Form"""
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        help_text=password_validation.password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """Profile Update Form"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }



# from django import forms
# from django.contrib.auth.forms import PasswordChangeForm
# from django.contrib.auth import password_validation
# from .models import User

# class LoginForm(forms.Form):
#     """Login Form"""
#     email = forms.EmailField(
#         label='Email Address',
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter your email',
#             'required': True,
#             'autofocus': True
#         })
#     )
#     password = forms.CharField(
#         label='Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter your password',
#             'required': True
#         })
#     )
#     remember_me = forms.BooleanField(
#         label='Remember me',
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         })
#     )

# class RegisterForm(forms.ModelForm):
#     """Registration Form"""
#     password = forms.CharField(
#         label='Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter password',
#             'required': True
#         }),
#         min_length=8,
#         help_text='Password must be at least 8 characters long'
#     )
#     password_confirm = forms.CharField(
#         label='Confirm Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Confirm password',
#             'required': True
#         })
#     )
    
#     class Meta:
#         model = User
#         fields = ['email', 'first_name', 'last_name', 'phone']
#         widgets = {
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter your email',
#                 'required': True
#             }),
#             'first_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'First Name',
#                 'required': True
#             }),
#             'last_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Last Name',
#                 'required': True
#             }),
#             'phone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Phone Number (optional)'
#             }),
#         }
#         labels = {
#             'email': 'Email Address',
#             'first_name': 'First Name',
#             'last_name': 'Last Name',
#             'phone': 'Phone Number'
#         }
    
#     def clean_email(self):
#         """Validate email uniqueness"""
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError('This email is already registered.')
#         return email
    
#     def clean(self):
#         """Validate password confirmation"""
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         password_confirm = cleaned_data.get('password_confirm')
        
#         if password and password_confirm:
#             if password != password_confirm:
#                 raise forms.ValidationError("Passwords don't match")
        
#         return cleaned_data

# class ChangePasswordForm(PasswordChangeForm):
#     """Change Password Form"""
#     old_password = forms.CharField(
#         label='Current Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Current Password',
#             'required': True
#         })
#     )
#     new_password1 = forms.CharField(
#         label='New Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'New Password',
#             'required': True
#         }),
#         help_text=password_validation.password_validators_help_text_html()
#     )
#     new_password2 = forms.CharField(
#         label='Confirm New Password',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Confirm New Password',
#             'required': True
#         })
#     )

# class ProfileUpdateForm(forms.ModelForm):
#     """Profile Update Form"""
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'phone']
#         widgets = {
#             'first_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'First Name'
#             }),
#             'last_name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Last Name'
#             }),
#             'phone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Phone Number'
#             }),
#         }