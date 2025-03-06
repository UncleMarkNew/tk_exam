import sqlite3
from contextlib import contextmanager
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection_pool = []
        return cls._instance
    
    def get_connection(self):
        if not self.connection_pool:
            conn = sqlite3.connect('exams.db')
            conn.row_factory = sqlite3.Row
            self.connection_pool.append(conn)
        return self.connection_pool[0]
    
    def close_all(self):
        for conn in self.connection_pool:
            conn.close()
        self.connection_pool.clear()

@contextmanager
def get_db_connection():
    db = DatabaseConnection()
    conn = db.get_connection()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        conn.commit()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 原始试卷表
        cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            year INTEGER,
            month INTEGER,
            level INTEGER,
            exam_type TEXT,
            is_real BOOLEAN,
            has_analysis BOOLEAN,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            file_type TEXT,
            status TEXT DEFAULT 'pending',
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 整理好的试题表
        cursor.execute('''CREATE TABLE IF NOT EXISTS processed_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question_number TEXT NOT NULL,
            content TEXT NOT NULL,
            question_type TEXT,
            options TEXT,
            correct_answer TEXT,
            analysis TEXT,
            processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams (id))''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exam_year ON exams(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exam_type ON exams(exam_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_question_exam_id ON processed_questions(exam_id)')
        
        logger.info("Database initialized successfully")

def save_exam(title, subject, year, month, level, exam_type, is_real, has_analysis, file_path, file_type):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exams (
                title, subject, year, month, level, exam_type, 
                is_real, has_analysis, file_path, file_type, 
                upload_date, last_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, subject, year, month, level, exam_type,
            is_real, has_analysis, file_path, file_type,
            datetime.now(), datetime.now()
        ))
        exam_id = cursor.lastrowid
        logger.info(f"Saved exam with ID: {exam_id}")
        return exam_id

def save_processed_question(exam_id, question_number, content, question_type=None, options=None, correct_answer=None, analysis=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO processed_questions (
                exam_id, question_number, content, question_type,
                options, correct_answer, analysis,
                processed_date, last_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exam_id, question_number, content, question_type,
            options, correct_answer, analysis,
            datetime.now(), datetime.now()
        ))
        logger.info(f"Saved processed question for exam ID: {exam_id}")

def get_exams(filters=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM exams'
        params = []
        
        if filters:
            conditions = []
            if 'year' in filters:
                conditions.append('year = ?')
                params.append(filters['year'])
            if 'exam_type' in filters:
                conditions.append('exam_type = ?')
                params.append(filters['exam_type'])
            if 'level' in filters:
                conditions.append('level = ?')
                params.append(filters['level'])
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY upload_date DESC'
        cursor.execute(query, params)
        exams = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Retrieved {len(exams)} exams")
        return exams

def get_exam_details(exam_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
        exam = dict(cursor.fetchone())
        
        cursor.execute('SELECT * FROM processed_questions WHERE exam_id = ? ORDER BY question_number', (exam_id,))
        questions = [dict(row) for row in cursor.fetchall()]
        
        logger.info(f"Retrieved exam details for ID: {exam_id}")
        return exam, questions

def update_exam_status(exam_id, status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE exams 
            SET status = ?, last_modified = ? 
            WHERE id = ?
        ''', (status, datetime.now(), exam_id))
        logger.info(f"Updated exam status to {status} for ID: {exam_id}")

def delete_exam(exam_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM processed_questions WHERE exam_id = ?', (exam_id,))
        cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
        logger.info(f"Deleted exam with ID: {exam_id}")

# 清理数据库连接
import atexit
atexit.register(DatabaseConnection().close_all)