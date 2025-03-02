from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import cv2
import face_recognition
import pickle
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection
def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load trained model
with open("trained_model.pkl", "rb") as model_file:
    model_data = pickle.load(model_file)

known_encodings = model_data["encodings"]
known_ids = model_data["names"]

# Store ongoing attendance sessions
active_sessions = {}

# Function to initialize attendance for the period
def start_attendance_period(teacher_id, subject_name):
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    start_time = now.strftime("%H:%M:%S")
    end_time = (now + timedelta(hours=1)).strftime("%H:%M:%S")  # 1-hour duration

    conn = get_db_connection()
    
    # Get all students enrolled in the subject
    students = conn.execute(
        "SELECT student_id FROM enrollments WHERE subject_name = ?", (subject_name,)
    ).fetchall()
    
    # Mark all students absent by default
    for student in students:
        student_id = student['student_id']
        conn.execute(
            "INSERT INTO attendance (student_id, teacher_id, subject_name, date, start_time, end_time, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (student_id, teacher_id, subject_name, date_string, start_time, end_time, "Absent")
        )
    
    conn.commit()
    conn.close()
    
    # Store active session
    active_sessions[teacher_id] = {
        "subject_name": subject_name,
        "end_time": datetime.now() + timedelta(hours=1),  # 1-hour window
        "marked_present": set()
    }
    print(f"⏳ Attendance session started for {subject_name} by Teacher {teacher_id}.")

# Function to mark attendance
# Function to mark attendance
def mark_attendance(user_id, teacher_id):
    if teacher_id not in active_sessions:
        print(f"⚠️ No active session for teacher {teacher_id}.")
        return  

    session_data = active_sessions[teacher_id]
    subject_name = session_data["subject_name"]
    
    now = datetime.now()
    date_today = now.strftime("%Y-%m-%d")
    day_today = now.strftime("%A")  # ✅ Get the current day
    time_now = now.strftime("%H:%M:%S")

    # ✅ Check if already marked in session memory
    if user_id in session_data["marked_present"]:
        print(f"⚠️ Student {user_id} already marked present in memory. Skipping.")
        return  

    conn = get_db_connection()
    
    # ✅ Check if attendance already exists in the database
    cursor = conn.execute(
        "SELECT status FROM attendance WHERE student_id = ? AND subject_name = ? AND date = ? AND teacher_id = ?",
        (user_id, subject_name, date_today, teacher_id)
    )
    existing_record = cursor.fetchone()

    if existing_record:
        print(f"🔍 Found existing attendance record for {user_id} on {day_today}: {existing_record['status']}")
        if existing_record['status'] == 'Present':
            print(f"⚠️ {user_id} is already marked Present in DB. Skipping update.")
            conn.close()
            return  
        
        # ✅ Update status if previously absent
        print(f"🔄 Updating {user_id} to Present...")
        conn.execute(
            "UPDATE attendance SET status = 'Present', time = ?, day = ? WHERE student_id = ? AND subject_name = ? AND date = ? AND teacher_id = ?",
            (time_now, day_today, user_id, subject_name, date_today, teacher_id)
        )
    else:
        # ✅ Insert a new attendance record with the day
        print(f"➕ Inserting new attendance record for {user_id} on {day_today}...")
        conn.execute(
            "INSERT INTO attendance (student_id, teacher_id, subject_name, date, day, start_time, end_time, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 'Present')",
            (user_id, teacher_id, subject_name, date_today, day_today, time_now, session_data["end_time"].strftime("%H:%M:%S"))
        )

    conn.commit()
    conn.close()

    # ✅ Add student to session tracking
    session_data["marked_present"].add(user_id)

    print(f"✅ Successfully marked {user_id} as Present on {day_today} in {subject_name}.")


# Function for real-time face recognition
def start_face_recognition(teacher_id):
    if teacher_id not in active_sessions:
        return

    session_data = active_sessions[teacher_id]
    subject_name = session_data["subject_name"]
    video_capture = cv2.VideoCapture(0)

    while datetime.now() < session_data["end_time"]:
        ret, frame = video_capture.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            user_id = "Unknown"

            if True in matches:
                matched_idx = matches.index(True)
                user_id = known_ids[matched_idx]
                mark_attendance(user_id, teacher_id)

        cv2.imshow("Real-Time Attendance Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print(f"🛑 Attendance session ended for {subject_name}.")

# Home route (Login page)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if role == 'student':
            user = conn.execute('SELECT * FROM students WHERE student_name = ? AND password = ?', 
                                (username, password)).fetchone()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['student_name']
                session['role'] = 'student'
                return redirect(url_for('studentdash'))
            else:
                flash('Invalid student credentials!', 'error')

        elif role == 'teacher':
            user = conn.execute('SELECT * FROM teachers WHERE name = ? AND password = ?', 
                                (username, password)).fetchone()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['name']
                session['role'] = 'teacher'
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid teacher credentials!', 'error')

        conn.close()

    return render_template('login.html')

# Teacher Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and session['role'] == 'teacher':
        return render_template('dashboard.html', teacher_name=session['username'])
    else:
        return redirect(url_for('login'))
@app.route('/studentdash')
def studentdash():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    student_id = session['user_id']
    student_name = session['username']
    
    conn = get_db_connection()

    # Fetch attendance for each subject on each date
    attendance_data = conn.execute(
        """SELECT date, subject_name, status 
           FROM attendance 
           WHERE student_id = ? 
           ORDER BY date DESC""", 
        (student_id,)
    ).fetchall()

    conn.close()

    # Convert attendance data into a dictionary: {date -> {subject -> status}}
    attendance = {}
    for row in attendance_data:
        date = row['date']
        subject = row['subject_name']
        status = row['status']
        if date not in attendance:
            attendance[date] = {}
        attendance[date][subject] = status

    return render_template('studentdash.html', student_name=student_name, attendance=attendance)

# API to fetch attendance by date
@app.route('/get_attendance', methods=['POST'])
def get_attendance():
    if 'user_id' not in session or session['role'] != 'student':
        return {'error': 'Unauthorized access'}

    student_id = session['user_id']
    date_selected = request.json.get('date')

    conn = get_db_connection()
    attendance_record = conn.execute(
        "SELECT status FROM attendance WHERE student_id = ? AND date = ?", 
        (student_id, date_selected)
    ).fetchone()
    conn.close()

    if attendance_record:
        return {'status': attendance_record['status']}
    else:
        return {'status': 'No record found'}

# Start attendance session
@app.route('/start_attendance')
def start_attendance():
    if 'user_id' in session and session['role'] == 'teacher':
        teacher_id = session['user_id']
        conn = get_db_connection()

        # Fetch subject name assigned to the teacher
        subject = conn.execute("SELECT subject_name FROM subjects WHERE teacher_id = ?", (teacher_id,)).fetchone()
        conn.close()

        if subject:
            subject_name = subject['subject_name']
            start_attendance_period(teacher_id, subject_name)
            threading.Thread(target=start_face_recognition, args=(teacher_id,)).start()
            flash(f'Real-time attendance started for {subject_name}!', 'info')
        else:
            flash('No subject assigned to this teacher!', 'error')

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

# View attendance
@app.route('/view_attendance')
def view_attendance():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    teacher_id = session['user_id']
    conn = get_db_connection()

    # Fetch attendance records for the teacher's subject
    attendance_data = conn.execute(
        """SELECT a.student_id, s.student_name, a.date, a.start_time,a.day, a.end_time, a.status 
           FROM attendance a 
           JOIN students s ON a.student_id = s.id
           WHERE a.teacher_id = ?""",
        (teacher_id,)
    ).fetchall()
    
    conn.close()
    return render_template('view_attendance.html', attendance_data=attendance_data)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
