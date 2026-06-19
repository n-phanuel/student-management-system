"""
sms_project/urls.py 
===========================
Root URL dispatcher.

CHANGE:
  - Removed Django's built-in LoginView / LogoutView (they conflicted with
    our custom role-aware login/logout in students/views.py).
  - All routing is now fully handled by students/urls.py.
  - Django admin kept for superuser convenience.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel (superuser only)
    path('admin/', admin.site.urls),

    # Every other URL → handled by the students app (MVC controller layer)
    path('', include('students.urls')),
]
