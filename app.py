import time
from flask import Flask, request
from flask.views import MethodView

from summarizer import Summarizer
from transcriber import Transcriber

app = Flask(__name__)


class HealthCheckView(MethodView):
    def get(self):

        result = {
            "status": "ok",
            "timestamp": time.time()
        }

        return result


class TranscribeView(MethodView):

    def __init__(self):
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()

    def post(self):
        json_data = request.form or request.get_json()
        data = dict(json_data)

        # Get the audio file
        audio_file = data.get("webContentLink")

        transcript = self.transcriber.transcribe(audio_file)

        # Summarize the transcript
        summary = self.summarizer.summarize(transcript)

        results = {
            "transcript": transcript,
            "summary": summary
        }

        return results


app.add_url_rule('/transcribe', view_func=TranscribeView.as_view('transcribe'))
app.add_url_rule('/health', view_func=HealthCheckView.as_view('health'))

if __name__ == '__main__':
    app.run()
