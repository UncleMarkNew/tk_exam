import re
import PyPDF2
import docx
import logging
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QuestionType:
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN = "fill_in"
    PROGRAMMING = "programming"
    TEXT = "text"

def detect_file_type(filename: str) -> str:
    lower_filename = filename.lower()
    if lower_filename.endswith('.pdf'): return 'pdf'
    elif lower_filename.endswith('.docx'): return 'docx'
    elif lower_filename.endswith('.doc'): return 'doc'
    elif lower_filename.endswith('.txt'): return 'txt'
    return 'unknown'

def parse_exam_file(file_path: str, file_type: str) -> Dict[str, List[Dict[str, Any]]]:
    try:
        if file_type == 'pdf':
            questions = parse_pdf_file(file_path)
        elif file_type in ['docx', 'doc']:
            questions = parse_word_file(file_path)
        elif file_type == 'txt':
            questions = parse_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        logger.info(f"Successfully parsed {len(questions)} questions from {file_path}")
        return {'questions': questions}
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {str(e)}")
        raise

def extract_options(text: str) -> Optional[Dict[str, str]]:
    """从文本中提取选项"""
    options = {}
    option_pattern = r'([A-D])[\.、\s]+([^\n]+)'
    matches = re.finditer(option_pattern, text)
    for match in matches:
        options[match.group(1)] = match.group(2).strip()
    return options if options else None

def detect_question_type(text: str, options: Optional[Dict[str, str]] = None) -> str:
    """检测题目类型"""
    if options:
        # 根据选项数量判断是单选还是多选
        return QuestionType.SINGLE_CHOICE if len(options) <= 4 else QuestionType.MULTIPLE_CHOICE
    elif re.search(r'编程题|程序题|代码题', text):
        return QuestionType.PROGRAMMING
    elif re.search(r'填空题|填写', text):
        return QuestionType.FILL_IN
    else:
        return QuestionType.TEXT

def parse_question(text: str) -> Dict[str, Any]:
    """解析单个题目"""
    try:
        # 提取题号
        number_match = re.match(r'(\d+[\.\、])', text)
        if not number_match:
            return None
        
        question_number = number_match.group(1).rstrip('.、')
        question_content = text[len(number_match.group(0)):].strip()
        
        # 提取选项（如果有）
        options = extract_options(question_content)
        if options:
            # 如果有选项，从内容中移除选项部分
            question_content = re.sub(r'[A-D][\.、\s]+[^\n]+\n?', '', question_content).strip()
        
        # 检测题目类型
        question_type = detect_question_type(question_content, options)
        
        return {
            'number': question_number,
            'text': question_content,
            'type': question_type,
            'options': json.dumps(options) if options else None
        }
    except Exception as e:
        logger.error(f"Error parsing question: {str(e)}")
        return None

def parse_pdf_file(file_path: str) -> List[Dict[str, Any]]:
    questions = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # 使用更健壮的题目分割模式
            question_pattern = r'(?:^|\n)(\d+[\.\、][^\n]*(?:\n(?!\d+[\.\、])[^\n]*)*)'
            matches = re.finditer(question_pattern, text, re.MULTILINE)
            
            for match in matches:
                question_text = match.group(1).strip()
                parsed = parse_question(question_text)
                if parsed:
                    questions.append(parsed)
                    
        logger.info(f"Successfully parsed {len(questions)} questions from PDF file")
    except Exception as e:
        logger.error(f"Error parsing PDF file: {str(e)}")
        raise
    
    return questions

def parse_word_file(file_path: str) -> List[Dict[str, Any]]:
    questions = []
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # 使用更健壮的题目分割模式
        question_pattern = r'(?:^|\n)(\d+[\.\、][^\n]*(?:\n(?!\d+[\.\、])[^\n]*)*)'
        matches = re.finditer(question_pattern, text, re.MULTILINE)
        
        for match in matches:
            question_text = match.group(1).strip()
            parsed = parse_question(question_text)
            if parsed:
                questions.append(parsed)
                
        logger.info(f"Successfully parsed {len(questions)} questions from Word file")
    except Exception as e:
        logger.error(f"Error parsing Word file: {str(e)}")
        raise
    
    return questions

def parse_text_file(file_path: str) -> List[Dict[str, Any]]:
    questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
            # 使用更健壮的题目分割模式
            question_pattern = r'(?:^|\n)(\d+[\.\、][^\n]*(?:\n(?!\d+[\.\、])[^\n]*)*)'
            matches = re.finditer(question_pattern, text, re.MULTILINE)
            
            for match in matches:
                question_text = match.group(1).strip()
                parsed = parse_question(question_text)
                if parsed:
                    questions.append(parsed)
                    
        logger.info(f"Successfully parsed {len(questions)} questions from text file")
    except Exception as e:
        logger.error(f"Error parsing text file: {str(e)}")
        raise
    
    return questions