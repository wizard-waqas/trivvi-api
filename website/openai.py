from flask import Blueprint, Response, request, jsonify, make_response, stream_template
import openai
import re

generate_quiz = Blueprint("generatequiz", __name__)
openai.api_key = "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"


@generate_quiz.post("/tf")
def generate_tf_question():
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


@generate_quiz.post("/stream")
def test_stream():
    if request.method != "POST":
        return jsonify({"message": "Method Not Allowed!"}), 405

    if not (request.data):
        return jsonify({"message": "Invalid JSON"}), 400

    data = request.json

    quizType = data.get("quizType")
    quizData = data.get("quizData")
    numberOfQuestions = data.get("numberOfQuestions")
    difficultyLevel = data.get("difficultyLevel")

    message = ""

    if quizType == "tf":
        message = (
            f"Generate a true and false quiz with {numberOfQuestions} questions based on the topic of {quizData}. "
            f"The difficulty of the questions should be {difficultyLevel}. The response must be json objects separated by commas and not in an array. "
            f"The json object must have a field called question with the question, field called answers with a list of True and False, and a field called answer with the correct answer. "
            f"There should not be anything else in the response."
        )
    elif quizType == "mc":
        message = (
            f"Generate a multiple choice quiz with {numberOfQuestions} questions based on the topic of {quizData}. "
            f"The difficulty of the questions should be {difficultyLevel}. The response must be json objects separated by commas and not in an array. "
            f"The json object must have a field called question with the question, field called answers with a total of 4 answers, and a field called answer with the correct answer. "
            f"There should not be anything else in the response."
        )
    else:
        return jsonify({"message": "Invalid quiz type"}), 400

    def event_stream():
        data = ""
        for line in stream_messages(message):
            text = line.choices[0].delta.get("content", "")

            if len(text):
                if "}" in text:
                    split = text.split("}")
                    data += split[0] + "}"
                    yield f"{data}"
                    print(data)
                    data = split[1]

                    if len(data) > 0 and data[0] == ",":
                        data = data[1:]
                    else:
                        data = ""
                else:
                    data += text

    return Response(event_stream(), mimetype="text/event-stream")


def stream_messages(message: str):
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
        temperature=0.0,
    )
