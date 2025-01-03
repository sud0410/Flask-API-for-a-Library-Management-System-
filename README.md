# Flask-API-for-a-Library-Management-System-
A Flask-based REST API for managing a library system, supporting CRUD operations for books and members.
Features:-
Book management (Create, Read, Update, Delete)
Member registration and authentication
Token-based authentication using JWT
Search functionality for books by title or author
Pagination support for book listings
Type hints and annotations for better code maintainability
Unit tests for all endpoints

SETUP INSTRUCTIONS:
1) Clone Rep
2) Create & Activate vir environment
3) install dependencies and run app

API ENDPOINTS: 
POST /register - Register new member
POST /login - Login and receive JWT token

Books
GET /books - List all books 
POST /books - Add new book 
PUT /books/<id> - Update book 
DELETE /books/<id> - Delete book 

DESIGN CHOICES:
1) DB - SQLITE
2) Auth - JWT
3) Error Handling :
Descriptive error messages
Appropriate HTTP status codes
SQLite error handling

ASSUMPTIONS & LIMITATIONS:
Assumptions:
Single-user role (no admin/user distinction)
ISBN uniqueness for books
Email uniqueness for members
Basic password security (SHA-256 hashing)

Limitations:
No password recovery mechanism
No book reservation system
No book borrowing tracking
Basic search functionality (no advanced filtering)
In-memory SQLite database (data doesn't persist between restarts)

FUTURE IMPROVEMENTS:
-Implement database migrations
-Add book categories and tags
-Implement rate limiting
-Add logging system





