"""
students/views.py  —  CONTROLLER LAYER  
=============================================
Changes:
  - landing()          → pre-login landing/loadout screen
  - custom_login()     → role-aware login (admin → admin dash, student → portal)
  - custom_logout()    → fixed logout with flash message
  - student_register() → student self-registration
  - student_portal()   → student's personal dashboard (read-only)
  - student_profile_view() → student profile page
  - All original admin views kept, now protected by @admin_required
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
import csv

from .models import Student, Department, Course, Enrollment, StudentProfile
from .forms import (
    StudentForm, DepartmentForm, CourseForm,
    EnrollmentForm, StudentSearchForm,
    StudentRegistrationForm, PortalLoginForm,
)
from .access import admin_required, student_required, is_admin, is_student_user


# ══════════════════════════════════════════════════════════════
#  LANDING PAGE 
# ══════════════════════════════════════════════════════════════
def landing(request):
    """
    Pre-login entry screen — shown before login and after logout.
    If user is already authenticated, redirect to the correct dashboard.
    """
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('home')
        if is_student_user(request.user):
            return redirect('student_portal')
    return render(request, 'students/landing.html')


# ══════════════════════════════════════════════════════════════
#  CUSTOM LOGIN (role-aware)
# ══════════════════════════════════════════════════════════════
def custom_login(request):
    """
    Handles login for both admins and student portal users.
    After authentication, redirects based on the user's role:
      - Admin/staff → admin dashboard (/)
      - Student     → student portal (/portal/)
    """
    # Already logged in? Send to right place.
    if request.user.is_authenticated:
        return redirect('home' if is_admin(request.user) else 'student_portal')

    form = PortalLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if is_admin(user):
                messages.success(request, f'Welcome back, {user.username}! You are logged in as Admin.')
                return redirect('home')
            elif is_student_user(user):
                name = user.student_profile.student.first_name
                messages.success(request, f'Welcome back, {name}! You are logged in to the Student Portal.')
                return redirect('student_portal')
            else:
                # Authenticated but no recognised role — fail safe
                logout(request)
                messages.error(request, 'Your account is not configured correctly. Contact admin.')
                return redirect('landing')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'students/login.html', {'form': form})


# ══════════════════════════════════════════════════════════════
#  FIXED LOGOUT
# ══════════════════════════════════════════════════════════════
def custom_logout(request):
    """
    Fixed logout view.
    - Accepts GET and POST (Django 5 requires POST; we support both for simplicity).
    - Properly destroys the session via Django's logout().
    - Adds a success flash message.
    - Redirects to the landing page (not login).
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)   # ← this flushes the session and clears auth cookie
        messages.success(request, f'You have been logged out successfully. Goodbye, {username}!')
    return redirect('landing')


# ══════════════════════════════════════════════════════════════
#  STUDENT SELF-REGISTRATION
# ══════════════════════════════════════════════════════════════
def student_register(request):
    """
    Allows students to create their own portal account by linking
    their existing Student ID to a new username + password.
    """
    # Already logged in? Go to appropriate dashboard.
    if request.user.is_authenticated:
        return redirect('home' if is_admin(request.user) else 'student_portal')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user, profile = form.save()
            login(request, user)
            messages.success(
                request,
                f'Account created successfully! Welcome, {profile.student.first_name}. '
                f'You are now logged in to the Student Portal.'
            )
            return redirect('student_portal')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})


# ══════════════════════════════════════════════════════════════
#  STUDENT PORTAL — DASHBOARD
# ══════════════════════════════════════════════════════════════
@student_required
def student_portal(request):
    """
    Personal dashboard for a logged-in student.
    Shows ONLY their own data — enforced by filtering on their student record.
    """
    profile    = request.user.student_profile
    student    = profile.student
    enrollments = student.enrollments.select_related('course__department').all()

    # Grade distribution summary
    graded = [e for e in enrollments if e.grade]
    grade_map = {}
    for e in graded:
        grade_map[e.grade] = grade_map.get(e.grade, 0) + 1

    # Count passed / failed
    passed  = sum(1 for e in graded if e.grade not in ('F', ''))
    failed  = sum(1 for e in graded if e.grade == 'F')
    pending = sum(1 for e in enrollments if not e.grade)

    context = {
        'student':     student,
        'enrollments': enrollments,
        'passed':      passed,
        'failed':      failed,
        'pending':     pending,
        'total_credits': sum(e.course.credits for e in enrollments),
    }
    return render(request, 'students/student_portal.html', context)


# ══════════════════════════════════════════════════════════════
#  STUDENT PORTAL — PROFILE PAGE
# ══════════════════════════════════════════════════════════════
@student_required
def student_profile_view(request):
    """
    Student's own read-only profile page.
    They can view all personal and academic details but cannot edit them.
    """
    profile = request.user.student_profile
    student = profile.student
    return render(request, 'students/student_profile.html', {
        'student': student,
        'profile': profile,
    })


# ══════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD 
# ══════════════════════════════════════════════════════════════
def home(request):
    """
    Admin dashboard — now requires login.
    Student portal users are redirected to their own portal.
    """
    if not request.user.is_authenticated:
        from django.contrib import messages as msg
        msg.warning(request, 'Please log in to access the system.')
        return redirect('landing')
    # Student portal users who navigate here get sent to their dashboard
    if is_student_user(request.user):
        return redirect('student_portal')
    context = {
        'total_students':    Student.objects.count(),
        'active_students':   Student.objects.filter(status='active').count(),
        'total_departments': Department.objects.count(),
        'total_courses':     Course.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'recent_students':   Student.objects.select_related('department').order_by('-enrolled_at')[:5],
        'avg_gpa':           Student.objects.aggregate(avg=Avg('gpa'))['avg'] or 0,
    }
    return render(request, 'students/home.html', context)


# ══════════════════════════════════════════════════════════════
#  STUDENT CRUD  (admin only for write operations)
# ══════════════════════════════════════════════════════════════
@admin_required
def student_list(request):
    form     = StudentSearchForm(request.GET)
    students = Student.objects.select_related('department').all()

    if form.is_valid():
        query  = form.cleaned_data.get('query')
        dept   = form.cleaned_data.get('department')
        status = form.cleaned_data.get('status')
        if query:
            students = students.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) |
                Q(student_id__icontains=query) | Q(email__icontains=query)
            )
        if dept:
            students = students.filter(department=dept)
        if status:
            students = students.filter(status=status)

    return render(request, 'students/student_list.html', {
        'students': students, 'search_form': form})


@admin_required
def student_detail(request, pk):
    student     = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('course__department').all()
    return render(request, 'students/student_detail.html', {
        'student': student, 'enrollments': enrollments})


@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} created successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {
        'form': form, 'title': 'Add New Student', 'button': 'Create Student'})


@admin_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {
        'form': form, 'student': student,
        'title': f'Edit — {student.full_name}', 'button': 'Save Changes'})


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'Student "{name}" was deleted.')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


# ══════════════════════════════════════════════════════════════
#  DEPARTMENT CRUD
# ══════════════════════════════════════════════════════════════
@admin_required
def department_list(request):
    departments = Department.objects.annotate(
        student_count=Count('students'), course_count=Count('courses'))
    return render(request, 'students/department_list.html', {'departments': departments})


@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" created.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'students/department_form.html', {
        'form': form, 'title': 'Add Department', 'button': 'Create'})


@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{dept.name}" updated.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'students/department_form.html', {
        'form': form, 'title': f'Edit — {dept.name}', 'button': 'Save'})


@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted.')
        return redirect('department_list')
    return render(request, 'students/department_confirm_delete.html', {'dept': dept})


# ══════════════════════════════════════════════════════════════
#  COURSE CRUD
# ══════════════════════════════════════════════════════════════
@admin_required
def course_list(request):
    courses = Course.objects.select_related('department').annotate(
        enrollment_count=Count('enrollments'))
    return render(request, 'students/course_list.html', {'courses': courses})


@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.name}" created.')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'students/course_form.html', {
        'form': form, 'title': 'Add Course', 'button': 'Create'})


@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.name}" updated.')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'students/course_form.html', {
        'form': form, 'title': f'Edit — {course.name}', 'button': 'Save'})


@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')
    return render(request, 'students/course_confirm_delete.html', {'course': course})


# ══════════════════════════════════════════════════════════════
#  ENROLLMENT
# ══════════════════════════════════════════════════════════════
@admin_required
def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, 'Enrollment recorded.')
            return redirect('student_detail', pk=enrollment.student.pk)
    else:
        initial = {}
        student_id = request.GET.get('student')
        if student_id:
            initial['student'] = student_id
        form = EnrollmentForm(initial=initial)
    return render(request, 'students/enrollment_form.html', {
        'form': form, 'title': 'Enroll Student in Course'})


@admin_required
def enrollment_delete(request, pk):
    enrollment  = get_object_or_404(Enrollment, pk=pk)
    student_pk  = enrollment.student.pk
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment removed.')
        return redirect('student_detail', pk=student_pk)
    return render(request, 'students/enrollment_confirm_delete.html', {'enrollment': enrollment})


# ══════════════════════════════════════════════════════════════
#  CSV EXPORT
# ══════════════════════════════════════════════════════════════
@admin_required
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email',
                     'Department', 'Year', 'GPA', 'Status', 'Enrolled'])
    for s in Student.objects.select_related('department').all():
        writer.writerow([
            s.student_id, s.first_name, s.last_name, s.email,
            s.department.name if s.department else '',
            s.year_of_study, s.gpa, s.status, s.enrolled_at,
        ])
    return response


# ══════════════════════════════════════════════════════════════
#  ADMIN CHANGE PASSWORD
# ══════════════════════════════════════════════════════════════
@admin_required
def admin_change_password(request):
    """
    Allows a logged-in admin to change their own password.
    Uses Django's built-in PasswordChangeForm for safe validation,
    then calls update_session_auth_hash() so the admin stays logged
    in after the password changes (no forced re-login).
    """
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the session alive — without this the admin is logged out
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Your password was changed successfully. You are still logged in.'
            )
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    # Apply Bootstrap classes to the form fields rendered by Django
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'students/admin_change_password.html', {'form': form})
