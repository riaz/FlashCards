import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, Flashcard
from document_processor import process_document
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flashcards = process_document(file_path)
        for card in flashcards:
            new_flashcard = Flashcard(title=card['title'], content=card['content'])
            db.session.add(new_flashcard)
        db.session.commit()
        os.remove(file_path)  # Remove the file after processing
        return jsonify({'message': 'File processed successfully'}), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/flashcards')
def get_flashcards():
    flashcards = Flashcard.query.all()
    return render_template('flashcards.html', flashcards=flashcards)

@app.route('/flashcard/<int:id>', methods=['GET'])
def get_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    return jsonify({
        'id': flashcard.id,
        'title': flashcard.title,
        'content': flashcard.content,
        'likes': flashcard.likes,
        'dislikes': flashcard.dislikes
    })

@app.route('/flashcard/<int:id>', methods=['DELETE'])
def delete_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    db.session.delete(flashcard)
    db.session.commit()
    return jsonify({'message': 'Flashcard deleted successfully'}), 200

@app.route('/flashcard/<int:id>/like', methods=['POST'])
def like_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    flashcard.likes += 1
    db.session.commit()
    return jsonify({'likes': flashcard.likes})

@app.route('/flashcard/<int:id>/dislike', methods=['POST'])
def dislike_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    flashcard.dislikes += 1
    db.session.commit()
    return jsonify({'dislikes': flashcard.dislikes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
