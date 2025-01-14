import pypdf
import re


# Turns a pdf into string
def pdf_to_string(file_path):
    reader = pypdf.PdfReader(file_path)
    text = ""

    for i in range(0, len(reader.pages)):
        text += reader.pages[i].extract_text() + '/p'

    return text

def bee_parse(text):
    questions = []
    answers = []

    for i in range(1, 36):
        a = text.index('(' + str(i) + ')') + len(f'({i})')
        b = text.index('ANSWER') + len('ANSWER')

        if i < 35:
            c = text.index('(' + str(i + 1) + ')')
        else:
            c = len(text)

        # Extract and clean the question
        question = text[a:b - len('ANSWER')].strip()
        question = re.sub(r'\[\[.*?\]\]', '', question) 
        question = re.sub(r'\s+', ' ', question) 
        question = question.replace('/p', '').strip()  
        questions.append(question)

        # Extract and clean the answer
        answer = text[b+2:c].strip()
        answer = re.sub(r'\[\[.*?\]\]', '', answer)  
        answer = re.sub(r'\s+', ' ', answer)  
        answer = answer.replace('/p', '').strip() 
        if '(' in answer: 
            answer = answer[:answer.index('(')].strip()
        answers.append(answer)

        text = text[c:]

    # Create the final set 
    result_set = {'questions': questions, 'answers': answers}
    return result_set

def parse(file_path):
    text = pdf_to_string(file_path)
    qa = bee_parse(text)
    return qa