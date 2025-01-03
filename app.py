from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import jwt
from functools import wraps
import json
from typing import Dict, List, Optional, Tuple
import hashlib
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Generate a secure random key

BookDict = Dict[str, str]
MemberDict = Dict[str, str]
DatabaseResponse = Tuple[List, Optional[str]]

def init_db() -> 
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'available'
            )
        ''')
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                join_date TEXT NOT NULL
            )
        ''')
        
        conn.commit()

def get_hashed_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Sorry, you need to log in first!'}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Invalid token. Please log in again.'}), 401
            
        return f(*args, **kwargs)
    return decorated

# Bookmng
@app.route('/books', methods=['GET'])
def get_books() -> tuple:
    try:
        # Get search parameters
        search_term = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            
            if search_term:
                cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE ? OR author LIKE ?
                    LIMIT ? OFFSET ?
                ''', (f'%{search_term}%', f'%{search_term}%', per_page, (page-1)*per_page))
            else:
                cursor.execute('SELECT * FROM books LIMIT ? OFFSET ?', 
                             (per_page, (page-1)*per_page))
            
            books = cursor.fetchall()
            
            books_list = [{
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'isbn': book[3],
                'status': book[4]
            } for book in books]
            
            return jsonify({
                'books': books_list,
                'page': page,
                'per_page': per_page
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500

@app.route('/books', methods=['POST'])
@token_required
def add_book() -> tuple:
    """Add a new book to our collection."""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'author', 'isbn']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Please provide title, author, and ISBN'}), 400
            
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO books (title, author, isbn, status)
                VALUES (?, ?, ?, 'available')
            ''', (data['title'], data['author'], data['isbn']))
            
            return jsonify({'message': f"Added '{data['title']}' to the library!"}), 201
            
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Looks like we already have this book (ISBN must be unique)'}), 400
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500

@app.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id: int) -> tuple:
    """Update a book's information."""
    try:
        data = request.get_json()
        
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            if not cursor.fetchone():
                return jsonify({'error': "We couldn't find that book!"}), 404
                
            updates = []
            values = []
            for field in ['title', 'author', 'isbn', 'status']:
                if field in data:
                    updates.append(f'{field} = ?')
                    values.append(data[field])
            
            if not updates:
                return jsonify({'error': 'No fields to update'}), 400
                
            values.append(book_id)
            cursor.execute(f'''
                UPDATE books 
                SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            
            return jsonify({'message': 'Book updated successfully!'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id: int) -> tuple:
    """Remove a book from our collection."""
    try:
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT title FROM books WHERE id = ?', (book_id,))
            book = cursor.fetchone()
            
            if not book:
                return jsonify({'error': "We couldn't find that book!"}), 404
                
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            
            return jsonify({'message': f"Removed '{book[0]}' from the library"}), 200
            
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500

@app.route('/register', methods=['POST'])
def register_member() -> tuple:
    """Welcome a new member to our library!"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Please provide name, email, and password'}), 400
            
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            
            hashed_password = get_hashed_password(data['password'])
            join_date = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO members (name, email, password, join_date)
                VALUES (?, ?, ?, ?)
            ''', (data['name'], data['email'], hashed_password, join_date))
            
            return jsonify({'message': f"Welcome to the library, {data['name']}!"}), 201
            
    except sqlite3.IntegrityError:
        return jsonify({'error': 'This email is already registered'}), 400
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login() -> tuple:
    """Log in an existing member."""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Please provide email and password'}), 400
            
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM members WHERE email = ?', (data['email'],))
            member = cursor.fetchone()
            
            if not member or member[3] != get_hashed_password(data['password']):
                return jsonify({'error': 'Invalid email or password'}), 401
                
            token = jwt.encode(
                {'member_id': member[0], 'exp': datetime.utcnow() + timedelta(days=1)},
                app.config['SECRET_KEY']
            )
            
            return jsonify({
                'message': f"Welcome back, {member[1]}!",
                'token': token
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Oops! Something went wrong: {str(e)}'}), 500
    
@app.route('/')
def home():
    return jsonify({
        'message': 'Library Management System API',
        'endpoints': {
            'books': '/books',
            'register': '/register',
            'login': '/login'
        },
        'status': 'running'
    }), 200

if __name__ == '__main__':
    init_db()  
    app.run(debug=True)
