import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from storage_helper import upload_file_to_azure

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'sqlite:///library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    comics = db.relationship('Comic', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Comic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50)) # Added Genre
    cover_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Genres list
GENRES = [
    "Action", "Adventure", "Comedy", "Drama", "Fantasy", 
    "Horror", "Mystery", "Romance", "Sci-Fi", "Slice of Life"
]

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        query = request.args.get('q')
        genre_filter = request.args.get('genre')
        
        sql_query = Comic.query.filter_by(user_id=current_user.id)
        
        if query:
            sql_query = sql_query.filter(
                (Comic.title.contains(query)) | (Comic.author.contains(query))
            )
            
        if genre_filter and genre_filter in GENRES:
            sql_query = sql_query.filter_by(genre=genre_filter)
            
        comics = sql_query.all()
    else:
        comics = []
        
    return render_template('index.html', comics=comics, query=request.args.get('q'), genres=GENRES, current_genre=request.args.get('genre'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
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

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author') # Keeping 'author' but contextually it matches 'Creator/Author'
        genre = request.form.get('genre')
        file = request.files.get('cover_image')
        
        cover_url = None
        if file and file.filename != '':
            uploaded_url = upload_file_to_azure(file)
            if uploaded_url:
                cover_url = uploaded_url
        
        new_comic = Comic(title=title, author=author, genre=genre, cover_url=cover_url, owner=current_user)
        db.session.add(new_comic)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', genres=GENRES)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    comic = Comic.query.get_or_404(id)
    if comic.owner != current_user:
        abort(403)
        
    if request.method == 'POST':
        comic.title = request.form.get('title')
        comic.author = request.form.get('author')
        comic.genre = request.form.get('genre')
        file = request.files.get('cover_image')
        
        if file and file.filename != '':
            uploaded_url = upload_file_to_azure(file)
            if uploaded_url:
                comic.cover_url = uploaded_url
                
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', comic=comic, genres=GENRES)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    comic = Comic.query.get_or_404(id)
    if comic.owner != current_user:
        abort(403)
        
    db.session.delete(comic)
    db.session.commit()
    return redirect(url_for('index'))

# Temporary route to reset database
@app.route('/reset_db')
def reset_db():
    try:
        db.drop_all()
        db.create_all()
        return "Database reset successfully! All data has been cleared and schema updated (Comics & Genres)."
    except Exception as e:
        return f"Error resetting database: {e}"

if __name__ == '__main__':
    app.run(debug=True)