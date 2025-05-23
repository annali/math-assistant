# ai_engine.py
import requests

def call_gemma_chat(user_message):
    url = "http://192.168.168.58:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "gemma-3-12b-it",
        "messages": [
            {"role": "system", "content": "你是一位高中數學老師，請使用繁體中文回答。"},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 2048,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print("🧠 Chat 回傳 JSON：", data)  # ← 保留觀察格式

        # ✅ 正確取得 content
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Chat 模式失敗：", e)
        return "[錯誤] 無法取得 Chat 模型回應"



def build_prompt(student_answer):
    return f"""
你是一位高中數學老師，請你幫我批改以下學生作業內容：

=== 學生作業開始 ===
{student_answer}
=== 學生作業結束 ===

請你針對以下三點給出評語與建議：
1. 概念理解程度
2. 計算過程正確性
3. 錯誤修正建議與未來學習方向
請用條列方式回覆，並以繁體中文回答。
"""
