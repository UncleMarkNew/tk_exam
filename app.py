import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from db import init_db, save_exam, save_processed_question, get_exams, get_exam_details
import PyPDF2
import docx
from datetime import datetime
from storage import FileStorage
import shutil
import logging

# 设置日志
logger = logging.getLogger(__name__)

class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("试卷处理系统")
        
        # 初始化文件存储
        self.storage = FileStorage('uploads')
        
        # 初始化数据库
        init_db()
        
        # 设置窗口大小和位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = screen_width
        window_height = screen_height - 80
        self.root.geometry(f"{window_width}x{window_height}+0+0")
        
        # 创建主框架
        self.setup_main_frame()
        self.setup_upload_area()
        self.setup_exam_list()
        self.setup_detail_tabs()
        self.setup_action_buttons()
        
        # 加载试卷列表
        self.load_exams()
        
        # 设置进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, 
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=4, 
                             sticky=(tk.W, tk.E), pady=5)
        self.progress_bar.grid_remove()  # 默认隐藏
        
    def setup_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        for i in range(4):
            self.main_frame.columnconfigure(i, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
    
    def setup_upload_area(self):
        # 第一行
        ttk.Label(self.main_frame, text="试题年份:").grid(row=0, column=0, sticky=tk.W)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        years = [str(year) for year in range(2021, datetime.now().year + 2)]
        ttk.Combobox(self.main_frame, textvariable=self.year_var, 
                    values=years, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(self.main_frame, text="试题月份:").grid(row=0, column=2, sticky=tk.W)
        self.month_var = tk.StringVar(value="3")
        ttk.Combobox(self.main_frame, textvariable=self.month_var, 
                    values=["3", "6", "9", "12"], state="readonly").grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # 第二行
        ttk.Label(self.main_frame, text="试题级别:").grid(row=1, column=0, sticky=tk.W)
        self.level_var = tk.StringVar(value="1")
        ttk.Combobox(self.main_frame, textvariable=self.level_var, 
                    values=["1", "2", "3", "4", "5", "6", "7", "8"], state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(self.main_frame, text="试题类型:").grid(row=1, column=2, sticky=tk.W)
        self.type_var = tk.StringVar(value="Python")
        ttk.Combobox(self.main_frame, textvariable=self.type_var, 
                    values=["Python", "C++"], state="readonly").grid(row=1, column=3, sticky=(tk.W, tk.E))
        
        # 第三行
        self.real_var = tk.BooleanVar()
        ttk.Checkbutton(self.main_frame, text="真题", variable=self.real_var).grid(row=2, column=0, sticky=tk.W)
        
        self.analysis_var = tk.BooleanVar()
        ttk.Checkbutton(self.main_frame, text="解析", variable=self.analysis_var).grid(row=2, column=1, sticky=tk.W)
        
        # 上传按钮
        upload_btn = ttk.Button(self.main_frame, text="上传试卷", command=self.upload_exam)
        upload_btn.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E), pady=5)
    
    def setup_exam_list(self):
        # 试卷列表
        ttk.Label(self.main_frame, text="已上传的试卷:").grid(row=3, column=0, sticky=tk.W)
        self.exam_list = ttk.Treeview(self.main_frame, columns=("id", "title", "subject", "date"), show="headings")
        self.exam_list.heading("id", text="ID")
        self.exam_list.heading("title", text="标题")
        self.exam_list.heading("subject", text="科目")
        self.exam_list.heading("date", text="上传日期")
        self.exam_list.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))
    
    def setup_detail_tabs(self):
        # 详情显示（使用选项卡）
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=5, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.preview_tab = ttk.Frame(self.notebook)
        self.processed_tab = ttk.Frame(self.notebook)
        self.answer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="原始预览")
        self.notebook.add(self.processed_tab, text="整理试题")
        self.notebook.add(self.answer_tab, text="答案")
        
        self.preview_text = tk.Text(self.preview_tab, height=20, width=80)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        self.processed_text = tk.Text(self.processed_tab, height=20, width=80)
        self.processed_text.pack(fill=tk.BOTH, expand=True)
        
        self.answer_text = tk.Text(self.answer_tab, height=20, width=80)
        self.answer_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_action_buttons(self):
        # 按钮
        ttk.Button(self.main_frame, text="刷新列表", command=self.load_exams).grid(row=6, column=0, pady=5)
        ttk.Button(self.main_frame, text="预览试卷", command=self.preview_exam).grid(row=6, column=1, pady=5)
        ttk.Button(self.main_frame, text="整理试题", command=self.process_exam).grid(row=6, column=2, pady=5)
        ttk.Button(self.main_frame, text="生成答案", command=self.generate_answers).grid(row=6, column=3, pady=5)
    
    def load_exams(self):
        for item in self.exam_list.get_children():
            self.exam_list.delete(item)
        exams = get_exams()
        print(f"加载试卷列表: {len(exams)} 条记录")
        for exam in exams:
            self.exam_list.insert("", "end", values=exam)
    
    def detect_file_type(self, filename):
        lower_filename = filename.lower()
        if lower_filename.endswith('.pdf'): return 'pdf'
        elif lower_filename.endswith('.docx'): return 'docx'
        elif lower_filename.endswith('.doc'): return 'doc'
        elif lower_filename.endswith('.txt'): return 'txt'
        return 'unknown'
    
    def read_file_content(self, file_path, file_type):
        content = ""
        try:
            if file_type == 'pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
            elif file_type in ['docx', 'doc']:
                doc = docx.Document(file_path)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            elif file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            print(f"读取文件内容（前500字符）: {content[:500]}")
        except Exception as e:
            content = f"读取文件出错: {str(e)}"
            print(content)
        return content
    
    def upload_exam(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Supported files", "*.pdf *.docx *.doc *.txt")]
            )
            if not file_path:
                return
            
            # 获取文件信息
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].lower()
            
            # 保存文件到存储系统
            stored_path = self.storage.save_file(file_path)
            
            # 获取试卷信息
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            level = int(self.level_var.get())
            exam_type = self.type_var.get()
            title = f"{year}-{month}-{level}-{exam_type}"
            subject = f"真题: {self.real_var.get()}, 解析: {self.analysis_var.get()}"
            
            # 保存到数据库
            exam_id = save_exam(
                title=title,
                subject=subject,
                year=year,
                month=month,
                level=level,
                exam_type=exam_type,
                is_real=self.real_var.get(),
                has_analysis=self.analysis_var.get(),
                file_path=stored_path,
                file_type=file_type
            )
            
            # 刷新列表并显示预览
            self.load_exams()
            self.show_preview(exam_id, self.read_file_content(stored_path, file_type))
            messagebox.showinfo("成功", f"已上传试卷 {title}")
            
        except Exception as e:
            messagebox.showerror("错误", f"上传失败: {str(e)}")
            logger.error(f"Upload error: {str(e)}")
        finally:
            self.progress_bar.grid_remove()
    
    def show_preview(self, exam_id, content):
        self.preview_text.delete(1.0, tk.END)
        preview = f"试卷ID: {exam_id}\n\n{content}"
        self.preview_text.insert(tk.END, preview)
        self.notebook.select(self.preview_tab)
        self.root.update()
        print(f"原始预览: {preview[:100]}...")
    
    def preview_exam(self):
        try:
            selection = self.exam_list.selection()
            if not selection:
                messagebox.showwarning("提示", "请先选择一个试卷")
                return
                
            exam_id = self.exam_list.item(selection[0])['values'][0]
            exam, questions = get_exam_details(exam_id)
            
            if exam is None:
                messagebox.showerror("错误", "无法获取试卷详情")
                return
                
            preview_text = f"试卷ID: {exam['id']}\n\n"
            
            # 读取文件内容
            file_path = exam['file_path']
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # 只读取前500个字符
                    preview_text += f"原始预览: {content}..."
            else:
                preview_text += "原始文件不存在\n"
            
            if questions:
                preview_text += "\n\n处理后的题目:\n"
                for q in questions[:3]:  # 只显示前3个题目
                    preview_text += f"\n题号 {q['question_number']}: {q['content'][:100]}..."
            
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', preview_text)
        except Exception as e:
            logger.error(f"Error in preview_exam: {str(e)}")
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def process_exam(self):
        selected = self.exam_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个试卷")
            return
        
        exam_id = self.exam_list.item(selected[0])['values'][0]
        exam, _ = get_exam_details(exam_id)
        file_path = exam['file_path']
        file_type = exam['file_type']
        content = self.read_file_content(file_path, file_type)
        
        # 存入整理好的试题表（当前仅保存原始内容）
        save_processed_question(exam_id, content)
        
        self.processed_text.delete(1.0, tk.END)
        processed_content = f"试卷: {exam['title']} ({exam['subject']})\n整理时间: {exam['upload_date']}\n\n{content}"
        self.processed_text.insert(tk.END, processed_content)
        self.notebook.select(self.processed_tab)
        self.root.update()
        print(f"整理试题: {processed_content[:100]}...")
        messagebox.showinfo("成功", f"已整理试卷 {exam['title']} 的试题")
    
    def generate_answers(self):
        messagebox.showinfo("提示", "答案生成功能暂未实现，因为未解析问题。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()