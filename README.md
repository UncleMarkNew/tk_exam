# 试卷处理系统

一个基于 Python 的试卷处理系统，支持多种格式试卷的上传、解析和自动答题。

## 功能特点

- 支持 PDF、Word(docx/doc)、TXT 格式的试卷文件
- 自动识别和解析试题
- 使用 LLM (Deepseek) 进行智能解答
- 图形用户界面，操作简单直观
- SQLite 数据库存储，方便管理

## 技术栈

- Python 3.x
- tkinter (GUI)
- SQLite3 (数据库)
- PyPDF2 (PDF解析)
- python-docx (Word文档解析)
- Deepseek API (LLM服务)

## 安装

1. 克隆仓库
```bash
git clone [repository-url]
cd tk_exam
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建 `.env` 文件并添加以下内容：
```
DEEPSEEK_API_KEY=your_api_key_here
```

4. 运行程序
```bash
python app.py
```

## 使用说明

1. 启动程序后，可以看到主界面
2. 选择试卷年份、月份、级别和类型
3. 点击"上传试卷"选择要处理的试卷文件
4. 上传后可以在预览标签页查看原始内容
5. 点击"整理试题"进行试题解析
6. 点击"生成答案"获取 AI 解答结果

## 注意事项

- 确保已正确配置 Deepseek API Key
- 上传文件大小建议不超过 10MB
- 目前仅支持文本格式的试题，不支持图片试题
- 答案生成可能需要一定时间，请耐心等待
