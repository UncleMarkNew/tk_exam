import requests
from dotenv import load_dotenv
import os
import re

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_llm_answer(question_number, question_text):
    try:
        prompt = f"""
请回答以下试卷问题，题号为【{question_number}】。
问题: {question_text}
请按照以下格式回答:
题号: {question_number}
答案: [你的答案]
解析: [详细解释你的答案的过程和理由]
"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的试卷解答助手。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response_data = response.json()
        answer_text = response_data['choices'][0]['message']['content']
        
        answer_match = re.search(r'答案:(.*?)(?=解析:|$)', answer_text, re.DOTALL)
        explanation_match = re.search(r'解析:(.*?)$', answer_text, re.DOTALL)
        
        answer = answer_match.group(1).strip() if answer_match else ""
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        return {
            'answer': answer or answer_text,
            'explanation': explanation,
            'confidence': 0.9,
            'model': "deepseek-chat"
        }
    except Exception as e:
        return {
            'answer': f"题号 {question_number} - 无法获取答案",
            'explanation': f"发生错误: {str(e)}",
            'confidence': 0.0,
            'model': "error"
        }