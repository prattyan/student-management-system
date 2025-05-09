# Student Database System

A modern, professional, and responsive web-based Student Management System built with Flask, SQLite, and Bootstrap. This system allows students to manage their profiles, view attendance and marks, and enables admins to manage student records, attendance, and export reports.

---

## 🚀 Features

- **Student Registration & Login**
- **Profile Management** (with profile picture upload)
- **View Attendance & Marks** (with CGPA calculation)
- **Password Reset & Change**
- **Admin Dashboard** with analytics and student management
- **Export Students & Attendance** to Excel
- **Responsive UI** with Bootstrap 5
- **Profile pictures** shown in sidebar and navbar
- **Modern, professional UI/UX**

---

## 📁 Project Structure

```
student-database-system/
│
├── app.py
├── students.db
├── requirements.txt
├── README.md
├── static/
│   ├── style.css
│   ├── js/
│   │   └── script.js
│   ├── uploads/
│   │   └── default.png
│   └── exports/
│       ├── students.xlsx
│       └── attendance.xlsx
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── admin_dashboard.html
    ├── admin_update_marks.html
    ├── admin_update_attendance.html
    ├── edit_profile.html
    ├── student_details.html
    ├── attendance.html
    ├── view_marks.html
    ├── login.html
    ├── register.html
    ├── change_password.html
    ├── reset_password.html
    └── reset_password_request.html
```

---

## 🛠️ Setup Instructions

1. **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/student-database-system.git
    cd student-database-system
    ```

2. **Create a virtual environment and activate it**
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On Linux/Mac
    ```

3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```
    If `requirements.txt` is missing, install manually:
    ```sh
    pip install flask werkzeug pandas authlib pymongo
    ```

4. **Run the application**
    ```sh
    python app.py
    ```

5. **Access the app**
    - Open your browser and go to [http://localhost:5000](http://localhost:5000)

---

## 👤 Admin Access

- The default admin is identified by the email `admin@example.com`.
- To log in as admin, register with this email or update the database accordingly.

---

## 📦 Exporting Data

- Admins can export student and attendance data to Excel from the sidebar in the admin dashboard.
- Files are saved in `static/exports/`.

---

## 🖼️ Profile Pictures

- Students can upload a profile picture from their profile page.
- Profile pictures are displayed in the sidebar and navbar for a personalized experience.

---

## 🖥️ UI/UX

- Built with [Bootstrap 5](https://getbootstrap.com/) for a modern, responsive design.
- Sidebar navigation for both admin and students.
- Profile picture and name shown in sidebar and navbar.
- All forms use floating labels and validation.

---

## 📝 License

This project is licensed under Prattyan Ghosh.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📧 Contact

For any queries, please contact [your-email@example.com](mailto:prattyanghosh@gmail.com).

---

**Enjoy using the Student Database System!**
