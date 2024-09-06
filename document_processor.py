import PyPDF2
import markdown
import re

def process_document(file_path):
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return process_pdf(file_path)
    elif file_extension == 'md':
        return process_markdown(file_path)
    elif file_extension == 'txt':
        return process_text(file_path)
    else:
        raise ValueError("Unsupported file format")

def process_pdf(file_path):
    flashcards = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            flashcards.extend(extract_flashcards(text))
    return flashcards

def process_markdown(file_path):
    with open(file_path, 'r') as file:
        md_content = file.read()
        html_content = markdown.markdown(md_content)
        text = re.sub('<[^<]+?>', '', html_content)
        return extract_flashcards(text)

def process_text(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
        return extract_flashcards(text)

def extract_flashcards(text):
    # This is a simple implementation. You might want to improve this based on your specific needs.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    flashcards = []
    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences):
            flashcards.append({
                'title': sentences[i][:100],  # Limit title to 100 characters
                'content': sentences[i] + ' ' + sentences[i+1]
            })
    return flashcards
