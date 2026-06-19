"""
students/admin.py
-----------------
Registers models with Django admin for convenient data management.
"""
from django.contrib import admin
from .models import Student, Department, Course, Enrollment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'credits']
    list_filter = ['department']
    search_fields = ['code', 'name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'department', 'year_of_study', 'gpa', 'status']
    list_filter = ['department', 'status', 'year_of_study']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'year', 'grade']
    list_filter = ['semester', 'year', 'grade']
