from flask import Blueprint, request, jsonify
import openai
import re
import logging

generate_quiz = Blueprint("generatequiz", __name__)
openai.api_key = "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"


@generate_quiz.route('/true-false', methods=['POST'])
def generate_tf_quiz():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    numberOfQuestions = data.get('numberOfQuestions')
    quizData = data.get('quizData')
    joinCode = data.get('joinCode')

    quizResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Generate a true or false quiz with {numberOfQuestions} questions based on this "
                           f"information: '{quizData}'. Each question will have an answer of T or F, do not write out "
                           f"the whole word only use the letter. The format of the quiz should be as follows and "
                           f"nothing else:\n"
                           "1. Question 1\n"
                           "Answer: T/F\n"
                           "2. Question 2\n"
                           "Answer: T/F\n"
                           "3. Question 3\n"
                           "Answer: T/F\n"
            }
        ],
        max_tokens=2000,
        temperature=0.0
    )

    quizResponseText = quizResponse.choices[0].message.content

    questions = []
    answerKey = []

    lines = quizResponseText.split("\n")
    currentQuestion = {"query": ""}

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match("^[0-9]+", line):
            currentQuestion["query"] = line
        elif line.startswith("Answer"):
            answer = line.split(":")[1].strip()
            answerKey.append(answer)
            questions.append(currentQuestion)
            currentQuestion = {"query": ""}

    return jsonify({"questions": questions, "answerKey": answerKey}), 200


@generate_quiz.post("/multiple-choice")
def generate_mc_quiz():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    numberOfQuestions = data.get('numberOfQuestions')
    quizData = data.get('quizData')
    joinCode = data.get('joinCode')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"I want you to generate a multiple choice quiz with {numberOfQuestions} questions "
                           f"based on this information: '{quizData}'. If the number of questions exceeds {numberOfQuestions}, "
                           f"follow the same format but add more questions. "
                           f"The format of the quiz should be as follows and nothing else:\n"
                           f"1. Question 1\n"
                           f"A. AnswerChoice\n"
                           f"B. AnswerChoice\n"
                           f"C. AnswerChoice\n"
                           f"D. AnswerChoice\n"
                           f"Answer: _\n"
                           f"2. Question 2\n"
                           f"A. AnswerChoice\n"
                           f"B. AnswerChoice\n"
                           f"C. AnswerChoice\n"
                           f"D. AnswerChoice\n"
                           f"Answer: _\n"
                           f"3. Question 3\n"
                           f"A. AnswerChoice\n"
                           f"B. AnswerChoice\n"
                           f"C. AnswerChoice\n"
                           f"D. AnswerChoice\n"
                           f"Answer: _\n",
            }
        ],
        max_tokens=2000,
        temperature=0.0
    )

    quiz_response_text = response.choices[0].message.content
    lines = quiz_response_text.split("\n")

    questions = []
    answer_key = []
    current_question = {"query": "", "answers": []}

    for line in lines:
        if line.startswith("\n") or line == "":
            continue

        if re.match("^[0-9]+", line):
            if current_question["query"]:
                questions.append(current_question)

            current_question = {
                "query": line,
                "answers": []
            }
        elif line.startswith("Answer"):
            answer_key.append(line[-1])
        elif line.startswith("A") or line.startswith("B") or line.startswith("C") or line.startswith("D"):
            current_question["answers"].append(line)

    questions.append(current_question)

    return {"questions": questions, "answer_key": answer_key}


@generate_quiz.post("/key-points")
def generate_key_points():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed!"}), 405

    data = request.json
    numberOfKeyPoints = data.get('numberOfKeyPoints')
    quizData = data.get('quizData')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"I want you to generate a list of {numberOfKeyPoints} key points based on this information: '{quizData}'"
            }
        ],
        max_tokens=2000,
        temperature=0.5
    )

    print(response.choices[0].message.content)

    return {"keyPoints": response.choices[0].message.content.split("\n")}