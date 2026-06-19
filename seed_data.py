"""
seed_data.py
============
Run this script ONCE after migrations to populate the database with
realistic sample data for demonstration purposes.

Usage:
    python manage.py shell < seed_data.py
  OR
    python seed_data.py   (if run from the project root with Django configured)
"""

import os
import sys
import django
from datetime import date

# ── Bootstrap Django ─────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from students.models import Department, Course, Student, Enrollment, StudentProfile

print("🌱  Seeding database …")

# ── 1. Superuser ─────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sms.edu', 'admin123')
    print("   ✔  Superuser created  (username: admin / password: admin123)")
else:
    print("   –  Superuser already exists, skipping.")

# ── 2. Departments ───────────────────────────────────────────────────────────
dept_data = [
    ('Computer Science',       'CS',  'Study of computation, algorithms, and software systems.'),
    ('Business Administration','BUS', 'Core business, management, and entrepreneurship studies.'),
    ('Electrical Engineering', 'EE',  'Circuits, electronics, signals, and power systems.'),
    ('Mathematics',            'MTH', 'Pure and applied mathematics.'),
    ('Information Technology', 'IT',  'Networking, systems administration, and IT management.'),
]

depts = {}
for name, code, desc in dept_data:
    d, created = Department.objects.get_or_create(
        code=code, defaults={'name': name, 'description': desc})
    depts[code] = d
    print(f"   {'✔' if created else '–'}  Department: {code}")

# ── 3. Courses ───────────────────────────────────────────────────────────────
course_data = [
    ('CS',  'Introduction to Programming',      'CS101', 3),
    ('CS',  'Data Structures & Algorithms',     'CS201', 3),
    ('CS',  'Database Systems',                 'CS301', 3),
    ('CS',  'Web Development',                  'CS310', 3),
    ('CS',  'Artificial Intelligence',          'CS401', 4),
    ('BUS', 'Principles of Management',         'BUS101', 3),
    ('BUS', 'Financial Accounting',             'BUS201', 3),
    ('BUS', 'Marketing Fundamentals',           'BUS210', 3),
    ('EE',  'Circuit Analysis',                 'EE101', 4),
    ('EE',  'Digital Electronics',              'EE201', 3),
    ('MTH', 'Calculus I',                       'MTH101', 4),
    ('MTH', 'Linear Algebra',                   'MTH201', 3),
    ('IT',  'Networking Fundamentals',          'IT101', 3),
    ('IT',  'Cybersecurity Essentials',         'IT301', 3),
]

courses = {}
for dept_code, name, code, credits in course_data:
    c, created = Course.objects.get_or_create(
        code=code,
        defaults={'department': depts[dept_code], 'name': name, 'credits': credits}
    )
    courses[code] = c
    print(f"   {'✔' if created else '–'}  Course: {code}")

# ── 4. Students ──────────────────────────────────────────────────────────────
student_data = [
    ('STU-2024-001', 'Amara',    'Ndjamba',   date(2002, 3, 14), 'F', 'amara.ndjamba@student.edu',    '+264 81 111 0001', 'CS',  1, 3.75, 'active'),
    ('STU-2024-002', 'Kofi',     'Mensah',    date(2001, 7, 22), 'M', 'kofi.mensah@student.edu',      '+264 81 111 0002', 'BUS', 2, 3.40, 'active'),
    ('STU-2024-003', 'Lindiwe',  'Dube',      date(2000, 11, 5), 'F', 'lindiwe.dube@student.edu',     '+264 81 111 0003', 'EE',  3, 2.90, 'active'),
    ('STU-2023-004', 'Ethan',    'Schultz',   date(1999, 4, 30), 'M', 'ethan.schultz@student.edu',    '+264 81 111 0004', 'MTH', 4, 3.60, 'active'),
    ('STU-2023-005', 'Priya',    'Nair',      date(2001, 9, 17), 'F', 'priya.nair@student.edu',       '+264 81 111 0005', 'IT',  2, 3.10, 'active'),
    ('STU-2022-006', 'Thomas',   'Nakale',    date(2000, 1, 8),  'M', 'thomas.nakale@student.edu',    '+264 81 111 0006', 'CS',  3, 2.40, 'active'),
    ('STU-2022-007', 'Fatima',   'Al-Rashid', date(2001, 6, 25), 'F', 'fatima.rashid@student.edu',    '+264 81 111 0007', 'BUS', 3, 3.85, 'graduated'),
    ('STU-2024-008', 'James',    'Okoye',     date(2003, 2, 12), 'M', 'james.okoye@student.edu',      '+264 81 111 0008', 'CS',  1, 2.80, 'active'),
    ('STU-2023-009', 'Sara',     'Petersen',  date(2001, 8, 19), 'F', 'sara.petersen@student.edu',    '+264 81 111 0009', 'EE',  2, 3.20, 'active'),
    ('STU-2023-010', 'Marcus',   'Hamutenya', date(2000, 5, 3),  'M', 'marcus.hamutenya@student.edu', '+264 81 111 0010', 'IT',  3, 1.80, 'suspended'),
]

students = {}
for sid, fn, ln, dob, gender, email, phone, dept_code, year, gpa, status in student_data:
    s, created = Student.objects.get_or_create(
        student_id=sid,
        defaults={
            'first_name': fn, 'last_name': ln, 'date_of_birth': dob,
            'gender': gender, 'email': email, 'phone': phone,
            'department': depts[dept_code], 'year_of_study': year,
            'gpa': gpa, 'status': status,
        }
    )
    students[sid] = s
    print(f"   {'✔' if created else '–'}  Student: {sid} — {fn} {ln}")

# ── 5. Enrollments ───────────────────────────────────────────────────────────
enrollment_data = [
    ('STU-2024-001', 'CS101', 'S1', 2024, 'A'),
    ('STU-2024-001', 'MTH101','S1', 2024, 'A-'),
    ('STU-2024-001', 'CS201', 'S2', 2024, ''),
    ('STU-2024-002', 'BUS101','S1', 2024, 'B+'),
    ('STU-2024-002', 'BUS201','S2', 2024, 'B'),
    ('STU-2023-004', 'MTH101','S1', 2023, 'A+'),
    ('STU-2023-004', 'MTH201','S2', 2023, 'A'),
    ('STU-2023-004', 'CS201', 'S1', 2024, 'B+'),
    ('STU-2023-005', 'IT101', 'S1', 2023, 'B'),
    ('STU-2023-005', 'IT301', 'S2', 2024, ''),
    ('STU-2022-006', 'CS101', 'S1', 2022, 'C'),
    ('STU-2022-006', 'CS201', 'S2', 2022, 'C+'),
    ('STU-2022-006', 'CS301', 'S1', 2023, 'B-'),
    ('STU-2024-008', 'CS101', 'S1', 2024, 'B'),
    ('STU-2023-009', 'EE101', 'S1', 2023, 'A-'),
    ('STU-2023-009', 'EE201', 'S2', 2023, 'B+'),
]

for sid, ccode, sem, year, grade in enrollment_data:
    e, created = Enrollment.objects.get_or_create(
        student=students[sid],
        course=courses[ccode],
        semester=sem,
        year=year,
        defaults={'grade': grade}
    )
    print(f"   {'✔' if created else '–'}  Enrollment: {sid} → {ccode}")

# ── 6. Demo Student Portal Account ───────────────────────────────────────────
# Creates a portal login for Amara Ndjamba (STU-2024-001) so you can demo
# the student portal immediately without registering.
demo_student = students['STU-2024-001']
if not demo_student.has_portal_account:
    demo_user = User.objects.create_user(
        username='amara',
        password='student123',
        email=demo_student.email,
        first_name=demo_student.first_name,
        last_name=demo_student.last_name,
    )
    StudentProfile.objects.create(user=demo_user, student=demo_student, is_student_user=True)
    print("   ✔  Demo student portal account created (username: amara / password: student123)")
else:
    print("   –  Demo student portal account already exists.")

print("\n Seed complete!")
print("   Landing page:  http://127.0.0.1:8000/")
print("   Run server:    python manage.py runserver")
