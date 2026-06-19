"""
students/urls.py  —  CONTROLLER LAYER (Routing)  v2
====================================================
New routes in v2:
  ''           → landing page (pre-login screen)
  auth/login/  → custom role-aware login
  auth/logout/ → fixed logout
  auth/register/ → student self-registration
  portal/      → student personal dashboard
  portal/profile/ → student read-only profile
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Landing / Auth ────────────────────────────────────────
    path('',                views.landing,          name='landing'),
    path('auth/login/',     views.custom_login,     name='login'),
    path('auth/logout/',    views.custom_logout,    name='logout'),
    path('auth/register/',  views.student_register, name='student_register'),

    # ── Admin Dashboard ───────────────────────────────────────
    path('dashboard/',               views.home,                  name='home'),
    path('dashboard/change-password/', views.admin_change_password, name='admin_change_password'),

    # ── Student Portal ────────────────────────────────────────
    path('portal/',         views.student_portal,       name='student_portal'),
    path('portal/profile/', views.student_profile_view, name='student_profile_view'),

    # ── Students (admin CRUD) ─────────────────────────────────
    path('students/',                   views.student_list,        name='student_list'),
    path('students/new/',               views.student_create,      name='student_create'),
    path('students/<int:pk>/',          views.student_detail,      name='student_detail'),
    path('students/<int:pk>/edit/',     views.student_edit,        name='student_edit'),
    path('students/<int:pk>/delete/',   views.student_delete,      name='student_delete'),
    path('students/export/csv/',        views.export_students_csv, name='export_students_csv'),

    # ── Departments ───────────────────────────────────────────
    path('departments/',                        views.department_list,   name='department_list'),
    path('departments/new/',                    views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/',          views.department_edit,   name='department_edit'),
    path('departments/<int:pk>/delete/',        views.department_delete, name='department_delete'),

    # ── Courses ───────────────────────────────────────────────
    path('courses/',                    views.course_list,   name='course_list'),
    path('courses/new/',                views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/',      views.course_edit,   name='course_edit'),
    path('courses/<int:pk>/delete/',    views.course_delete, name='course_delete'),

    # ── Enrollments ───────────────────────────────────────────
    path('enrollments/new/',                views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/delete/',    views.enrollment_delete, name='enrollment_delete'),
]
