"""
students/models.py  —  MODEL LAYER  (v2 — with StudentProfile)
===============================================================
Changes in v2:
  - Added StudentProfile: links a Django User account to a Student
    record, enabling the student self-service portal.
  - All existing models are unchanged for backward compatibility.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code, e.g. CS, BUS")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} — {self.name}"


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=15, unique=True)
    credits = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code}: {self.name}"


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [
        ('active', 'Active'), ('inactive', 'Inactive'),
        ('graduated', 'Graduated'), ('suspended', 'Suspended'),
    ]

    student_id = models.CharField(
        max_length=20, unique=True,
        validators=[RegexValidator(r'^[A-Z0-9\-]+$',
                                   'Use uppercase letters, digits, and hyphens only.')],
        help_text="e.g. STU-2024-001")
    first_name    = models.CharField(max_length=50)
    last_name     = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email         = models.EmailField(unique=True)
    phone         = models.CharField(max_length=20, blank=True)
    address       = models.TextField(blank=True)
    department    = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name='students')
    year_of_study = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(6)])
    gpa = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(4.00)])
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.student_id} — {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def has_portal_account(self):
        return hasattr(self, 'portal_account')


# ─── NEW in v2 ───────────────────────────────────────────────────────────────
class StudentProfile(models.Model):
    """
    Links a Django User account to a Student academic record.
    One-to-one with User; one-to-one with Student.
    is_student_user=True  → Student portal (read-only, own data only)
    is_student_user=False → reserved for future role expansion
    """
    user    = models.OneToOneField(User, on_delete=models.CASCADE,
                                   related_name='student_profile')
    student = models.OneToOneField(Student, on_delete=models.CASCADE,
                                   related_name='portal_account')
    is_student_user = models.BooleanField(default=True)
    profile_bio     = models.TextField(blank=True, default='')
    joined_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Student Portal Account'
        verbose_name_plural = 'Student Portal Accounts'

    def __str__(self):
        return f"{self.user.username} → {self.student.student_id}"


# ─────────────────────────────────────────────────────────────────────────────
class Enrollment(models.Model):
    SEMESTER_CHOICES = [('S1', 'Semester 1'), ('S2', 'Semester 2'), ('S3', 'Summer')]
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D', 'D'), ('F', 'F'), ('', 'Not graded yet'),
    ]

    student  = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course   = models.ForeignKey(Course,  on_delete=models.CASCADE, related_name='enrollments')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default='S1')
    year     = models.PositiveSmallIntegerField(default=2024)
    grade    = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, default='')
    enrolled_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'semester', 'year')
        ordering = ['-year', 'semester']

    def __str__(self):
        return f"{self.student.student_id} → {self.course.code} ({self.semester} {self.year})"
