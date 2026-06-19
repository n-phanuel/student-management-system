# Written Report: Student Management System
## MVC Web Application — University Assignment

---

## 1. System Overview

The **Student Management System (SMS)** is a web-based application designed to manage academic records for a university or college. The system enables administrators to create, view, update, and delete student profiles, academic departments, courses, and course enrollment records. Built using the **Django** web framework and a **SQLite** database, the application demonstrates a clean, maintainable separation of concerns through the Model–View–Controller (MVC) architectural pattern.

The system is accessible through a web browser and requires no additional software beyond Python and Django. It supports both unauthenticated guest users (read-only access) and authenticated administrators (full CRUD access), making it suitable for real-world institutional use with minimal configuration.

---

## 2. Objectives

The primary objectives of this project are:

- To design and implement a fully functional web application following the MVC architecture.
- To provide complete CRUD (Create, Read, Update, Delete) functionality for student, department, course, and enrollment records.
- To enforce server-side data validation to ensure data integrity.
- To implement user authentication so that administrative actions are protected.
- To produce a clean, modern user interface that is intuitive for non-technical users.
- To demonstrate best practices in web application development, including separation of concerns, DRY (Don't Repeat Yourself) principles, and the use of ORM for database abstraction.

---

## 3. MVC Architecture Description

The Model–View–Controller (MVC) pattern is a software design paradigm that divides an application into three interconnected components. Each component has a distinct responsibility, which makes the codebase easier to maintain, test, and extend.

**Model** — The Model represents the data and the business rules governing that data. It communicates directly with the database and is responsible for storing, retrieving, and validating data at the database level. The Model is independent of the user interface; it does not know how data will be displayed.

**View** — The View is responsible for presenting data to the user. It receives data from the Controller and renders it as HTML pages. The View contains no business logic; it only formats and displays what it is given. In Django, Views are implemented as HTML template files.

**Controller** — The Controller acts as the intermediary between the Model and the View. It receives incoming HTTP requests from the browser, applies any necessary business logic, retrieves or modifies data through the Model, and then passes the result to the appropriate View for rendering. In Django, the Controller role is fulfilled by view functions and URL routing configuration.

The flow of a typical request in this system is:
1. The user performs an action in the browser (e.g., submits a form).
2. The browser sends an HTTP request to the server.
3. Django's URL dispatcher (Controller) routes the request to the correct view function.
4. The view function (Controller) validates input, interacts with the Model, and selects a template.
5. The template (View) renders the HTML response, which is returned to the browser.

---

## 4. Implementation Details

### 4.1 Model Layer (`students/models.py`)

Four database models were defined using Django's Object-Relational Mapper (ORM):

**Department** — Stores academic departments with fields for name, code, and description. It serves as the parent entity for both students and courses.

**Course** — Represents individual courses offered by a department. Each course has a unique code, a credit value, and a foreign key relationship to the Department model.

**Student** — The primary entity of the system. It stores comprehensive personal and academic information, including student ID, name, date of birth, gender, contact details, department (foreign key), year of study, GPA, and enrollment status. Input validation is enforced using Django's built-in validators (e.g., GPA must be between 0.00 and 4.00).

**Enrollment** — A junction model that establishes a many-to-many relationship between Students and Courses, with additional fields for semester, academic year, and grade. A unique constraint prevents duplicate enrollments for the same student, course, semester, and year combination.

All models inherit from `django.db.models.Model` and include `__str__` methods for readable representations in the Django admin panel.

### 4.2 View Layer (`students/templates/students/`)

The View layer consists of thirteen HTML template files that form the user interface. All templates inherit from a shared `base.html` file using Django's template inheritance system, which eliminates duplication of the navigation sidebar, top bar, and footer.

The `base.html` template includes the Bootstrap 5 CSS framework for responsive layout, Bootstrap Icons for visual elements, and a custom stylesheet that defines the application's design language — including a dark sidebar navigation panel, stat cards for the dashboard, and colour-coded status badges.

Key pages include:
- **Dashboard (`home.html`)** — Displays summary statistics (total students, active students, departments, courses, average GPA) and a table of recently added students.
- **Student List (`student_list.html`)** — A searchable, filterable table of all student records with action buttons.
- **Student Profile (`student_detail.html`)** — Detailed view of a single student's personal and academic information, along with their enrollment history.
- **Forms (`student_form.html`, `department_form.html`, etc.)** — Reusable form pages for both creating and editing records.
- **Delete Confirmations** — Separate confirmation pages for each delete operation to prevent accidental data loss.
- **Login (`login.html`)** — A standalone, styled login page with a branded design.

### 4.3 Controller Layer (`students/views.py`, `students/urls.py`, `students/forms.py`)

The Controller layer is implemented across three files:

**`urls.py`** defines URL patterns that map browser requests to the correct view function. For example, a GET request to `/students/` is routed to `student_list`, while a GET to `/students/5/edit/` is routed to `student_edit` with `pk=5`.

**`views.py`** contains one function per action, handling all business logic. Each view function follows a consistent pattern: authenticate the user if required (via `@login_required`), process the request method (GET or POST), interact with the Model using Django's ORM, pass data to a template, and return an HTTP response. Flash messages (`django.contrib.messages`) provide user feedback after every operation.

**`forms.py`** defines Django ModelForms for each entity, specifying which fields to expose, how they render as HTML widgets, and custom validation logic (e.g., normalising email addresses to lowercase, forcing student IDs to uppercase). Server-side validation runs on every POST submission before any data reaches the database.

---

## 5. Database Schema

The database consists of four tables with the following relationships:

| Table       | Primary Key | Foreign Keys                   |
|-------------|-------------|-------------------------------|
| Department  | id (int)    | —                              |
| Course      | id (int)    | department_id → Department     |
| Student     | id (int)    | department_id → Department     |
| Enrollment  | id (int)    | student_id → Student, course_id → Course |

**Relationships:**
- Department → Course: **One-to-Many** (one department offers many courses)
- Department → Student: **One-to-Many** (one department has many students)
- Student ↔ Course via Enrollment: **Many-to-Many** (a student can enroll in many courses; a course can have many students)

---

## 6. Functional Requirements Fulfilled

| Requirement                    | Status |
|--------------------------------|--------|
| User input forms               | ✔ All entities have create/edit forms |
| Server-side validation         | ✔ Django ModelForms with custom validators |
| Display records in table format| ✔ All list pages use styled HTML tables |
| Update/edit functionality      | ✔ Edit views for students, departments, courses |
| Delete functionality           | ✔ Delete with confirmation for all entities |
| Authentication (login/logout)  | ✔ Django built-in auth, @login_required |
| Search / filter                | ✔ Student list supports name, ID, email, department, status filter |
| CSV export                     | ✔ One-click download of all student records |
| Bootstrap UI                   | ✔ Bootstrap 5 throughout |
| Responsive design              | ✔ Mobile-friendly sidebar toggle |

---

## 7. Screenshots Description

**Screenshot 1 — Dashboard:** Shows the main dashboard with five stat cards (Total Students, Active Students, Departments, Courses, Enrollments) and a table of recently added students. The dark sidebar is visible on the left with navigation links.

**Screenshot 2 — Student List:** Displays the full student table with search bar, department dropdown filter, and status filter at the top. Each row shows the student's avatar initials, name, email, student ID, department, year, GPA (colour-coded green/amber/red), status badge, and action buttons.

**Screenshot 3 — Student Profile:** Shows a single student's full profile split into two cards (Personal Information and Academic Information) with their course enrollment table below listing all enrolled courses with grades.

**Screenshot 4 — Add Student Form:** A multi-section form with labelled fields grouped into Identification, Personal Information, and Academic Details sections. Validation errors appear inline beneath each field.

**Screenshot 5 — Login Page:** A centred card on a dark gradient background with the system logo, username and password fields, and a "Browse as guest" link.

---

## 8. Conclusion

The Student Management System successfully demonstrates the MVC architectural pattern in a real-world web application. The separation between Model (data), View (templates), and Controller (views, forms, URLs) results in code that is clean, readable, and maintainable. Every CRUD operation works correctly, input validation protects data integrity, and the authentication system ensures that only authorised users can modify records. The application can be deployed locally in under five minutes with a single setup command.
