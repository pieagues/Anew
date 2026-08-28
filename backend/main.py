from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypinyin import lazy_pinyin, Style
from snownlp import SnowNLP
import json
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
)

profile = {
    "heroTitle": "关于我",
    "heroSubtitle": "项目，创意，灵感，心得，我的作品",
    "featuredWork": {
        "kicker": "作品",
        "title": "文字实验室",
        "copy": "拼音和情绪，挖掘中文里的细节",
        "linkLabel": "打开作品",
    },
    "identity": {
        "motto": "已识乾坤大，犹怜草木青",
        "learning": "零到全栈",
    },
}

class AnalyzeRequest(BaseModel):
    text: str

HISTORY_FILE = "history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_record(record):
    records = load_history()
    records.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def score_label(score):
    if score > 0.6:
        return "偏积极"
    elif score < 0.4:
        return "偏消极"
    else:
        return "偏平静"

@app.get("/api/profile")
def get_profile():
    return profile

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    text = req.text
    score = round(SnowNLP(text).sentiments, 2)
    result = {
        "text": text,
        "score": score,
        "label": score_label(score),
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_record(result)
    return result

@app.get("/api/history")
def history():
    records = load_history()
    records.reverse()
    return records[:10]