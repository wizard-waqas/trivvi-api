from flask import Blueprint, request, jsonify
import openai
import re

generate_quiz = Blueprint("generatequiz", __name__)
openai.api_key = "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"


@generate_quiz.post("/tf")
def generate_tf_question():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    quizData = data.get('quizData')
    numberOfQuestions = data.get("numberOfQuestions")

    quizResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a true or false quiz with {numberOfQuestions} questions "
                           f"based on this information: '{quizData}'. Each question will have an answer of T or F, "
                           f"do not write out the whole word only use the letter. "
                           f"The format of each question should be as follows and nothing else:\n"
                           "1. [insert question text]\n"
                           "Answer: [insert T or F]\n"
            }
        ],
        max_tokens=2000,
        temperature=0.0
    )

    quizResponseText = quizResponse.choices[0].message.content
    lines = quizResponseText.split("\n")

    question = {"query": ""}
    answerKey = ""

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match("^[0-9]+", line):  # if line starts with a number
            question["query"] = re.sub(r'^\d+\.\s*', '', line)  # remove the number and period
        elif line.startswith("Answer"):
            answer = line.split(":")[1].strip()
            answerKey = answer

    return jsonify({"question": question, "answerKey": answerKey}), 200


@generate_quiz.post("/mc")
def generate_mc_question():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    quizData = data.get('quizData')
    numberOfQuestions = data.get("numberOfQuestions")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a multiple choice quiz with {numberOfQuestions} questions "
                           f"based on this information: '{quizData}'. "
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
        temperature=0.0
    )

    quiz_response_text = response.choices[0].message.content
    lines = quiz_response_text.split("\n")

    question = {"query": "", "answers": []}
    answer_key = ""

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match("^[0-9]+", line):  # if line starts with a number
            question["query"] = re.sub(r'^\d+\.\s*', '', line)  # remove the number and period
        elif line.startswith("Answer"):
            answer_key = line[-1]
        elif line.startswith("A") or line.startswith("B") or line.startswith("C") or line.startswith("D"):
            question["answers"].append(line)

    return {"question": question, "answerKey": answer_key}


@generate_quiz.post("/key-points")
def generate_key_points():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    number_of_key_points = data.get('numberOfKeyPoints')
    quiz_data = data.get('quizData')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a list of {number_of_key_points} key points based on this information: '{quiz_data}'"
            }
        ],
        max_tokens=2000,
        temperature=0.3
    )

    lines = response.choices[0].message.content.split("\n")
    list_of_key_points = [re.sub(r'^\d+\.\s*', '', line) for line in lines]  # remove number from beginning of line

    return {"keyPoints": list_of_key_points}
