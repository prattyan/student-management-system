import os
import sqlite3
import time
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.config['SESSION_COOKIE_NAME'] = 'session_cookie'
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  
app.config['SESSION_PERMANENT'] = False  
app.config['SESSION_USE_SIGNER'] = True  
from fpdf import FPDF

def get_ist_now():
    """Get the current time in IST (Indian Standard Time)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist)

@app.route('/export_all_admit_cards')
def export_all_admit_cards():
    from fpdf import FPDF

    export_dir = os.path.join('static', 'admit_cards')
    os.makedirs(export_dir, exist_ok=True)
    uploads_dir = os.path.join('static', 'uploads')
    logo_path = os.path.join('static', 'logo.png') 
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()  # All students
    conn.close()
    exam_settings = get_exam_settings()
    for student in students:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_line_width(1.5)
        pdf.set_draw_color(44, 62, 80)
        pdf.rect(5, 5, 200, 287)
        pdf.set_xy(10, 30)
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(190, 15, "ADMIT CARD", ln=True, align='C')
        profile_pic = student['profile_pic'] if student['profile_pic'] else 'default.png'
        pic_path = os.path.join(uploads_dir, profile_pic)
        if not os.path.exists(pic_path):
            pic_path = os.path.join(uploads_dir, 'default.png')
        try:
            pdf.image(pic_path, x=150, y=30, w=35, h=35)
        except:
            pass
        pdf.set_xy(10, 80)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(50, 10, "Name:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['name']}", ln=1)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Roll Number:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['roll_number']}", ln=1)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Department:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['department']}", ln=1)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Email:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['email']}", ln=1)
        pdf.ln(5)
        pdf.set_draw_color(127, 140, 141)
        pdf.set_line_width(0.5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 10, "Exam Details", ln=1, align='L')
        pdf.set_text_color(44, 62, 80)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Exam Center: {exam_settings['exam_center']}", ln=1, align='L')
        pdf.cell(0, 8, f"Date: {exam_settings['exam_date']}", ln=1, align='L')
        pdf.cell(0, 8, f"Reporting Time: {exam_settings['reporting_time']}", ln=1, align='L')
        signature_path = os.path.join('static', 'signature.png')
        if os.path.exists(signature_path):
            pdf.image(signature_path, x=140, y=pdf.get_y(), w=50, h=20)
            pdf.ln(18) 
        pdf.set_font("Arial", 'I', 12)
        pdf.set_draw_color(44, 62, 80)
        pdf.line(140, pdf.get_y(), 200, pdf.get_y())
        pdf.cell(0, 10, "Signature of Controller of Examinations", ln=1, align='R')
        file_path = os.path.join(export_dir, f"admit_card_{student['id']}.pdf")
        pdf.output(file_path)
    flash('All Admit cards exported', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/export_all_profiles')
def export_all_profiles():
    from fpdf import FPDF
    import os
    export_dir = os.path.join('static', 'profiles')
    os.makedirs(export_dir, exist_ok=True)
    uploads_dir = os.path.join('static', 'uploads')

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    for student in students:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_line_width(1.2)
        pdf.set_draw_color(52, 73, 94)
        pdf.rect(8, 8, 194, 281)

        # Heading
        pdf.set_xy(10, 20)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(190, 15, "Student Profile", ln=True, align='C')

        # Student Picture
        profile_pic = student['profile_pic'] if student['profile_pic'] else 'default.png'
        pic_path = os.path.join(uploads_dir, profile_pic)
        if not os.path.exists(pic_path):
            pic_path = os.path.join(uploads_dir, 'default.png')
        try:
            pdf.image(pic_path, x=85, y=40, w=40, h=40)
        except:
            pass

        # Student Info
        pdf.set_xy(10, 90)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(50, 10, "Name:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['name']}", ln=1)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Email:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['email']}", ln=1)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Phone:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['phone']}", ln=1)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Roll Number:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['roll_number']}", ln=1)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(50, 10, "Department:", ln=0)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, f"{student['department']}", ln=1)

        # Marks (optional)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 10, "Marks", ln=1, align='L')
        pdf.set_text_color(52, 73, 94)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Math: {student['math_marks']}", ln=1, align='L')
        pdf.cell(0, 8, f"Science: {student['science_marks']}", ln=1, align='L')
        pdf.cell(0, 8, f"English: {student['english_marks']}", ln=1, align='L')
        pdf.cell(0, 8, f"Social Science: {student['social_science_marks']}", ln=1, align='L')
        pdf.cell(0, 8, f"2nd Language: {student['second_language_marks']}", ln=1, align='L')

        file_path = os.path.join(export_dir, f"profile_{student['id']}.pdf")
        pdf.output(file_path)

    flash('All student profiles exported successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

DATABASE = 'students.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/download_admit_card/<int:student_id>')
def download_admit_card(student_id):
    # Only allow the logged-in student or admin to download
    if 'student_id' not in session or (session['student_id'] != student_id and not session.get('admin')):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('dashboard'))

    if not student['exam_fee_paid']:
        flash('You must pay the exam fees to download your admit card.', 'warning')
        return redirect(url_for('dashboard'))

    exam_settings = get_exam_settings()
    uploads_dir = os.path.join('static', 'uploads')
    profile_pic = student['profile_pic'] if student['profile_pic'] else 'default.png'
    pic_path = os.path.join(uploads_dir, profile_pic)
    if not os.path.exists(pic_path):
        pic_path = os.path.join(uploads_dir, 'default.png')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_line_width(1.5)
    pdf.set_draw_color(44, 62, 80)
    pdf.rect(5, 5, 200, 287)
    pdf.set_xy(10, 30)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(190, 15, "ADMIT CARD", ln=True, align='C')
    try:
        pdf.image(pic_path, x=150, y=30, w=35, h=35)
    except:
        pass
    pdf.set_xy(10, 80)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(50, 10, "Name:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['name']}", ln=1)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Roll Number:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['roll_number']}", ln=1)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Department:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['department']}", ln=1)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Email:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['email']}", ln=1)
    pdf.ln(5)
    pdf.set_draw_color(127, 140, 141)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, "Exam Details", ln=1, align='L')
    pdf.set_text_color(44, 62, 80)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Exam Center: {exam_settings['exam_center']}", ln=1, align='L')
    pdf.cell(0, 8, f"Date: {exam_settings['exam_date']}", ln=1, align='L')
    pdf.cell(0, 8, f"Reporting Time: {exam_settings['reporting_time']}", ln=1, align='L')
    signature_path = os.path.join('static', 'signature.png')
    if os.path.exists(signature_path):
        pdf.image(signature_path, x=140, y=pdf.get_y(), w=50, h=20)
        pdf.ln(18)
    pdf.set_font("Arial", 'I', 12)
    pdf.set_draw_color(44, 62, 80)
    pdf.line(140, pdf.get_y(), 200, pdf.get_y())
    pdf.cell(0, 10, "Signature of Controller of Examinations", ln=1, align='R')

    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f'admit_card_{student['id']}.pdf', mimetype='application/pdf')

@app.route('/download_profile/<int:student_id>')
def download_profile(student_id):
    # Only allow the logged-in student or admin to download
    if 'student_id' not in session or (session['student_id'] != student_id and not session.get('admin')):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    uploads_dir = os.path.join('static', 'uploads')
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('dashboard'))

    profile_pic = student['profile_pic'] if student['profile_pic'] else 'default.png'
    pic_path = os.path.join(uploads_dir, profile_pic)
    if not os.path.exists(pic_path):
        pic_path = os.path.join(uploads_dir, 'default.png')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_line_width(1.2)
    pdf.set_draw_color(52, 73, 94)
    pdf.rect(8, 8, 194, 281)

    # Heading
    pdf.set_xy(10, 20)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(190, 15, "Student Profile", ln=True, align='C')

    # Student Picture
    try:
        pdf.image(pic_path, x=85, y=40, w=40, h=40)
    except:
        pass

    # Student Info
    pdf.set_xy(10, 90)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(50, 10, "Name:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['name']}", ln=1)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Email:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['email']}", ln=1)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Phone:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['phone']}", ln=1)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Roll Number:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['roll_number']}", ln=1)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "Department:", ln=0)
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"{student['department']}", ln=1)

    # Marks (optional)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, "Marks", ln=1, align='L')
    pdf.set_text_color(52, 73, 94)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Math: {student['math_marks']}", ln=1, align='L')
    pdf.cell(0, 8, f"Science: {student['science_marks']}", ln=1, align='L')
    pdf.cell(0, 8, f"History: {student['history_marks']}", ln=1, align='L')
    pdf.cell(0, 8, f"English: {student['english_marks']}", ln=1, align='L')

    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f'profile_{student["id"]}.pdf', mimetype='application/pdf')

def init_db():
    with get_db_connection() as conn:
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
                social_science_marks INTEGER DEFAULT 0,
                english_marks INTEGER DEFAULT 0,
                second_language_marks INTEGER DEFAULT 0,
                session_token TEXT,
                exam_fee_paid INTEGER DEFAULT 0,
                exam_fee_payment_time TEXT,
                last_login TEXT,
                last_login_ip TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                total_classes INTEGER DEFAULT 0,
                attended_classes INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exam_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_center TEXT DEFAULT 'Main Campus',
                exam_date TEXT DEFAULT '01 June 2025',
                reporting_time TEXT DEFAULT '09:00 AM',
                exam_fee_payment_open INTEGER DEFAULT 0,
                exam_fee INTEGER DEFAULT 1000
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                student_name TEXT,
                message TEXT,
                reply TEXT,
                created_at TEXT,
                replied_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

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
        student_id = session['student_id']
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{student_id}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

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

@app.route('/contact_admin', methods=['GET', 'POST'])
def contact_admin():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form['message']
        student_id = session['student_id']
        student_name = session['student_name']
        created_at = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (student_id, student_name, message, created_at) VALUES (?, ?, ?, ?)',
                     (student_id, student_name, message, created_at))
        conn.commit()
        conn.close()
        flash('Your message has been sent to the admin.', 'success')
        return redirect(url_for('dashboard'))

    # Show previous messages and replies
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages WHERE student_id = ? ORDER BY created_at DESC', (session['student_id'],)).fetchall()
    conn.close()
    return render_template('contact_admin.html', messages=messages)
@app.route('/admin_messages', methods=['GET', 'POST'])
def admin_messages():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        reply = request.form['reply']
        message_id = request.form['message_id']
        replied_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('UPDATE messages SET reply = ?, replied_at = ? WHERE id = ?', (reply, replied_at, message_id))
        conn.commit()
        flash('Reply sent.', 'success')

    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_messages.html', messages=messages)
@app.route('/update_marks/<int:id>', methods=['GET', 'POST'])
def update_marks(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        math_marks = int(request.form['math_marks'])
        science_marks = int(request.form['science_marks'])
        social_science_marks = int(request.form['social_science_marks'])
        english_marks = int(request.form['english_marks'])
        second_language_marks = int(request.form['second_language_marks'])

        conn.execute('''
            UPDATE students
            SET math_marks = ?, science_marks = ?, social_science_marks = ?, english_marks = ?, second_language_marks = ?
            WHERE id = ?
        ''', (math_marks, science_marks, social_science_marks, english_marks, second_language_marks, id))
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
    students = conn.execute('SELECT id, name, email, profile_pic, exam_fee_paid, last_login, last_login_ip FROM students WHERE email != "admin@example.com"').fetchall()
    total_students = conn.execute('SELECT COUNT(*) AS total FROM students WHERE email != "admin@example.com"').fetchone()['total']
    avg_attendance = conn.execute('SELECT AVG(attended_classes * 100.0 / total_classes) AS avg_attendance FROM attendance WHERE total_classes > 0').fetchone()
    avg_marks = conn.execute('''
        SELECT 
            AVG(math_marks) AS math_avg, 
            AVG(science_marks) AS science_avg, 
            AVG(social_science_marks) AS social_science_avg,
            AVG(english_marks) AS english_avg,
            AVG(second_language_marks) AS second_language_avg
        FROM students 
        WHERE email != "admin@example.com"
    ''').fetchone()
    conn.close()

    # Check export status for each student
    updated_students = []
    for student in students:
        s = dict(student)
        student_id = s['id']
        admit_card_path = os.path.join('static', 'admit_cards', f'admit_card_{student_id}.pdf')
        profile_pdf_path = os.path.join('static', 'profiles', f'profile_{student_id}.pdf')
        s['admit_card_exported'] = os.path.exists(admit_card_path)
        s['profile_exported'] = os.path.exists(profile_pdf_path)
        updated_students.append(s)

    students = updated_students

    avg_attendance = avg_attendance['avg_attendance'] if avg_attendance and avg_attendance['avg_attendance'] is not None else 0
    avg_marks = {
        'math_avg': avg_marks['math_avg'] if avg_marks and avg_marks['math_avg'] is not None else 0,
        'science_avg': avg_marks['science_avg'] if avg_marks and avg_marks['science_avg'] is not None else 0,
        'social_science_avg': avg_marks['social_science_avg'] if avg_marks and avg_marks['social_science_avg'] is not None else 0,
        'english_avg': avg_marks['english_avg'] if avg_marks and avg_marks['english_avg'] is not None else 0,
        'second_language_avg': avg_marks['second_language_avg'] if avg_marks and avg_marks['second_language_avg'] is not None else 0
    }

    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(m in user_agent for m in ['iphone', 'android', 'ipad', 'mobile'])

    template = 'admin_dashboard_mobile.html' if is_mobile else 'admin_dashboard.html'
    return render_template(template, students=students, total_students=total_students, avg_attendance=avg_attendance, avg_marks=avg_marks)
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
            flash('Email already registered. Please login.', 'danger')
            conn.close()
            return redirect(url_for('login'))

        conn.execute('''
            INSERT INTO students (name, email, password, phone, roll_number, department)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password, phone, roll_number, department))
        conn.commit()
        conn.close()

        flash('Registration Successful! You can login now.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

import uuid

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE email = ?', (email,)).fetchone()

        if student and check_password_hash(student['password'], password):
            login_time = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')
            login_ip = request.remote_addr
            conn.execute('UPDATE students SET last_login = ?, last_login_ip = ? WHERE id = ?', (login_time, login_ip, student['id']))
            conn.commit()
            # ...existing session logic...
            session['student_id'] = student['id']
            session['student_name'] = student['name']
            session['student_email'] = student['email']
            session['student_phone'] = student['phone']
            session['student_roll_number'] = student['roll_number']
            session['student_department'] = student['department']
            session['student_profile_pic'] = student['profile_pic'] if student['profile_pic'] else 'default.png'
            session['admin'] = (student['email'] == 'admin@example.com')
            conn.close()
            if session['admin']:
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        else:
            conn.close()
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')
def is_session_valid():
    # If admin, always valid
    if session.get('admin'):
        return True
    if 'student_id' not in session or 'session_token' not in session:
        return False
    if 'expires_at' not in session or int(time.time()) > session['expires_at']:
        conn = get_db_connection()
        conn.execute('UPDATE students SET session_token = NULL WHERE id = ?', (session['student_id'],))
        conn.commit()
        conn.close()
        session.clear()
        return False
    conn = get_db_connection()
    student = conn.execute('SELECT session_token FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()
    return student and student['session_token'] == session['session_token']

@app.route('/dashboard')
def dashboard():
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
        'profile_pic': student['profile_pic'] if student['profile_pic'] else 'default.png',
        'exam_fee_paid': student['exam_fee_paid']
    }

    exam_settings = get_exam_settings()
    exam_fee_payment_open = exam_settings['exam_fee_payment_open'] if exam_settings else 0
    admit_card_available = exam_settings['admit_card_available'] if exam_settings else 0

    return render_template(
        'dashboard.html',
        student=student_data,
        exam_fee_payment_open=exam_fee_payment_open,
        admit_card_available=admit_card_available
    )
@app.route('/delete_all_admit_cards')
def delete_all_admit_cards():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('admin_dashboard'))

    admit_cards_dir = os.path.join('static', 'admit_cards')
    deleted = 0
    if os.path.exists(admit_cards_dir):
        for filename in os.listdir(admit_cards_dir):
            if filename.endswith('.pdf'):
                try:
                    os.remove(os.path.join(admit_cards_dir, filename))
                    deleted += 1
                except Exception:
                    pass
    flash(f'Deleted {deleted} admit card(s).', 'success')
    return redirect(url_for('admin_dashboard'))
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
        current_profile_pic = conn.execute('SELECT profile_pic FROM students WHERE id = ?', (session['student_id'],)).fetchone()['profile_pic']

        # Handle profile picture upload
        if file and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{session['student_id']}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            conn.execute('UPDATE students SET profile_pic = ? WHERE id = ?', (filename, session['student_id']))
        # else: do nothing, keep current

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

        # Fetch the updated profile_pic from the database and update session
        conn = get_db_connection()
        profile_pic_row = conn.execute('SELECT profile_pic FROM students WHERE id = ?', (session['student_id'],)).fetchone()
        conn.close()
        session['student_profile_pic'] = profile_pic_row['profile_pic'] if profile_pic_row and profile_pic_row['profile_pic'] else 'default.png'

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
        return redirect(url_for('admin_dashboard'))
    conn = get_db_connection()
    student = conn.execute('SELECT profile_pic FROM students WHERE id = ?', (id,)).fetchone()

    # Delete profile picture if not default
    if student and student['profile_pic'] and student['profile_pic'] != 'default.png':
        pic_path = os.path.join(app.config['UPLOAD_FOLDER'], student['profile_pic'])
        if os.path.exists(pic_path):
            os.remove(pic_path)

    # Delete admit card PDF
    admit_card_path = os.path.join('static', 'admit_cards', f"admit_card_{id}.pdf")
    if os.path.exists(admit_card_path):
        os.remove(admit_card_path)

    # Delete profile PDF
    profile_pdf_path = os.path.join('static', 'profiles', f"profile_{id}.pdf")
    if os.path.exists(profile_pdf_path):
        os.remove(profile_pdf_path)

    # Delete attendance records
    conn.execute('DELETE FROM attendance WHERE student_id = ?', (id,))
    # Delete student record
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Student and all their data deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    if 'student_id' in session:
        conn = get_db_connection()
        conn.execute('UPDATE students SET session_token = NULL WHERE id = ?', (session['student_id'],))
        conn.commit()
        conn.close()
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
        'social_science_marks': student['social_science_marks'],
        'second_language_marks': student['second_language_marks'],
        'english_marks': student['english_marks'],
        'profile_pic': student['profile_pic'] if student['profile_pic'] else 'default.png'
    }

    # Check if profile PDF exists
    profile_pdf_path = os.path.join('static', 'profiles', f"profile_{student['id']}.pdf")
    profile_pdf_available = os.path.exists(profile_pdf_path)

    return render_template('student_details.html', student=student_data, profile_pdf_available=profile_pdf_available)

@app.route('/pay_exam_fees', methods=['GET', 'POST'])
def pay_exam_fees():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    exam_settings = get_exam_settings()
    if not exam_settings['exam_fee_payment_open']:
        flash('Exam fee payment is currently closed. Please contact admin.', 'warning')
        return redirect(url_for('dashboard'))

    fee = exam_settings['exam_fee'] if 'exam_fee' in exam_settings.keys() else 1000

    if request.method == 'POST':
        payment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        conn.execute('UPDATE students SET exam_fee_paid = 1, exam_fee_payment_time = ? WHERE id = ?', (payment_time, session['student_id']))
        conn.commit()
        conn.close()
        flash('Exam fee payment successful!', 'success')
        return redirect(url_for('pay_exam_fees'))

    # Fetch payment status and time to show in template
    conn = get_db_connection()
    student = conn.execute('SELECT exam_fee_paid, exam_fee_payment_time FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()
    paid = student['exam_fee_paid']
    payment_time = student['exam_fee_payment_time'] if student['exam_fee_payment_time'] else None
    return render_template('pay_exam_fees.html', exam_fee_paid=paid, payment_time=payment_time, exam_fee=fee)

@app.route('/attendance')
def attendance():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    attendance = conn.execute('SELECT * FROM attendance WHERE student_id = ?', (session['student_id'],)).fetchone()
    today = get_ist_now().strftime('%Y-%m-%d')
    attendance_log = conn.execute(
        'SELECT * FROM attendance_log WHERE student_id = ? AND date = ?',
        (session['student_id'], today)
    ).fetchone()
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

    attendance_marked_today = attendance_log is not None

    return render_template(
        'attendance.html',
        attendance=attendance_data,
        attendance_marked_today=attendance_marked_today
    )
@app.route('/update_attendance/<int:id>', methods=['GET', 'POST'])
def update_attendance(id):
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    attendance = conn.execute('SELECT * FROM attendance WHERE student_id = ?', (id,)).fetchone()

    if request.method == 'POST':
        total_classes = int(request.form['total_classes'])
        attended_classes = int(request.form['attended_classes'])

        if attendance:
            conn.execute('''
                UPDATE attendance
                SET total_classes = ?, attended_classes = ?
                WHERE student_id = ?
            ''', (total_classes, attended_classes, id))
        else:
            conn.execute('''
                INSERT INTO attendance (student_id, total_classes, attended_classes)
                VALUES (?, ?, ?)
            ''', (id, total_classes, attended_classes))

        conn.commit()
        conn.close()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    attendance_data = {
        'total_classes': attendance['total_classes'] if attendance else 0,
        'attended_classes': attendance['attended_classes'] if attendance else 0
    }
    conn.close()
    return render_template('admin_update_attendance.html', student=student, attendance=attendance_data)
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

    def calculate_cgpa(math, science, social_science, english, second_language):
        return round((math + science + social_science + english + second_language) / 5 / 10, 2)

    marks_data = {
    'math_marks': student['math_marks'],
    'science_marks': student['science_marks'],
    'social_science_marks': student['social_science_marks'],
    'english_marks': student['english_marks'],
    'second_language_marks': student['second_language_marks'],
    'grades': {
        'math': calculate_grade(student['math_marks']),
        'science': calculate_grade(student['science_marks']),
        'social_science': calculate_grade(student['social_science_marks']),
        'english': calculate_grade(student['english_marks']),
        'second_language': calculate_grade(student['second_language_marks'])
    },
    'cgpa': calculate_cgpa(
        student['math_marks'],
        student['science_marks'],
        student['social_science_marks'],
        student['english_marks'],
        student['second_language_marks']
    )
}

    return render_template('view_marks.html', marks=marks_data)

@app.route('/export_students')
def export_students():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students WHERE email != "admin@example.com"').fetchall()
    conn.close()

    student_list = [dict(student) for student in students]
    df = pd.DataFrame(student_list)

    export_dir = os.path.join('static', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    file_path = os.path.join(export_dir, 'students.xlsx')
    df.to_excel(file_path, index=False)

    flash('Student data exported successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/export_attendance')
def export_attendance():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    attendance = conn.execute('SELECT * FROM attendance').fetchall()
    conn.close()

    attendance_list = [dict(record) for record in attendance]
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
            # In a real app, generate a token and send email
            token = os.urandom(16).hex()
            session['reset_token'] = token
            session['reset_student_id'] = student['id']
            flash('Verification successful. Please reset your password.', 'success')
            return redirect(url_for('reset_password', token=token))
        else:
            flash('No matching student found.', 'danger')
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        if 'reset_token' in session and session['reset_token'] == token:
            conn = get_db_connection()
            conn.execute('UPDATE students SET password = ? WHERE id = ?', (generate_password_hash(password), session['reset_student_id']))
            conn.commit()
            conn.close()
            session.pop('reset_token', None)
            session.pop('reset_student_id', None)
            flash('Password reset successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired token.', 'danger')
    return render_template('reset_password.html', token=token)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'student_id' not in session:
        flash('Please login to change password.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('change_password.html')
        conn = get_db_connection()
        student = conn.execute('SELECT password FROM students WHERE id = ?', (session['student_id'],)).fetchone()
        if not student or not check_password_hash(student['password'], current_password):
            flash('Current password is incorrect.', 'danger')
            conn.close()
            return render_template('change_password.html')
        conn.execute('UPDATE students SET password = ? WHERE id = ?', (generate_password_hash(new_password), session['student_id']))
        conn.commit()
        conn.close()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/mark_attendance', methods=['GET'])
def mark_attendance():
    if 'student_id' not in session:
        flash('Please login to mark attendance.', 'danger')
        return redirect(url_for('login'))

    today = get_ist_now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    # Check if already marked today
    already_marked = conn.execute(
        'SELECT * FROM attendance_log WHERE student_id = ? AND date = ?',
        (session['student_id'], today)
    ).fetchone()

    if already_marked:
        flash('You have already marked attendance for today.', 'warning')
        conn.close()
        return redirect(url_for('dashboard'))

    # Mark attendance
    attendance = conn.execute('SELECT * FROM attendance WHERE student_id = ?', (session['student_id'],)).fetchone()
    if attendance:
        conn.execute('''
            UPDATE attendance
            SET total_classes = total_classes + 1,
                attended_classes = attended_classes + 1
            WHERE student_id = ?
        ''', (session['student_id'],))
    else:
        conn.execute('''
            INSERT INTO attendance (student_id, total_classes, attended_classes)
            VALUES (?, 1, 1)
        ''', (session['student_id'],))
    # Log today's attendance
    conn.execute('INSERT INTO attendance_log (student_id, date) VALUES (?, ?)', (session['student_id'], today))
    conn.commit()
    conn.close()

    flash('Attendance marked successfully!', 'success')
    return redirect(url_for('dashboard'))
@app.route('/admit_card')
def admit_card():
    if 'student_id' not in session:
        flash('Please login to view admit card.', 'danger')
        return redirect(url_for('login'))

    exam_settings = get_exam_settings()
    if not exam_settings['admit_card_available']:
        flash('Admit card download is currently disabled by admin.', 'warning')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (session['student_id'],)).fetchone()
    conn.close()

    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('login'))

    if not student['exam_fee_paid']:
        flash('You must pay the exam fees to access your admit card.', 'warning')
        return redirect(url_for('dashboard'))

    exam_settings = get_exam_settings()
    admit_card_pdf_path = os.path.join('static', 'admit_cards', f"admit_card_{student['id']}.pdf")
    admit_card_pdf_exists = os.path.exists(admit_card_pdf_path)

    return render_template(
        'admit_card.html',
        student=student,
        exam_settings=exam_settings,
        admit_card_pdf_exists=admit_card_pdf_exists
    )
@app.route('/clear_all_exam_fee_payments')
def clear_all_exam_fee_payments():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    conn.execute('UPDATE students SET exam_fee_paid = 0, exam_fee_payment_time = NULL')
    conn.commit()
    conn.close()
    flash('All exam fee payment records have been cleared.', 'success')
    return redirect(url_for('admin_dashboard'))
@app.route('/exam_settings', methods=['GET', 'POST'])
def exam_settings():
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM exam_settings LIMIT 1').fetchone()

    if request.method == 'POST':
        exam_center = request.form['exam_center']
        exam_date = request.form['exam_date']
        reporting_time = request.form['reporting_time']
        exam_fee_payment_open = 1 if request.form.get('exam_fee_payment_open') == 'on' else 0
        admit_card_available = 1 if request.form.get('admit_card_available') == 'on' else 0
        exam_fee = int(request.form.get('exam_fee', 1000))

        conn.execute('''
            UPDATE exam_settings
            SET exam_center = ?, exam_date = ?, reporting_time = ?, exam_fee_payment_open = ?, admit_card_available = ?, exam_fee = ?
            WHERE id = ?
        ''', (exam_center, exam_date, reporting_time, exam_fee_payment_open, admit_card_available, exam_fee, settings['id']))
        conn.commit()
        flash('Exam settings updated!', 'success')
        settings = conn.execute('SELECT * FROM exam_settings LIMIT 1').fetchone()

    conn.close()
    return render_template('exam_settings.html', settings=settings)

def get_exam_settings():
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM exam_settings LIMIT 1').fetchone()
    conn.close()
    return settings

@app.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route('/delete_admit_card_pdf/<int:student_id>')
def delete_admit_card_pdf(student_id):
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('admin_dashboard'))
    admit_card_path = os.path.join('static', 'admit_cards', f"admit_card_{student_id}.pdf")
    if (os.path.exists(admit_card_path)):
        os.remove(admit_card_path)
        flash('Admit card PDF deleted.', 'success')
    else:
        flash('Admit card PDF not found.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_profile_pdf/<int:student_id>')
def delete_profile_pdf(student_id):
    if 'admin' not in session or not session['admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('admin_dashboard'))
    profile_pdf_path = os.path.join('static', 'profiles', f"profile_{student_id}.pdf")
    if (os.path.exists(profile_pdf_path)):
        os.remove(profile_pdf_path)
        flash('Profile PDF deleted.', 'success')
    else:
        flash('Profile PDF not found.', 'warning')
    return redirect(url_for('admin_dashboard'))
@app.route('/clear_session')
def clear_session():
    if 'student_id' in session:
        conn = get_db_connection()
        conn.execute('UPDATE students SET session_token = NULL WHERE id = ?', (session['student_id'],))
        conn.commit()
        conn.close()
    session.clear()
    flash('Session cleared successfully.', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)