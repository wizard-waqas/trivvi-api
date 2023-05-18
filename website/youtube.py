""" parse text from a youtube videos transcript """
import re

from flask import Blueprint, make_response, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

youtube = Blueprint("youtube", __name__)


@youtube.route("/<vid>")
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
