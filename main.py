import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Flashcard, User
from document_processor import process_document
from config import Config
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        flashcards = process_document(file_path)
        for card in flashcards:
            new_flashcard = Flashcard(title=card['title'], content=card['content'], user_id=current_user.id)
            db.session.add(new_flashcard)
        db.session.commit()
        os.remove(file_path)  # Remove the file after processing
        return jsonify({'message': 'File processed successfully'}), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/flashcards')
@login_required
def get_flashcards():
    flashcards = Flashcard.query.filter_by(user_id=current_user.id).all()
    return render_template('flashcards.html', flashcards=flashcards)

@app.route('/flashcard/<int:id>', methods=['GET'])
@login_required
def get_flashcard(id):
    flashcard = Flashcard.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': flashcard.id,
        'title': flashcard.title,
        'content': flashcard.content,
        'likes': flashcard.likes,
        'dislikes': flashcard.dislikes
    })

@app.route('/flashcard/<int:id>', methods=['DELETE'])
@login_required
def delete_flashcard(id):
    flashcard = Flashcard.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(flashcard)
    db.session.commit()
    return jsonify({'message': 'Flashcard deleted successfully'}), 200

@app.route('/flashcard/<int:id>/like', methods=['POST'])
@login_required
def like_flashcard(id):
    flashcard = Flashcard.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    flashcard.likes += 1
    db.session.commit()
    return jsonify({'likes': flashcard.likes})

@app.route('/flashcard/<int:id>/dislike', methods=['POST'])
@login_required
def dislike_flashcard(id):
    flashcard = Flashcard.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    flashcard.dislikes += 1
    db.session.commit()
    return jsonify({'dislikes': flashcard.dislikes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
