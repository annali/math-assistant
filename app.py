from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from utils_pdf import extract_text_from_pdf
from ai_engine import call_gemma_chat
import markdown
import os
from datetime import datetime
from urllib.parse import unquote  # ← 放在檔案上方

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 模擬資料庫的歷史記錄
history_records = []
feedback_cache = {}  # ← 儲存 feedback 供 result 顯示

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", history=reversed(history_records))

@app.route("/upload", methods=["POST"])
def upload():
    question = request.form.get("question", "").strip()
    file = request.files.get("file")
    parsed_text = ""

    if file and file.filename != "" and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        parsed_text = extract_text_from_pdf(filepath)
        if parsed_text:
            with open(f"{filepath}.txt", "w", encoding="utf-8") as f:
                f.write(parsed_text)
        else:
            parsed_text = "(無法解析 PDF 內容)"
    else:
        filename = f"問題-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    if not question and not parsed_text:
        return "請輸入問題或上傳PDF作業檔案"

    # Combine 問題與檔案內容
    full_text = ""
    if question:
        full_text += f"老師提問：{question}\n\n"
    if parsed_text:
        full_text += f"學生作業內容如下：\n{parsed_text}"

    # 呼叫 Chat 模型
    feedback = call_gemma_chat(full_text)

    # 模擬評分
    score = feedback.count("✔") * 10 + 60
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 儲存紀錄與回應
    history_records.append({
        "title": filename,
        "score": score,
        "time": now_str
    })
    feedback_cache[filename] = {"content": full_text, "feedback": feedback}

    return redirect(url_for("result", filename=filename))

import markdown  # ⬅ 加在頂部

@app.route("/result/<filename>")
def result(filename):
    if filename in feedback_cache:
        data = feedback_cache[filename]
        content = data["content"]
        feedback_raw = data["feedback"]
        feedback_html = markdown.markdown(feedback_raw, extensions=["fenced_code", "tables"])
    else:
        content = "(找不到原始資料)"
        feedback_html = "(找不到 AI 回應)"

    return render_template("result.html", filename=filename, content=content, feedback=feedback_html)

@app.route("/api/chat/<path:filename>")
def api_chat(filename):
    filename = unquote(filename)  # ← 解碼回原始名稱
    if filename in feedback_cache:
        data = feedback_cache[filename]
        content = data["content"]
        feedback_raw = data["feedback"]
        feedback_html = markdown.markdown(feedback_raw, extensions=["fenced_code", "tables"])
        return render_template("chat_detail.html", content=content, feedback=feedback_html)
    else:
        return "<div class='text-muted'>⚠️ 找不到該筆紀錄</div>"


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
