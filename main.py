from flask import Flask, make_response, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
from PyPDF2 import PdfReader
import docx2txt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def convert_pdf_to_txt(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    text = text.replace("\n", "")
    text = text.replace("  ", " ")

    return text


def convert_docx_to_txt(file):
    text = docx2txt.process(file)
    text = text.replace("\n", "")
    text = text.replace("  ", " ")
    return text


# This function will take a file and convert it to text and return it
@app.route("/api/parsepdf", methods=["POST"])
def convert():
    try:
        uploaded_file = request.files[
            "file"
        ]  # <- Make sure to put the name as "file" in the request/form

        if uploaded_file.filename == "":
            return make_response("No file selected", 400)

        if uploaded_file.filename.endswith(".pdf"):
            text = convert_pdf_to_txt(uploaded_file)
            return make_response(jsonify(text), 200)
        elif uploaded_file.filename.endswith(
                ".docx"
        ) or uploaded_file.filename.endswith(".doc"):
            text = convert_docx_to_txt(uploaded_file)
            return make_response(jsonify(text), 200)
        else:
            return make_response("File not supported", 400)
    except Exception as e:
        return make_response("Error", 400)


@app.route("/api/youtube/<vid>")
def about(vid):
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(vid)
        transcript = transcripts.find_generated_transcript(["en"])
        text = TextFormatter().format_transcript(transcript.fetch())

        # Removing [Music] [Applause] etc from the text using regex and the text has a \n at each line
        text = re.sub(r"\[.*?\]", "", text)
        text = text.replace("\n", " ")
        return make_response(jsonify(text), 200)
    except Exception as e:
        return make_response("Transcript Not Found", 404)


if __name__ == '__main__':
    app.run()
