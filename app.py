import os
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from storage_helper import upload_file_to_azure

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'sqlite:///library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover_url = db.Column(db.String(500))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    query = request.args.get('q')
    if query:
        books = Book.query.filter(Book.title.contains(query) | Book.author.contains(query)).all()
    else:
        books = Book.query.all()
    return render_template('index.html', books=books, query=query)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        file = request.files.get('cover_image')
        
        cover_url = None
        if file and file.filename != '':
            uploaded_url = upload_file_to_azure(file)
            if uploaded_url:
                cover_url = uploaded_url
        
        new_book = Book(title=title, author=author, cover_url=cover_url)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        file = request.files.get('cover_image')
        
        if file and file.filename != '':
            uploaded_url = upload_file_to_azure(file)
            if uploaded_url:
                book.cover_url = uploaded_url
                
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', book=book)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)