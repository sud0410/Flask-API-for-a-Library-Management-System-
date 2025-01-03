import unittestimport jsonfrom app import appimport sqlite3class LibraryAPITests(unittest.TestCase):    """Test suite for our Library Management System API."""    def setUp(self):        """Prepare for testing!"""        self.app = app.test_client()        self.app.testing = True                with app.app_context():            conn = sqlite3.connect('test_library.db')            conn.close()                    register_data = {            'name': 'Test User',            'email': 'test@example.com',            'password': 'testpass123'        }        self.app.post('/register',                      data=json.dumps(register_data),                     content_type='application/json')                                     response = self.app.post('/login',                               data=json.dumps({                                   'email': 'test@example.com',                                   'password': 'testpass123'                               }),                               content_type='application/json')        self.token = json.loads(response.data)['token']    def test_register_member(self):        """Test member registration."""        data = {            'name': 'Jane Doe',            'email': 'jane@example.com',            'password': 'securepass123'        }        response = self.app.post('/register',                               data=json.dumps(data),                               content_type='application/json')        self.assertEqual(response.status_code, 201)        self.assertIn('Welcome to the library', json.loads(response.data)['message'])    def test_login_success(self):        """Test successful login."""        data = {            'email': 'test@example.com',            'password': 'testpass123'        }        response = self.app.post('/login',                               data=json.dumps(data),                               content_type='application/json')        self.assertEqual(response.status_code, 200)        self.assertIn('token', json.loads(response.data))    def test_login_failure(self):        """Test login with wrong password."""        data = {            'email': 'test@example.com',            'password': 'wrongpass'        }        response = self.app.post('/login',                               data=json.dumps(data),                               content_type='application/json')        self.assertEqual(response.status_code, 401)    def test_add_book(self):        """Test adding a new book."""        data = {            'title': 'The Great Gatsby',            'author': 'F. Scott Fitzgerald',            'isbn': '978-0743273565'        }        response = self.app.post('/books',                               data=json.dumps(data),                               content_type='application/json',                               headers={'Authorization': f'Bearer {self.token}'})        self.assertEqual(response.status_code, 201)        self.assertIn('Added', json.loads(response.data)['message'])    def test_get_books(self):        """Test retrieving books list."""        test_book = {            'title': 'Pride and Prejudice',            'author': 'Jane Austen',            'isbn': '978-0141439518'        }        self.app.post('/books',                     data=json.dumps(test_book),                     content_type='application/json',                     headers={'Authorization': f'Bearer {self.token}'})        response = self.app.get('/books')        data = json.loads(response.data)                self.assertEqual(response.status_code, 200)        self.assertIn('books', data)        self.assertTrue(len(data['books']) > 0)    def test_search_books(self):        """Test searching for books."""        books = [            {                'title': 'The Hobbit',                'author': 'J.R.R. Tolkien',                'isbn': '978-0547928227'            },            {                'title': 'The Fellowship of the Ring',                'author': 'J.R.R. Tolkien',                'isbn': '978-0547928210'            }        ]                for book in books:            self.app.post('/books',                         data=json.dumps(book),                         content_type='application/json',                         headers={'Authorization': f'Bearer {self.token}'})        response = self.app.get('/books?search=Tolkien')        data = json.loads(response.data)                self.assertEqual(response.status_code, 200)        self.assertEqual(len(data['books']), 2)        response = self.app.get('/books?search=Hobbit')        data = json.loads(response.data)                self.assertEqual(response.status_code, 200)        self.assertEqual(len(data['books']), 1)    def test_update_book(self):        """Test updating a book's information."""        # First add a test book        test_book = {            'title': 'Original Title',            'author': 'Original Author',            'isbn': '978-1234567890'        }        response = self.app.post('/books',                               data=json.dumps(test_book),                               content_type='application/json',                               headers={'Authorization': f'Bearer {self.token}'})                book_id = 1  # Assuming this is the first book                # Update the book        update_data = {            'title': 'Updated Title',            'author': 'Updated Author'        }        response = self.app.put(f'/books/{book_id}',                              data=json.dumps(update_data),                              content_type='application/json',                              headers={'Authorization': f'Bearer {self.token}'})                self.assertEqual(response.status_code, 200)        self.assertIn('updated successfully', json.loads(response.data)['message'])    def test_delete_book(self):        """Test removing a book."""        test_book = {            'title': 'Book to Delete',            'author': 'Delete Author',            'isbn': '978-9876543210'        }        self.app.post('/books',                     data=json.dumps(test_book),                     content_type='application/json',                     headers={'Authorization': f'Bearer {self.token}'})                book_id = 1  # Assuming this is the first book                # Delete the book        response = self.app.delete(f'/books/{book_id}',                                 headers={'Authorization': f'Bearer {self.token}'})                self.assertEqual(response.status_code, 200)        self.assertIn('Removed', json.loads(response.data)['message'])    def test_pagination(self):        """Test book list pagination."""        for i in range(15):  #testing adding 15 book            book = {                'title': f'Book {i+1}',                'author': f'Author {i+1}',                'isbn': f'978-111111111{i}'            }            self.app.post('/books',                         data=json.dumps(book),                         content_type='application/json',                         headers={'Authorization': f'Bearer {self.token}'})                response = self.app.get('/books')        data = json.loads(response.data)                self.assertEqual(response.status_code, 200)        self.assertEqual(len(data['books']), 10)        self.assertEqual(data['page'], 1)                response = self.app.get('/books?page=2')        data = json.loads(response.data)                self.assertEqual(response.status_code, 200)        self.assertEqual(len(data['books']), 5)        self.assertEqual(data['page'], 2)    def tearDown(self):        """Clean up after testing."""        import os                os.remove('test_library.db')if __name__ == '__main__':    unittest.main()