"""
students/forms.py  —  CONTROLLER LAYER (Validation) 
=========================================================
Changes in v2:
  - Added StudentRegistrationForm  (student self-registration)
  - Added StudentLoginForm         (custom login with role awareness)
  - All original forms unchanged
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Course, Department, Enrollment, StudentProfile


# ── Original forms ────────────────────────────────────────────────

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'email', 'phone',
            'address', 'department', 'year_of_study', 'gpa', 'status',
        ]
        widgets = {
            'student_id':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STU-2024-001'}),
            'first_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender':        forms.Select(attrs={'class': 'form-select'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':         forms.TextInput(attrs={'class': 'form-control'}),
            'address':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'department':    forms.Select(attrs={'class': 'form-select'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'gpa':           forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00', 'max': '4.00'}),
            'status':        forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_student_id(self):
        return self.cleaned_data['student_id'].upper()


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].upper()


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['department', 'name', 'code', 'credits', 'description']
        widgets = {
            'department':  forms.Select(attrs={'class': 'form-select'}),
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'credits':     forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'semester', 'year', 'grade']
        widgets = {
            'student':  forms.Select(attrs={'class': 'form-select'}),
            'course':   forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'year':     forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'grade':    forms.Select(attrs={'class': 'form-select'}),
        }


class StudentSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, or email…',
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Student.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


# ── Student Registration Form ─────────────────────────────────────────

class StudentRegistrationForm(forms.Form):
    """
    Allows a student to create a portal account by:
      1. Providing their registered Student ID (must already exist in DB)
      2. Choosing a username and password
    """
    # Step 1: link to existing academic record
    student_id = forms.CharField(
        max_length=20,
        label="Your Student ID",
        help_text="Enter the Student ID assigned to you by the institution (e.g. STU-2024-001)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. STU-2024-001',
            'autocomplete': 'off',
        })
    )

    # Step 2: choose login credentials
    username = forms.CharField(
        max_length=150,
        label="Choose a Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. john_doe',
            'autocomplete': 'off',
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters',
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password',
        })
    )

    def clean_student_id(self):
        sid = self.cleaned_data['student_id'].strip().upper()
        try:
            student = Student.objects.get(student_id=sid)
        except Student.DoesNotExist:
            raise forms.ValidationError(
                "No student record found with that ID. "
                "Please check your Student ID or contact administration."
            )
        # Check if account already created
        if student.has_portal_account:
            raise forms.ValidationError(
                "A portal account already exists for this Student ID. "
                "Please log in instead."
            )
        return sid

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "That username is already taken. Please choose another."
            )
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        return username

    def clean_password1(self):
        pw = self.cleaned_data.get('password1', '')
        if len(pw) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return pw

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned

    def save(self):
        """Create User + StudentProfile. Call only after is_valid()."""
        student = Student.objects.get(student_id=self.cleaned_data['student_id'])
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=student.email,
            first_name=student.first_name,
            last_name=student.last_name,
        )
        profile = StudentProfile.objects.create(
            user=user,
            student=student,
            is_student_user=True,
        )
        return user, profile


# ── Custom Login Form ─────────────────────────────────────────────────

class PortalLoginForm(AuthenticationForm):
    """Extends Django's AuthenticationForm with Bootstrap styling."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
