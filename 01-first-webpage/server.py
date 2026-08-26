from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
from uuid import uuid4
from storage import (
    add_message,
    conversation_exists,
    create_conversation,
    get_messages,
    initialize_database,
    message_count,
)
from model_client import ModelConfigurationError, generate


DICTIONARY = {
    "gehen": {
        "meaning": "去；走",
        "partOfSpeech": "动词",
        "example": "Ich gehe nach Hause。（我回家。）",
    },
    "lernen": {
        "meaning": "学习",
        "partOfSpeech": "动词",
        "example": "Ich lerne Deutsch。（我学习德语。）",
    },
}
def decide_intent(message):
    text = message.lower()
    if any(keyword in text for keyword in ["对话", "练习", "餐厅", "conversation"]):
        return "conversation"
    if any(keyword in text for keyword in ["语法", "grammar", "satz"]):
        return "grammar"
    return "lookup"


def explain_grammar(message):
    return {
        "topic": "德语语法入门",
        "explanation": "先找出句子的主语、动词和宾语，再观察动词在句子中的位置。",
        "exercise": "请写一句包含 gehen 的德语句子。",
    }


def lookup_word(word):
    return DICTIONARY.get(word.lower())


def practice_conversation(message):
    conversation_id = str(uuid4())
    opening = "Guten Tag. Was möchten Sie bestellen?"
    create_conversation(conversation_id, "餐厅点餐", opening)
    return {
        "conversation_id": conversation_id,
        "scene": "餐厅点餐",
        "role": "你是顾客，我是服务员。",
        "opening": opening,
        "hint": "你可以回答：Ich möchte eine Suppe, bitte.",
    }


def continue_conversation(conversation_id, message):
    if not conversation_exists(conversation_id):
        return {"error": "会话不存在，请重新开始场景对话。"}

    add_message(conversation_id, "user", message)
    history = get_messages(conversation_id)
    model_messages = [
        {
            "role": "system",
            "content": (
                "Du bist ein freundlicher Deutschlehrer. Führe ein Restaurantgespräch "
                "auf Deutsch auf A2-Niveau. Antworte kurz und korrigiere Fehler sanft."
            ),
        },
        *history,
    ]
    try:
        reply = generate(model_messages)
    except (ModelConfigurationError, OSError, KeyError, ValueError):
        if "suppe" in message.lower():
            reply = "Sehr gern. Möchten Sie auch etwas trinken?"
        else:
            reply = "Danke. Können Sie das bitte noch einmal sagen?"
    add_message(conversation_id, "assistant", reply)
    return {
        "conversation_id": conversation_id,
        "reply": reply,
        "turns": message_count(conversation_id),
        "history": get_messages(conversation_id),
    }


def chat(message, conversation_id=None, level="A2"):
    if not conversation_id:
        conversation_id = str(uuid4())
        create_conversation(conversation_id, "普通聊天", "")
    elif not conversation_exists(conversation_id):
        return {"error": "聊天会话不存在，请重新开始。"}

    add_message(conversation_id, "user", message)
    history = get_messages(conversation_id)
    model_messages = [
        {
            "role": "system",
            "content": (
                f"你是一个友好的德语学习教练。学习者等级是 {level}。"
                "可以用中文解释，但练习时优先使用德语。"
                "发现语法错误时，先自然回应，再温和地纠正。"
                f"请按照 {level} 的词汇和句子复杂度回答。"
            ),
        },
        *history,
    ]
    try:
        reply = generate(model_messages)
    except Exception as error:
        return {"error": f"模型调用失败：{error.__class__.__name__}"}

    add_message(conversation_id, "assistant", reply)
    return {
        "conversation_id": conversation_id,
        "reply": reply,
        "history": get_messages(conversation_id),
    }


class GermanLearnerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlparse(self.path)

        if request.path == "/api/agent":
            message = parse_qs(request.query).get("message", [""])[0].strip()
            intent = decide_intent(message)
            if intent == "grammar":
                tool = "grammar_explainer"
                result = explain_grammar(message)
            elif intent == "conversation":
                tool = "conversation_practice"
                result = practice_conversation(message)
            else:
                tool = "dictionary_lookup"
                word = message.split()[-1] if message else ""
                result = lookup_word(word)
                if result is None:
                    result = {"error": f"暂时没有找到“{word}”"}

            self.send_json({"message": message, "intent": intent, "tool": tool, "result": result})
            return

        if request.path == "/api/conversation":
            query = parse_qs(request.query)
            conversation_id = query.get("session", [""])[0]
            message = query.get("message", [""])[0].strip()
            self.send_json(continue_conversation(conversation_id, message))
            return

        if request.path == "/api/chat":
            query = parse_qs(request.query)
            conversation_id = query.get("session", [""])[0] or None
            message = query.get("message", [""])[0].strip()
            level = query.get("level", ["A2"])[0].upper()
            if level not in {"A1", "A2", "B1"}:
                level = "A2"
            if not message:
                self.send_json({"error": "消息不能为空。"}, status=400)
                return
            result = chat(message, conversation_id, level)
            self.send_json(result, status=500 if "error" in result else 200)
            return

        if request.path != "/api/lookup":
            self.send_json({"error": "接口不存在"}, status=404)
            return

        word = parse_qs(request.query).get("word", [""])[0].strip().lower()
        entry = DICTIONARY.get(word)

        if entry is None:
            self.send_json({"error": f"暂时没有找到“{word}”"}, status=404)
            return

        self.send_json({"word": word, **entry})

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    initialize_database()
    server = HTTPServer(("127.0.0.1", 8001), GermanLearnerHandler)
    print("German Learner API: http://127.0.0.1:8001")
    server.serve_forever()
