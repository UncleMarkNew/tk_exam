import re
import PyPDF2
import docx

def detect_file_type(filename):
    lower_filename = filename.lower()
    if lower_filename.endswith('.pdf'): return 'pdf'
    elif lower_filename.endswith('.docx'): return 'docx'
    elif lower_filename.endswith('.doc'): return 'doc'
    elif lower_filename.endswith('.txt'): return 'txt'
    return 'unknown'

def parse_exam_file(file_path, file_type):
    questions = []
    if file_type == 'pdf':
        questions = parse_pdf_file(file_path)
    elif file_type in ['docx', 'doc']:
        questions = parse_word_file(file_path)
    elif file_type == 'txt':
        questions = parse_text_file(file_path)
    return {'questions': questions}

def parse_pdf_file(file_path):
    questions = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            question_pattern = r'(\d+[\.\、][^\d\.\、]+?)(?=\d+[\.\、]|$)'
            matches = re.finditer(question_pattern, text, re.DOTALL)
            for match in matches:
                question_text = match.group(1).strip()
                number_match = re.match(r'(\d+[\.\、])', question_text)
                if number_match:
                    question_number = number_match.group(1).rstrip('.、')
                    question_content = question_text[len(number_match.group(0)):].strip()
                    questions.append({'number': question_number, 'text': question_content, 'type': 'text'})
    except Exception as e:
        print(f"解析PDF文件时出错: {e}")
    return questions

def parse_word_file(file_path):
    questions = []
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        question_pattern = r'(\d+[\.\、][^\d\.\、]+?)(?=\d+[\.\、]|$)'
        matches = re.finditer(question_pattern, text, re.DOTALL)
        for match in matches:
            question_text = match.group(1).strip()
            number_match = re.match(r'(\d+[\.\、])', question_text)
            if number_match:
                question_number = number_match.group(1).rstrip('.、')
                question_content = question_text[len(number_match.group(0)):].strip()
                questions.append({'number': question_number, 'text': question_content, 'type': 'text'})
    except Exception as e:
        print(f"解析Word文件时出错: {e}")
    return questions

def parse_text_file(file_path):
    questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            question_pattern = r'(\d+[\.\、][^\d\.\、]+?)(?=\d+[\.\、]|$)'
            matches = re.finditer(question_pattern, text, re.DOTALL)
            for match in matches:
                question_text = match.group(1).strip()
                number_match = re.match(r'(\d+[\.\、])', question_text)
                if number_match:
                    question_number = number_match.group(1).rstrip('.、')
                    question_content = question_text[len(number_match.group(0)):].strip()
                    questions.append({'number': question_number, 'text': question_content, 'type': 'text'})
    except Exception as e:
        print(f"解析文本文件时出错: {e}")
    return questions