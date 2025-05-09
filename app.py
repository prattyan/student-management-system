from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient
from io import BytesIO
from flask import send_file

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

DATABASE = 'students.db'
# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    with get_db_connection() as conn:
        # Create students table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT,
                roll_number TEXT,
                department TEXT,
                profile_pic TEXT DEFAULT 'default.png',
                math_marks INTEGER DEFAULT 0,
                science_marks INTEGER DEFAULT 0,
                history_marks INTEGER DEFAULT 0,
                english_marks INTEGER DEFAULT 0
            )
        ''')
        # Create attendance table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER DEFAULT 1,
                total_classes INTEGER DEFAULT 0,
                attended_classes INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        conn.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'student_id' not in session:
        flash('Please log in to upload a profile picture.', 'danger')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file and allowed_file(file.filename):
        # Rename the file to the student's ID
        student_id = session['student_id']
        file_extension = file.filename.rsplit('.', 1)[1].lower()  # Get the file extension
        filename = f"{student_id}.{file_extension}"  # Rename file to student ID with extension
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Debugging: Print values
        print(f"Student ID: {student_id}")
        print(f"File Extension: {file_extension}")
        print(f"Filename: {filename}")
        print(f"File Path: {file_path}")

        # Save the file
        file.save(file_path)

        # Update the student's profile picture in the database
        conn = get_db_connection()
        conn.execute('''
            UPDATE students
            SET profile_pic = ?
            WHERE id = ?
        ''', (filename, student_id))
        conn.commit()
        conn.close()

        flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid file type. Please upload a valid image.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/update_marks/<int:id>', methods=['GET', 'POST'])
def update_marks(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        math_marks = request.form['math_marks']
        science_marks = request.form['science_marks']
        history_marks = request.form['history_marks']
        english_marks = request.form['english_marks']
        conn.execute('''
            UPDATE students
            SET math_marks = ?, science_marks = ?, history_marks = ?, english_marks = ?
            WHERE id = ?
        ''', (math_marks, science_marks, history_marks,english_marks, id))
        conn.commit()
        conn.close()
        flash('Marks updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('admin_update_marks.html', student=student)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    students = conn.execute('SELECT id, name, email, profile_pic FROM students WHERE email != "admin@example.com"').fetchall()
    total_students = conn.execute('SELECT COUNT(*) AS total FROM students WHERE email != "admin@example.com"').fetchone()['total']
    avg_attendance = conn.execute('SELECT AVG(attended_classes * 100.0 / total_classes) AS avg_attendance FROM attendance WHERE total_classes > 0').fetchone()
    avg_marks = conn.execute('''
        SELECT 
            AVG(math_marks) AS math_avg, 
            AVG(science_marks) AS science_avg, 
            AVG(history_marks) AS history_avg,
            AVG(english_marks) AS english_avg
        FROM students 
        WHERE email != "admin@example.com"
    ''').fetchone()
    conn.close()

    avg_attendance = avg_attendance['avg_attendance'] if avg_attendance and avg_attendance['avg_attendance'] is not None else 0
    avg_marks = {
        'math_avg': avg_marks['math_avg'] if avg_marks and avg_marks['math_avg'] is not None else 0,
        'science_avg': avg_marks['science_avg'] if avg_marks and avg_marks['science_avg'] is not None else 0,
        'history_avg': avg_marks['history_avg'] if avg_marks and avg_marks['history_avg'] is not None else 0,
        'english_avg': avg_marks['english_avg'] if avg_marks and avg_marks['english_avg'] is not None else 0
    }

    students = [dict(student) for student in students]
    return render_template('admin_dashboard.html', students=students, total_students=total_students, avg_attendance=avg_attendance, avg_marks=avg_marks)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        phone = request.form['phone']
        roll_number = request.form['roll_number']
        department = request.form['department']
        conn = get_db_connection()
        existing_student = conn.execute('SELECT * FROM students WHERE email = ?', (email,)).fetchone()
        if existing_student:
            flash('Email already exists!', 'danger')
            conn.close()
            return redirect(url_for('register'))

        conn.execute('''
            INSERT INTO students (name, email, password, phone, roll_number, department)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password, phone, roll_number, department))
        conn.commit()
        conn.close()

        flash('Registration Successful! You can login now.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE email = ?', (email,)).fetchone()
        conn.close()

        if student and check_password_hash(student['password'], password):
            session['student_id'] = student['id']
            session['student_name'] = student['name']
            session['student_email'] = student['email']
            session['student_phone'] = student['phone']
            session['student_roll_number'] = student['roll_number']
            session['student_department'] = student['department']
            session['admin'] = (email == 'admin@example.com')  # Replace with your admin email
            session['role'] = 'admin' if session['admin'] else 'student'

            if session['admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()

    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('login'))

    student_data = {
        'id': student['id'],
        'name': student['name'],
        'email': student['email'],
        'phone': student['phone'],
        'roll_number': student['roll_number'],
        'department': student['department'],
        'profile_pic': student['profile_pic'] if student['profile_pic'] else 'default.png'
    }

    return render_template('dashboard.html', student=student_data)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        roll_number = request.form['roll_number']
        department = request.form['department']
        file = request.files.get('file')

        conn = get_db_connection()

        # Fetch the current profile picture
        current_profile_pic = conn.execute('SELECT profile_pic FROM students WHERE id = ?', (session['student_id'],)).fetchone()['profile_pic']

        # Handle profile picture upload
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Delete the old profile picture if it's not the default
            if current_profile_pic and current_profile_pic != 'default.png':
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], current_profile_pic)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Save the new profile picture
            file.save(file_path)
            conn.execute('''
                UPDATE students
                SET profile_pic = ?
                WHERE id = ?
            ''', (filename, session['student_id']))
        else:
            # Ensure profile_pic remains as default.png if no file is uploaded
            conn.execute('''
                UPDATE students
                SET profile_pic = COALESCE(profile_pic, 'default.png')
                WHERE id = ?
            ''', (session['student_id'],))

        # Update other profile details
        conn.execute('''
            UPDATE students
            SET name = ?, email = ?, phone = ?, roll_number = ?, department = ?
            WHERE id = ?
        ''', (name, email, phone, roll_number, department, session['student_id']))
        conn.commit()
        conn.close()

        # Update session variables
        session['student_name'] = name
        session['student_email'] = email
        session['student_phone'] = phone
        session['student_roll_number'] = roll_number
        session['student_department'] = department

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    student = {
        'name': session['student_name'],
        'email': session['student_email'],
        'phone': session['student_phone'],
        'roll_number': session['student_roll_number'],
        'department': session['student_department'],
        'profile_pic': session.get('student_profile_pic', 'default.png')
    }
    return render_template('edit_profile.html', student=student)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    students = conn.execute('SELECT id, name, email FROM students').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', students=students)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Fetch the student's profile picture filename
    student = conn.execute('SELECT profile_pic FROM students WHERE id = ?', (id,)).fetchone()
    if student and student['profile_pic'] != 'default.png':  # Ensure it's not the default picture
        profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], student['profile_pic'])
        if os.path.exists(profile_pic_path):
            os.remove(profile_pic_path)  # Delete the profile picture file

    # Delete related attendance records first (if any)
    conn.execute('DELETE FROM attendance WHERE student_id = ?', (id,))

    # Delete the student record
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Student and their profile picture deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/student_details')
def student_details():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()

    student_data = {
        'id': student['id'],
        'name': student['name'],
        'email': student['email'],
        'phone': student['phone'],
        'roll_number': student['roll_number'],
        'department': student['department'],
        'math_marks': student['math_marks'],
        'science_marks': student['science_marks'],
        'history_marks': student['history_marks'],
        'profile_pic': student['profile_pic'] if student['profile_pic'] else 'default.png'
    }
    return render_template('student_details.html', student=student_data)

@app.route('/attendance')
def attendance():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    attendance = conn.execute('SELECT * FROM attendance WHERE student_id = ?', (session['student_id'],)).fetchone()
    conn.close()

    if attendance:
        attendance_data = {
            'total_classes': attendance['total_classes'],
            'attended_classes': attendance['attended_classes'],
            'attendance_percentage': round((attendance['attended_classes'] / attendance['total_classes']) * 100, 2) if attendance['total_classes'] > 0 else 0
        }
    else:
        attendance_data = {
            'total_classes': 0,
            'attended_classes': 0,
            'attendance_percentage': 0
        }

    return render_template('attendance.html', attendance=attendance_data)

@app.route('/update_attendance/<int:id>', methods=['GET', 'POST'])
def update_attendance(id):
    if 'admin' not in session or not session['admin']:
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    attendance = conn.execute('SELECT * FROM attendance WHERE student_id = ?', (id,)).fetchone()

    if request.method == 'POST':
        total_classes = request.form['total_classes']
        attended_classes = request.form['attended_classes']

        if attendance:
            # Update existing attendance record
            conn.execute('''
                UPDATE attendance
                SET total_classes = ?, attended_classes = ?
                WHERE student_id = ?
            ''', (total_classes, attended_classes, id))
        else:
            # Insert new attendance record
            conn.execute('''
                INSERT INTO attendance (student_id, total_classes, attended_classes)
                VALUES (?, ?, ?)
            ''', (id, total_classes, attended_classes))

        conn.commit()
        conn.close()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('admin_update_attendance.html', student=student, attendance=attendance)

@app.route('/view_marks')
def view_marks():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()

    def calculate_grade(marks):
        if marks >= 90:
            return 'A'
        elif marks >= 75:
            return 'B'
        elif marks >= 50:
            return 'C'
        else:
            return 'D'

    # Function to calculate CGPA
    def calculate_cgpa(math, science, history, english):
        total_marks = math + science + history + english
        max_marks = 400  # Assuming each subject is out of 100
        percentage = (total_marks / max_marks) * 100

        # Convert percentage to CGPA (scale of 10)
        cgpa = percentage / 9.5  # Common conversion formula
        return round(cgpa, 2)

    # Calculate grades and CGPA
    marks_data = {
        'math_marks': student['math_marks'],
        'science_marks': student['science_marks'],
        'history_marks': student['history_marks'],
        'english_marks': student['english_marks'],
        'grades': {
            'math': calculate_grade(student['math_marks']),
            'science': calculate_grade(student['science_marks']),
            'history': calculate_grade(student['history_marks']),
            'english': calculate_grade(student['english_marks'])
        },
        'cgpa': calculate_cgpa(
            student['math_marks'],
            student['science_marks'],
            student['history_marks'],
            student['english_marks']
        )
    }

    return render_template('view_marks.html', marks=marks_data)

@app.route('/export_students')
def export_students():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Exclude admin from the export
    students = conn.execute('SELECT * FROM students WHERE email != "admin@example.com"').fetchall()
    conn.close()

    # Convert SQLite rows to a list of dictionaries
    student_list = [dict(student) for student in students]

    # Create a DataFrame from the list of dictionaries
    import pandas as pd
    df = pd.DataFrame(student_list)

    # Ensure the export directory exists
    export_dir = os.path.join('static', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    # Save the DataFrame to an Excel file
    file_path = os.path.join(export_dir, 'students.xlsx')
    df.to_excel(file_path, index=False)

    flash('Student data exported successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/export_attendance')
def export_attendance():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    attendance = conn.execute('SELECT * FROM attendance').fetchall()
    conn.close()

    attendance_list = [dict(record) for record in attendance]

    import pandas as pd
    df = pd.DataFrame(attendance_list)

    export_dir = os.path.join('static', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    file_path = os.path.join(export_dir, 'attendance.xlsx')
    df.to_excel(file_path, index=False)

    flash('Attendance report exported successfully!', 'success')
    return redirect(url_for('admin_dashboard'))



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE email = ? AND phone = ?', (email, phone)).fetchone()
        conn.close()

        if student:
            # Generate a reset token (for simplicity, use the email as the token)
            reset_token = email

            # Redirect to the reset password page with the token
            flash('Authentication successful! Please reset your password.', 'success')
            return redirect(url_for('reset_password', token=reset_token))
        else:
            flash('No account found with the provided email and phone number.', 'danger')

    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if new_password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('reset_password', token=token))

        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE email = ?', (token,)).fetchone()

        if not student:
            flash('Invalid token or user not found.', 'danger')
            conn.close()
            return redirect(url_for('reset_password_request'))

        # Check if the new password is the same as the current password
        if check_password_hash(student['password'], new_password):
            flash('New password cannot be the same as the current password.', 'danger')
            conn.close()
            return redirect(url_for('reset_password', token=token))

        # Hash the new password and update it in the database
        hashed_password = generate_password_hash(new_password)
        conn.execute('UPDATE students SET password = ? WHERE email = ?', (hashed_password, token))
        conn.commit()
        conn.close()

        flash('Your password has been reset successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if current_password == new_password:
            flash('New password cannot be the same as the current password.', 'danger')
            return redirect(url_for('change_password'))
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()

        # Check if the current password matches
        if not check_password_hash(student['password'], current_password):
            flash('Current password is incorrect.', 'danger')
            conn.close()
            return redirect(url_for('change_password'))

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'danger')
            conn.close()
            return redirect(url_for('change_password'))

        # Update the password in the database
        hashed_password = generate_password_hash(new_password)
        conn.execute('UPDATE students SET password = ? WHERE id = ?', (hashed_password, session['student_id']))
        conn.commit()
        conn.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/mark_attendance/<int:class_id>', methods=['GET'])
def mark_attendance(class_id):
    if 'student_id' not in session:
        flash('Please log in to mark attendance.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO attendance (student_id, class_id, total_classes, attended_classes)
        VALUES (?, ?, 1, 1)
        ON CONFLICT(student_id, class_id) DO UPDATE SET
        total_classes = total_classes + 1,
        attended_classes = attended_classes + 1
    ''', (session['student_id'], class_id))
    conn.commit()
    conn.close()

    flash('Attendance marked successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',port=5000)