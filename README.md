# Student Database System

A modern, professional, and responsive web-based Student Management System built with Flask, SQLite, and Bootstrap. This system allows students to manage their profiles, view attendance and marks, and enables admins to manage student records, attendance, and export reports.

---

## 🚀 Features

- **Student Registration & Login** (with strong password policy)
- **Single Active Session:** Only one session per user is allowed; logging in elsewhere logs out previous sessions.
- **IST Timezone:** All timestamps (login, attendance, messages, etc.) are stored and displayed in IST.
- **Attendance Management:**
  - Students submit attendance requests (one per day).
  - Admin must approve attendance requests for them to count.
  - Students see "Approval Pending" until admin approval.
- **Marks Management:** Admin can update marks for all subjects.
- **Exam Fee Payment:** Online payment with receipt and status.
- **Admit Card & Profile PDF:** Export and download as PDF (admin and student).
- **Admin Dashboard:**
  - View all students, attendance, marks, last login time & IP.
  - Export/import data (students, attendance, admit cards, profiles).
  - Analytics with Chart.js (attendance, marks).
  - Bulk messaging to students.
  - Attendance requests approval.
- **Student Dashboard:** View profile, attendance, marks, admit card, exam fee, and contact admin.
- **Contact Admin:** Messaging system with admin replies.
- **Mobile-Optimized:** Dedicated mobile admin dashboard and responsive UI.
- **Security:**
  - CSRF protection on all forms.
  - Rate limiting on login.
  - Secure session cookies.
  - Audit logging for admin actions.
- **Professional Polish:**
  - Modern Bootstrap 5 UI, dark mode support.
  - Custom error pages (404, etc.).
  - Favicon, meta tags, About/Help pages.


---

## 📁 Project Structure

```
student-database-system/
│
├── app.py
├── students.db
├── requirements.txt
├── README.md
├── version.txt
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
    ├── admin_dashboard_mobile.html
    ├── admin_update_marks.html
    ├── admin_update_attendance.html
    ├── admin_attendance_requests.html
    ├── edit_profile.html
    ├── student_details.html
    ├── attendance.html
    ├── view_marks.html
    ├── login.html
    ├── register.html
    ├── change_password.html
    ├── reset_password.html
    ├── reset_password_request.html
    ├── pay_exam_fees.html
    ├── contact_admin.html
    ├── admin_messages.html
    ├── exam_settings.html
    └── 404.html
```

---

## 🛠️ Setup Instructions

1. **Clone the repository**
    ```sh
    git clone https://github.com/prattyan/student-database-system.git
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
    pip install flask werkzeug pandas authlib fpdf
    ```

4. **Run the application**
    ```sh
    python app.py
    ```

5. **Access the app**
    - Open your browser and go to [http://localhost:5000/](http://localhost:5000/)

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
- Dedicated mobile admin dashboard.

---

## 🔒 Security

- CSRF protection on all forms.
- Rate limiting on login.
- Secure session cookies.
- Only one active session per user.
- Audit logging for admin actions.

---

## 📊 Analytics

- Admin dashboard includes attendance and marks analytics with Chart.js.
- Attendance approval workflow with pending requests.

---

## 📝 License

This project is licensed under Prattyan Ghosh.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📧 Contact

For any queries, please contact [prattyanghosh@gmail.com](mailto:prattyanghosh@gmail.com).

---

**Enjoy using the Student Database System!**
