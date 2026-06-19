"""
students/access.py  —  Role-Based Access Control Helpers
=========================================================
Custom decorators and helper functions that enforce the two-role
system: Admin (staff) vs Student portal user.

Usage
-----
  @admin_required          — only Django staff/superusers
  @student_required        — only linked student portal users
  @login_required          — any authenticated user (Django built-in)

Helper
------
  is_admin(user)           → bool
  is_student_user(user)    → bool
  get_student_profile(user)→ StudentProfile | None
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# ── Role detection helpers ────────────────────────────────────────────────────

def is_admin(user):
    """Return True if the user is a Django staff or superuser (admin role)."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_student_user(user):
    """Return True if the user has a linked StudentProfile (student role)."""
    return (
        user.is_authenticated
        and hasattr(user, 'student_profile')
        and user.student_profile.is_student_user
    )


def get_student_profile(user):
    """Return the StudentProfile for a student portal user, or None."""
    if is_student_user(user):
        return user.student_profile
    return None


# ── Decorators ───────────────────────────────────────────────────────────────

def admin_required(view_func):
    """
    Decorator: only Django staff / superusers may access this view.
    - Unauthenticated → redirect to landing page.
    - Authenticated non-admin (e.g. student) → redirect to their dashboard.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access that page.')
            return redirect('landing')
        if not is_admin(request.user):
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('student_portal')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """
    Decorator: only student portal users may access this view.
    - Unauthenticated → redirect to landing page.
    - Authenticated admin → redirect to admin dashboard.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access the student portal.')
            return redirect('landing')
        if not is_student_user(request.user):
            # Admin trying to access student portal — send them to admin dashboard
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
