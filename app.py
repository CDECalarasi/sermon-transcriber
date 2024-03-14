import time
import logging
import os
from flask import Flask, request
from flask.views import MethodView
from summarizer import Summarizer
from transcriber import Transcriber

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

logging.debug("The log level is set to: " + LOGLEVEL)

app = Flask(__name__)


class TranscribeView(MethodView):

    def __init__(self):
        self.summarizer = Summarizer()
        self.logger = logging.getLogger(__name__)

    def post(self):
        _start_time = time.time()
        self.logger.info("Transcribing audio")
        json_data = request.form or request.get_json()
        data = dict(json_data)

        self.logger.debug(f"Received data: {data}")

        # Get the audio file
        audio_file = data.get("webContentLink")
        file_name = data.get("name")
        md5 = data.get("md5Checksum")

        transcriber = Transcriber(md5)

        transcript = transcriber.transcribe(audio_file, file_name)

        # Summarize the transcript
        summary = self.summarizer.summarize(transcript)

        _end_time = time.time()

        results = {
            "transcript": transcript,
            "summary": summary,
            "time_taken": _end_time - _start_time,
        }

        return results


app.add_url_rule('/transcribe', view_func=TranscribeView.as_view('transcribe'))


@app.route('/health', methods=['GET'])
def health_check():
    result = {
        "status": "ok",
        "timestamp": time.time()
    }

    return result


@app.route('/', methods=['GET'])
def home():
    return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
