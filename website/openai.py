import time
from flask import Blueprint, Response, request, jsonify, make_response, stream_template
import openai
import re

generate_quiz = Blueprint("generatequiz", __name__)
openai.api_key = "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"

JSON_FORMAT_MC = """{"query":"The question","answers":["A. Choice 1","B. Choice 2","C. Choice 3","D. Choice 4"],"answer_key":"The correct answer (A, B, C or D)"}"""
JSON_FORMAT_TF = """{"query":"The question","answers":["T","F"],"answer_key":"The correct answer (T or F)"}"""


@generate_quiz.post("/tf")
def generate_tf_question():
    """
    Generate a true or false quiz based on the information provided
    :return: JSON response following the schema of this variable: JSON_FORMAT_TF
    """
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    quizData = data.get("quizData")
    numberOfQuestions = data.get("numberOfQuestions")
    difficultyLevel = data.get("difficultyLevel")

    quizResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a true or false quiz with {numberOfQuestions} questions "
                f"based on this information: '{quizData}'. "
                f"The difficulty of the questions should be {difficultyLevel}. "
                f"Each question will have an answer of T or F, "
                f"do not write out the whole word only use the letter. "
                f"The format of each question should be as follows and nothing else:\n"
                "1. [insert question text]\n"
                "Answer: [insert T or F]\n",
            }
        ],
        max_tokens=2000,
        temperature=0.0,
    )

    quizResponseText = quizResponse.choices[0].message.content
    lines = quizResponseText.split("\n")

    questions = []
    answerKey = []

    current_question: any = {"query": ""}

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match(r"^[0-9]+", line):
            query_text = re.sub(r"^\d+\.\s*", "", line)  # remove the number and period
            current_question["query"] = query_text
        elif line.startswith("Answer"):
            answer = line.split(":")[1].strip()
            answerKey.append(answer)
            questions.append(current_question)
            current_question = {"query": ""}

    return jsonify({"questions": questions, "answerKey": answerKey}), 200


@generate_quiz.post("/mc")
def generate_mc_question():
    """
    Generate a multiple choice quiz based on the information provided
    :return: JSON response following the schema of this variable: JSON_FORMAT_MC
    """
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    quizData = data.get("quizData")
    numberOfQuestions = data.get("numberOfQuestions")
    difficultyLevel = data.get("difficultyLevel")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a multiple choice quiz with {numberOfQuestions} questions "
                f"based on this information: '{quizData}'. "
                f"The difficulty of the questions should be {difficultyLevel}. "
                f"The format of the Answer should be a single letter and nothing else.\n"
                f"The format of each question should be as follows and nothing else: "
                f"1. [insert question text]\n"
                f"A. [insert answer choice 1]\n"
                f"B. [insert answer choice 2]\n"
                f"C. [insert answer choice 3]\n"
                f"D. [insert answer choice 4]\n"
                f"Answer: [insert A B C or D]\n",
            }
        ],
        max_tokens=2000,
        temperature=0.0,
    )

    quiz_response_text = response.choices[0].message.content
    lines = quiz_response_text.split("\n")

    questions = []
    answer_key = []
    current_question = {"query": "", "answers": []}

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match(r"^[0-9]+", line):
            if current_question["query"]:
                questions.append(current_question)

            query_text = re.sub(r"^\d+\.\s*", "", line)  # remove the number and period
            current_question = {"query": query_text, "answers": []}
        elif line.startswith("Answer"):
            answer_key.append(line[-1])
        elif line[0] in ["A", "B", "C", "D"]:
            current_question["answers"].append(line)

    questions.append(current_question)

    return {"questions": questions, "answerKey": answer_key}


@generate_quiz.post("/key-points")
def generate_key_points():
    """
    Generate a list of key points based on the information provided
    CURRENTLY DEPRECATED
    """
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    number_of_key_points = data.get("numberOfKeyPoints")
    quiz_data = data.get("quizData")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a list of {number_of_key_points} key points based on this information: '{quiz_data}'",
            }
        ],
        max_tokens=2000,
        temperature=0.3,
    )

    lines = response.choices[0].message.content.split("\n")
    list_of_key_points = [
        re.sub(r"^\d+\.\s*", "", line) for line in lines
    ]  # remove number from beginning of line

    return {"keyPoints": list_of_key_points}


@generate_quiz.post("/summarize")
def summarize_text():
    """
    Summarize a text based on the information provided
    """
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    textData = data.get("textData")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Summarize the following text with context: '{textData}'",
            }
        ],
        max_tokens=2000,
        temperature=0.0,
    )

    summarized_text = response.choices[0].message.content
    return make_response(jsonify(summarized_text), 200)


@generate_quiz.post("/create-image")
def create_image():
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    image_query = data.get("imageQuery")

    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"DO NOT add any detail to this prompt, just use it AS-IS: Generate a profile picture without any letters in a flat and simple art style of {image_query}",
        size="1024x1024",
        quality="standard",
    )
    image_url = response["data"][0]["url"]
    return {"imageUrl": image_url}


@generate_quiz.post("/generate-quiz-stream")
def generate_quiz_as_stream():
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    if not request.data:
        return jsonify({"message": "Invalid JSON"}), 400

    data = request.json

    quizType = data.get("quizType")
    quizData = data.get("quizData")
    numberOfQuestions = data.get("numberOfQuestions")
    message = generate_quiz_prompt(quizType, numberOfQuestions, quizData)

    if not message:
        return jsonify({"message": "Invalid quiz type"}), 400

    return Response(
        event_stream(message),
        mimetype="text/event-stream",
        headers={"Connection": "keep-alive"},
    )


def generate_quiz_prompt(quizType, numberOfQuestions, quizData):
    quiz = ""
    jsonFormat = ""

    if quizType == "tf":
        quiz = "true and false"
        jsonFormat = JSON_FORMAT_TF
    elif quizType == "mc":
        quiz = "multiple choice"
        jsonFormat = JSON_FORMAT_MC
    else:
        return None

    return (
        f"Generate a {quiz} quiz with {numberOfQuestions} questions based on this information {quizData} and any supporting infomration you may need. "
        f"Each question must follow this format: {jsonFormat}. "
        f"The response should be these objects separated by a comma and nothing else."
    )


def event_stream(message):
    data = ""
    for line in generate_streamed_completion(message):
        text = line.choices[0].delta.get("content", "")

        if len(text):
            if "}" in text:
                split = text.split("}")
                data += split[0] + "}"
                data.replace("\n", "")
                print(data)
                yield f"data: {data} \n\n"
                data = split[1]

                if len(data) > 0 and data[0] == ",":
                    data = data[1:]
                else:
                    data = ""
            else:
                data += text


def generate_streamed_completion(message: str):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": message,
            },
        ],
        stream=True,
        max_tokens=2000,
        temperature=0.3,
    )
