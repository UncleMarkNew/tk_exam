import sqlite3

def init_db():
    conn = sqlite3.connect('exams.db')
    cursor = conn.cursor()
    
    # 原始试卷表
    cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_path TEXT,
        file_type TEXT)''')
    
    # 整理好的试题表
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        content TEXT NOT NULL,
        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exam_id) REFERENCES exams (id))''')
    
    conn.commit()
    conn.close()

def save_exam(title, subject, file_path, file_type):
    conn = sqlite3.connect('exams.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO exams (title, subject, file_path, file_type) VALUES (?, ?, ?, ?)',
                   (title, subject, file_path, file_type))
    exam_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exam_id

def save_processed_question(exam_id, content):
    conn = sqlite3.connect('exams.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO processed_questions (exam_id, content) VALUES (?, ?)',
                   (exam_id, content))
    conn.commit()
    conn.close()

def get_exams():
    conn = sqlite3.connect('exams.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exams ORDER BY upload_date DESC')
    exams = cursor.fetchall()
    conn.close()
    return exams

def get_exam_details(exam_id):
    conn = sqlite3.connect('exams.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
    exam = dict(cursor.fetchone())
    conn.close()
    return exam, []

def get_processed_questions(exam_id):
    conn = sqlite3.connect('exams.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM processed_questions WHERE exam_id = ? ORDER BY processed_date', (exam_id,))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions