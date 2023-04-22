""" parse text from a youtube videos transcript """

import docx2txt
from PyPDF2 import PdfReader
from flask import Blueprint
from flask import make_response, jsonify, request

parsepdf = Blueprint("parsepdf", __name__)


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
@app.route("/", methods=["POST"])
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
