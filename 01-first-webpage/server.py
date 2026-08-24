from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json


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


class GermanLearnerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlparse(self.path)

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
    server = HTTPServer(("127.0.0.1", 8001), GermanLearnerHandler)
    print("German Learner API: http://127.0.0.1:8001")
    server.serve_forever()
