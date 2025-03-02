import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY ,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY ,
    student_name TEXT NOT NULL,
    password TEXT NOT NULL
)
''')
cursor.execute('''
    CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    teacher_id INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
)''')
cursor.execute('''
  
    CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject_name TEXT,
    teacher_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
)

''')

# Add a sample teacher
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (1,"Dr.Jisha","drjisha@gmail.com", "jisha123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (2,"Dincy Paul","dincy@gmail.com", "dincy123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (3,"Lekshmi","lekshmi@gmail.com", "lekshmi123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (4,"Ms.Ajith","ajith@gmail.com", "ajith123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (5,"Dr.Jincy","drjincy@gmail.com", "jincy123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (6,"Dr.Mary","drmary@gmail.com", "mary123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (7,"Mehbooba","mehbooba@gmail.com", "mehbooba123")
''')
cursor.execute('''
INSERT INTO teachers (id,name,email,password)
VALUES (8,"Janani","janani@gmail.com", "janani123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (1,"Alphy Geevarghese", "alphy123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (2,"Arun Vijo Tharakan", "arun123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (3,"Athul K", "athul123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (4,"Ashwin Prathap", "ashwin123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (5,"Abhinav Nair", "abhinav123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (6,"Alen Thomas John", "alen123")
''')
cursor.execute('''
INSERT INTO students (id,student_name,password)
VALUES (7,"Athul K", "athul123")
''')

cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (1,"Mini Project",1)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (2,"CD",2)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (3,"IEFT",3)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (4,"Comprehensive",4)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (5,"CGIP",5)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (6,"Program Elective",6)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (7,"CN Lab",7)
''')
cursor.execute('''
INSERT INTO subjects (id,subject_name,teacher_id)
VALUES (8,"AAD",8)
''')
cursor.execute('''
             CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER ,
    teacher_id INTEGER ,
    subject_name TEXT ,
    date TEXT ,
    start_time TEXT ,
    end_time TEXT ,
    status TEXT DEFAULT 'Absent',
    time TEXT DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)


)



''')
# Create the timetable table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        day TEXT,
        period1 TEXT,
        period2 TEXT,
        period3 TEXT,
        period4 TEXT,
        period5 TEXT,
        period6 TEXT,
        period7 TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
''')

cursor.execute('''
ALTER TABLE attendance ADD COLUMN day TEXT;

''')






conn.commit()
conn.close()
