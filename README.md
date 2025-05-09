# Student Database System

A web-based Student Management System built with Flask, SQLite, and Bootstrap. This application allows students to register, log in, manage their profiles, view attendance and marks, and allows admins to manage student records and export data.

## Features

- Student registration and login
- Profile management with profile picture upload
- View attendance and marks with CGPA calculation
- Password reset and change functionality
- Admin dashboard to view, update, and delete students
- Export student and attendance data to Excel
- Responsive UI with Bootstrap

## Project Structure

```
app.py
Procfile
README.md
students.db
style.css
instance/
static/
    exports/
        students.xlsx
    js/
        script.js
    uploads/
        default.png
        ...
templates/
    admin_dashboard.html
    admin_update_attendance.html
    admin_update_marks.html
    attendance.html
    base.html
    change_password.html
    dashboard.html
    edit_profile.html
    login.html
    register.html
    reset_password_request.html
    reset_password.html
    student_details.html
    view_marks.html
```

## Setup Instructions

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/student-database-system.git
    cd student-database-system
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

    If `requirements.txt` does not exist, install manually:
    ```sh
    pip install flask werkzeug pandas authlib pymongo
    ```

4. **Run the application:**
    ```sh
    python app.py
    ```

5. **Access the app:**
    Open your browser and go to [http://localhost:5000](http://localhost:5000)

## Admin Access

- The default admin email is `admin@example.com`. You may need to manually add this user to the database.

## Deployment

- To deploy on platforms like Heroku, use the provided `Procfile`.

## License

This project is licensed under the MIT License.

---

**Note:** Make sure to create the `students.db` SQLite database and required tables before running the app. The app will attempt to create some tables automatically, but you may need to add the `students` and `attendance` tables if not present.
