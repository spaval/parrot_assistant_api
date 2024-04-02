def condense_question(input: dict):
    if input.get("chat_history"):
        history = input.get("chat_history")
        last = history[-1]
        return last.content
    else:
        return input.get("question")