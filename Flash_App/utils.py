
def parse_questions_answers(content):
    # Implement your parsing logic here
    pairs = content.split('Question: ')[1:]
    flashcards = []

    for pair in pairs:
        question, answer = pair.split('Answer: ')
        flashcards.append({'question': question.strip(), 'answer': answer.strip()})

    return flashcards

