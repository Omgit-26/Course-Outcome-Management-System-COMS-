"""
==========================================================
Course Outcome Management System (COMS)
Backend Application: backend.py
Description: Single-command Flask backend with built-in DBMS engine.
Runs completely with ONE command: python backend.py
Zero configuration, zero password setup required!
==========================================================
"""

import os
import sqlite3
import threading
import webbrowser
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Database file path (located right in project folder)
DB_FILE = os.path.join(os.path.dirname(__file__), 'course_outcome.db')


def get_db_connection():
    """Establishes and returns a connection to the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enables dictionary-style column access
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
    return conn


def init_database():
    """Initializes tables and seeds initial sample data automatically on startup."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL UNIQUE,
            course_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_outcomes (
            co_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            co_number TEXT NOT NULL,
            co_description TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            student_name TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            co_id INTEGER NOT NULL,
            assessment_name TEXT NOT NULL,
            max_marks REAL NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (co_id) REFERENCES course_outcomes(co_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_marks (
            marks_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            obtained_marks REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE,
            UNIQUE(student_id, assessment_id)
        )
    """)

    # 2. Check if sample data is already loaded
    cursor.execute("SELECT COUNT(*) AS count FROM courses")
    if cursor.fetchone()['count'] == 0:
        # Seed Courses
        cursor.executemany("""
            INSERT INTO courses (course_id, course_code, course_name)
            VALUES (?, ?, ?)
        """, [
            (1, 'CS301', 'Database Management Systems'),
            (2, 'CS302', 'Computer Networks'),
            (3, 'CS303', 'Operating Systems')
        ])

        # Seed Course Outcomes
        cursor.executemany("""
            INSERT INTO course_outcomes (co_id, course_id, co_number, co_description)
            VALUES (?, ?, ?, ?)
        """, [
            (1, 1, 'CO1', 'Understand relational database concepts and ER modeling'),
            (2, 1, 'CO2', 'Formulate complex queries using Structured Query Language (SQL)'),
            (3, 1, 'CO3', 'Apply database normalization to eliminate anomalies'),
            (4, 1, 'CO4', 'Understand transaction processing, concurrency, and ACID properties'),
            (5, 2, 'CO1', 'Understand OSI and TCP/IP protocol stack layers'),
            (6, 2, 'CO2', 'Analyze IP addressing, subnetting, and routing protocols')
        ])

        # Seed Students (CS301)
        students_data = [
            (1, 'CS202401', 'Aarav Sharma', 1),
            (2, 'CS202402', 'Neha Patil', 1),
            (3, 'CS202403', 'Rohan Kulkarni', 1),
            (4, 'CS202404', 'Pooja Iyer', 1),
            (5, 'CS202405', 'Aniket Verma', 1),
            (6, 'CS202406', 'Sneha Deshmukh', 1),
            (7, 'CS202407', 'Aditya Joshi', 1),
            (8, 'CS202408', 'Priya Nair', 1),
            (9, 'CS202409', 'Vikram Shinde', 1),
            (10, 'CS202410', 'Tanvi Mehta', 1)
        ]
        cursor.executemany("""
            INSERT INTO students (student_id, roll_no, student_name, course_id)
            VALUES (?, ?, ?, ?)
        """, students_data)

        # Seed Assessments
        cursor.executemany("""
            INSERT INTO assessments (assessment_id, course_id, co_id, assessment_name, max_marks)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (1, 1, 1, 'Unit Test 1 (CO1)', 20.0),
            (2, 1, 2, 'SQL Lab Test (CO2)', 25.0),
            (3, 1, 3, 'Normalization Assignment (CO3)', 30.0),
            (4, 1, 4, 'Unit Test 2 (CO4)', 20.0)
        ])

        # Seed Student Marks
        # UT1: Max 20, Target 12 (8/10 pass target = 80% Attainment -> Level 3)
        ut1_marks = [
            (1, 1, 16.0), (2, 1, 14.5), (3, 1, 18.0), (4, 1, 15.0), (5, 1, 13.0),
            (6, 1, 11.0), (7, 1, 17.5), (8, 1, 10.0), (9, 1, 15.5), (10, 1, 14.0)
        ]
        # SQL Lab: Max 25, Target 15 (7/10 pass target = 70% Attainment -> Level 3)
        sql_marks = [
            (1, 2, 22.0), (2, 2, 19.0), (3, 2, 24.0), (4, 2, 17.0), (5, 2, 12.0),
            (6, 2, 16.0), (7, 2, 20.0), (8, 2, 11.5), (9, 2, 13.0), (10, 2, 18.5)
        ]
        # Normalization: Max 30, Target 18 (6/10 pass target = 60% Attainment -> Level 2)
        norm_marks = [
            (1, 3, 25.0), (2, 3, 21.0), (3, 3, 27.0), (4, 3, 16.0), (5, 3, 14.0),
            (6, 3, 19.5), (7, 3, 22.0), (8, 3, 15.0), (9, 3, 12.5), (10, 3, 20.0)
        ]
        # UT2: Max 20, Target 12 (5/10 pass target = 50% Attainment -> Level 1)
        ut2_marks = [
            (1, 4, 15.0), (2, 4, 13.0), (3, 4, 16.5), (4, 4, 10.0), (5, 4, 11.0),
            (6, 4, 14.0), (7, 4, 12.5), (8, 4, 9.0), (9, 4, 8.5), (10, 4, 11.5)
        ]

        all_marks = ut1_marks + sql_marks + norm_marks + ut2_marks
        cursor.executemany("""
            INSERT INTO student_marks (student_id, assessment_id, obtained_marks)
            VALUES (?, ?, ?)
        """, all_marks)

    conn.commit()
    conn.close()


# Enable CORS
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# ==========================================================
# 1. Main Page Route
# ==========================================================
@app.route('/')
def home():
    """Serves the frontend.html page directly from current directory."""
    html_file = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(html_file):
        return send_file(html_file)
    return "frontend.html not found in project directory.", 404


# ==========================================================
# 2. Database Status Route
# ==========================================================
@app.route('/api/status', methods=['GET'])
def check_status():
    """Returns database connectivity and table statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS count FROM courses")
        courses_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM course_outcomes")
        cos_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM students")
        students_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM assessments")
        assessments_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM student_marks")
        marks_count = cursor.fetchone()['count']

        conn.close()

        return jsonify({
            'connected': True,
            'message': 'Connected to Course Outcome Database successfully (Active)',
            'stats': {
                'courses': courses_count,
                'cos': cos_count,
                'students': students_count,
                'assessments': assessments_count,
                'marks': marks_count
            }
        })
    except Exception as e:
        return jsonify({'connected': False, 'message': str(e)}), 200


# ==========================================================
# 3. Course Management Routes
# ==========================================================
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Fetches all courses."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_id, course_code, course_name FROM courses ORDER BY course_code ASC")
        rows = cursor.fetchall()
        courses = [dict(r) for r in rows]
        conn.close()
        return jsonify({'success': True, 'data': courses})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 200


@app.route('/api/courses', methods=['POST'])
def add_course():
    """Adds a new course."""
    data = request.get_json() or {}
    course_code = data.get('course_code', '').strip().upper()
    course_name = data.get('course_name', '').strip()

    if not course_code or not course_name:
        return jsonify({'success': False, 'message': 'Course Code and Course Name are required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (course_code, course_name) VALUES (?, ?)", (course_code, course_name))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Course added successfully.', 'course_id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error: {str(e)}"}), 400


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Deletes a course and related records."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Course deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ==========================================================
# 4. Course Outcomes Management Routes
# ==========================================================
@app.route('/api/course-outcomes', methods=['GET'])
def get_course_outcomes():
    """Fetches course outcomes. Can be filtered by course_id."""
    course_id = request.args.get('course_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if course_id:
            query = """
                SELECT co.co_id, co.course_id, co.co_number, co.co_description,
                       c.course_code, c.course_name
                FROM course_outcomes co
                JOIN courses c ON co.course_id = c.course_id
                WHERE co.course_id = ?
                ORDER BY co.co_number ASC
            """
            cursor.execute(query, (course_id,))
        else:
            query = """
                SELECT co.co_id, co.course_id, co.co_number, co.co_description,
                       c.course_code, c.course_name
                FROM course_outcomes co
                JOIN courses c ON co.course_id = c.course_id
                ORDER BY c.course_code ASC, co.co_number ASC
            """
            cursor.execute(query)

        rows = cursor.fetchall()
        cos = [dict(r) for r in rows]
        conn.close()
        return jsonify({'success': True, 'data': cos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 200


@app.route('/api/course-outcomes', methods=['POST'])
def add_course_outcome():
    """Adds a new course outcome."""
    data = request.get_json() or {}
    course_id = data.get('course_id')
    co_number = data.get('co_number', '').strip().upper()
    co_description = data.get('co_description', '').strip()

    if not course_id or not co_number or not co_description:
        return jsonify({'success': False, 'message': 'Course, CO Number, and Description are required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO course_outcomes (course_id, co_number, co_description)
            VALUES (?, ?, ?)
        """, (course_id, co_number, co_description))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Course Outcome added successfully.', 'co_id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/course-outcomes/<int:co_id>', methods=['DELETE'])
def delete_course_outcome(co_id):
    """Deletes a course outcome."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_outcomes WHERE co_id = ?", (co_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Course Outcome deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ==========================================================
# 5. Student Management Routes
# ==========================================================
@app.route('/api/students', methods=['GET'])
def get_students():
    """Fetches students with course details. Can be filtered by course_id."""
    course_id = request.args.get('course_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if course_id:
            query = """
                SELECT s.student_id, s.roll_no, s.student_name, s.course_id,
                       c.course_code, c.course_name
                FROM students s
                JOIN courses c ON s.course_id = c.course_id
                WHERE s.course_id = ?
                ORDER BY s.roll_no ASC
            """
            cursor.execute(query, (course_id,))
        else:
            query = """
                SELECT s.student_id, s.roll_no, s.student_name, s.course_id,
                       c.course_code, c.course_name
                FROM students s
                JOIN courses c ON s.course_id = c.course_id
                ORDER BY c.course_code ASC, s.roll_no ASC
            """
            cursor.execute(query)

        rows = cursor.fetchall()
        students = [dict(r) for r in rows]
        conn.close()
        return jsonify({'success': True, 'data': students})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 200


@app.route('/api/students', methods=['POST'])
def add_student():
    """Adds a new student."""
    data = request.get_json() or {}
    roll_no = data.get('roll_no', '').strip().upper()
    student_name = data.get('student_name', '').strip()
    course_id = data.get('course_id')

    if not roll_no or not student_name or not course_id:
        return jsonify({'success': False, 'message': 'Roll Number, Student Name, and Course are required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (roll_no, student_name, course_id) VALUES (?, ?, ?)",
                       (roll_no, student_name, course_id))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Student added successfully.', 'student_id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Deletes a student."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Student deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ==========================================================
# 6. Assessment Management Routes
# ==========================================================
@app.route('/api/assessments', methods=['GET'])
def get_assessments():
    """Fetches assessments. Can be filtered by course_id."""
    course_id = request.args.get('course_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if course_id:
            query = """
                SELECT a.assessment_id, a.course_id, a.co_id, a.assessment_name, a.max_marks,
                       c.course_code, c.course_name,
                       co.co_number, co.co_description
                FROM assessments a
                JOIN courses c ON a.course_id = c.course_id
                JOIN course_outcomes co ON a.co_id = co.co_id
                WHERE a.course_id = ?
                ORDER BY a.assessment_id ASC
            """
            cursor.execute(query, (course_id,))
        else:
            query = """
                SELECT a.assessment_id, a.course_id, a.co_id, a.assessment_name, a.max_marks,
                       c.course_code, c.course_name,
                       co.co_number, co.co_description
                FROM assessments a
                JOIN courses c ON a.course_id = c.course_id
                JOIN course_outcomes co ON a.co_id = co.co_id
                ORDER BY c.course_code ASC, a.assessment_id ASC
            """
            cursor.execute(query)

        rows = cursor.fetchall()
        assessments = [dict(r) for r in rows]
        conn.close()
        return jsonify({'success': True, 'data': assessments})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 200


@app.route('/api/assessments', methods=['POST'])
def add_assessment():
    """Adds a new assessment associated with a Course Outcome."""
    data = request.get_json() or {}
    course_id = data.get('course_id')
    co_id = data.get('co_id')
    assessment_name = data.get('assessment_name', '').strip()
    max_marks = data.get('max_marks')

    if not course_id or not co_id or not assessment_name or max_marks is None:
        return jsonify({'success': False, 'message': 'Course, CO, Assessment Name, and Maximum Marks are required.'}), 400

    try:
        max_marks = float(max_marks)
        if max_marks <= 0:
            return jsonify({'success': False, 'message': 'Maximum Marks must be greater than zero.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Maximum Marks must be a number.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessments (course_id, co_id, assessment_name, max_marks)
            VALUES (?, ?, ?, ?)
        """, (course_id, co_id, assessment_name, max_marks))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Assessment added successfully.', 'assessment_id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/assessments/<int:assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    """Deletes an assessment."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assessments WHERE assessment_id = ?", (assessment_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Assessment deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ==========================================================
# 7. Student Marks Management Routes
# ==========================================================
@app.route('/api/marks', methods=['GET'])
def get_marks():
    """Fetches student marks filtered by assessment_id or course_id."""
    assessment_id = request.args.get('assessment_id')
    course_id = request.args.get('course_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if assessment_id:
            query = """
                SELECT sm.marks_id, sm.student_id, sm.assessment_id, sm.obtained_marks,
                       s.roll_no, s.student_name,
                       a.assessment_name, a.max_marks,
                       co.co_number
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                JOIN assessments a ON sm.assessment_id = a.assessment_id
                JOIN course_outcomes co ON a.co_id = co.co_id
                WHERE sm.assessment_id = ?
                ORDER BY s.roll_no ASC
            """
            cursor.execute(query, (assessment_id,))
        elif course_id:
            query = """
                SELECT sm.marks_id, sm.student_id, sm.assessment_id, sm.obtained_marks,
                       s.roll_no, s.student_name,
                       a.assessment_name, a.max_marks,
                       co.co_number
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                JOIN assessments a ON sm.assessment_id = a.assessment_id
                JOIN course_outcomes co ON a.co_id = co.co_id
                WHERE a.course_id = ?
                ORDER BY a.assessment_name ASC, s.roll_no ASC
            """
            cursor.execute(query, (course_id,))
        else:
            query = """
                SELECT sm.marks_id, sm.student_id, sm.assessment_id, sm.obtained_marks,
                       s.roll_no, s.student_name,
                       a.assessment_name, a.max_marks,
                       co.co_number
                FROM student_marks sm
                JOIN students s ON sm.student_id = s.student_id
                JOIN assessments a ON sm.assessment_id = a.assessment_id
                JOIN course_outcomes co ON a.co_id = co.co_id
                ORDER BY sm.marks_id DESC
                LIMIT 50
            """
            cursor.execute(query)

        rows = cursor.fetchall()
        marks = []
        for r in rows:
            m = dict(r)
            m['obtained_marks'] = float(m['obtained_marks'])
            m['max_marks'] = float(m['max_marks'])
            target_marks = round(0.60 * m['max_marks'], 2)
            m['target_marks'] = target_marks
            m['achieved_target'] = (m['obtained_marks'] >= target_marks)
            marks.append(m)

        conn.close()
        return jsonify({'success': True, 'data': marks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 200


@app.route('/api/marks', methods=['POST'])
def save_mark():
    """
    Saves or updates marks for a student in an assessment.
    Validates that obtained_marks <= max_marks and >= 0.
    """
    data = request.get_json() or {}
    student_id = data.get('student_id')
    assessment_id = data.get('assessment_id')
    obtained_marks = data.get('obtained_marks')

    if not student_id or not assessment_id or obtained_marks is None:
        return jsonify({'success': False, 'message': 'Student, Assessment, and Obtained Marks are required.'}), 400

    try:
        obtained_marks = float(obtained_marks)
        if obtained_marks < 0:
            return jsonify({'success': False, 'message': 'Obtained Marks cannot be negative.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Obtained Marks must be a number.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate against maximum marks
        cursor.execute("SELECT max_marks, assessment_name FROM assessments WHERE assessment_id = ?", (assessment_id,))
        asmt = cursor.fetchone()
        if not asmt:
            conn.close()
            return jsonify({'success': False, 'message': 'Assessment not found.'}), 404

        max_marks = float(asmt['max_marks'])
        if obtained_marks > max_marks:
            conn.close()
            return jsonify({
                'success': False,
                'message': f"Validation Error: Obtained marks ({obtained_marks}) cannot exceed Maximum Marks ({max_marks}) for {asmt['assessment_name']}."
            }), 400

        # Upsert: check if already entered
        cursor.execute("SELECT marks_id FROM student_marks WHERE student_id = ? AND assessment_id = ?",
                       (student_id, assessment_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE student_marks SET obtained_marks = ? WHERE marks_id = ?",
                           (obtained_marks, existing['marks_id']))
        else:
            cursor.execute("INSERT INTO student_marks (student_id, assessment_id, obtained_marks) VALUES (?, ?, ?)",
                           (student_id, assessment_id, obtained_marks))

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Marks saved successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/marks/<int:marks_id>', methods=['DELETE'])
def delete_mark(marks_id):
    """Deletes a student mark entry."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_marks WHERE marks_id = ?", (marks_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Marks entry deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ==========================================================
# 8. CO Attainment Calculation Route
# ==========================================================
@app.route('/api/co-attainment', methods=['GET'])
def get_co_attainment():
    """
    Calculates direct CO Attainment for all COs in a given course.
    Formula:
    - Target Marks = 60% of Maximum Marks
    - Students Achieving Target = Number of students scoring >= Target Marks
    - CO Attainment % = (Students Achieving Target / Total Students Evaluated) * 100
    - Levels: >= 70%: Level 3 | >= 60%: Level 2 | >= 50%: Level 1 | < 50%: Level 0
    """
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({'success': False, 'message': 'Course ID is required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get course details
        cursor.execute("SELECT course_id, course_code, course_name FROM courses WHERE course_id = ?", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            conn.close()
            return jsonify({'success': False, 'message': 'Course not found.'}), 404
        course = dict(course_row)

        # Get all COs for this course
        cursor.execute("""
            SELECT co_id, co_number, co_description
            FROM course_outcomes
            WHERE course_id = ?
            ORDER BY co_number ASC
        """, (course_id,))
        cos = [dict(r) for r in cursor.fetchall()]

        attainment_results = []

        for co in cos:
            co_id = co['co_id']

            # Find assessments mapped to this CO
            cursor.execute("""
                SELECT assessment_id, assessment_name, max_marks
                FROM assessments
                WHERE co_id = ?
            """, (co_id,))
            assessments = [dict(r) for r in cursor.fetchall()]

            assessment_names = [a['assessment_name'] for a in assessments]
            assessment_str = ", ".join(assessment_names) if assessment_names else "No Assessment Assigned"

            # Query marks for these assessments
            cursor.execute("""
                SELECT sm.obtained_marks, a.max_marks
                FROM student_marks sm
                JOIN assessments a ON sm.assessment_id = a.assessment_id
                WHERE a.co_id = ?
            """, (co_id,))
            marks_records = [dict(r) for r in cursor.fetchall()]

            total_evaluated = len(marks_records)
            students_achieving_target = 0

            for m in marks_records:
                obtained = float(m['obtained_marks'])
                max_m = float(m['max_marks'])
                target = 0.60 * max_m  # 60% Target
                if obtained >= target:
                    students_achieving_target += 1

            if total_evaluated > 0:
                attainment_pct = round((students_achieving_target / total_evaluated) * 100, 2)
                if attainment_pct >= 70.0:
                    level = 3
                elif attainment_pct >= 60.0:
                    level = 2
                elif attainment_pct >= 50.0:
                    level = 1
                else:
                    level = 0
            else:
                attainment_pct = 0.0
                level = 0

            attainment_results.append({
                'co_id': co['co_id'],
                'co_number': co['co_number'],
                'co_description': co['co_description'],
                'assessments': assessment_str,
                'total_students': total_evaluated,
                'students_achieved': students_achieving_target,
                'attainment_percentage': attainment_pct,
                'level': level
            })

        conn.close()
        return jsonify({
            'success': True,
            'course': course,
            'attainment': attainment_results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'attainment': []}), 200


# ==========================================================
# Run Flask Server & Auto-Open Browser with ONE Command
# ==========================================================
if __name__ == '__main__':
    print("==========================================================")
    print("Course Outcome Management System (COMS)")
    print("Initializing Database & Sample Data...")
    init_database()
    print("Database ready! Starting web server on http://127.0.0.1:5000")
    print("Opening browser automatically...")
    print("Press CTRL+C to stop the server.")
    print("==========================================================")

    # Automatically launch default browser to the web app
    threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:5000')).start()

    # Start Flask server
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
