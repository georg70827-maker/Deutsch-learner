from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
from uuid import uuid4
from storage import (
    add_message,
    conversation_exists,
    create_conversation,
    initialize_database,
    message_count,
)


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
    if "suppe" in message.lower():
        reply = "Sehr gern. Möchten Sie auch etwas trinken?"
    else:
        reply = "Danke. Können Sie das bitte noch einmal sagen?"
    add_message(conversation_id, "assistant", reply)
    return {"conversation_id": conversation_id, "reply": reply, "turns": message_count(conversation_id)}


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
