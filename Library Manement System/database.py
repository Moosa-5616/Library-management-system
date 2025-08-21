import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create tables
    conn.executescript('''
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS books;
        DROP TABLE IF EXISTS transactions;
        
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            name TEXT,
            admission_number TEXT,
            class_name TEXT,
            section TEXT,
            roll_number TEXT,
            department TEXT,
            subject TEXT,
            phone TEXT,
            password TEXT
        );
        
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            author TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            available INTEGER DEFAULT 1
        );
        
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT DEFAULT 'issued',
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        );
    ''')
    
    # Insert test users
    conn.execute('''
        INSERT INTO users (user_type, phone, password, name) 
        VALUES ('admin', '7382950164', 'Admin 0011', 'Administrator')
    ''')
    
    conn.execute('''
        INSERT INTO users (user_type, name, admission_number, class_name, section, roll_number, password) 
        VALUES ('student', 'Moosa', '7354', '8th', 'Green', '19', 'student123')
    ''')
    
    conn.execute('''
        INSERT INTO users (user_type, name, department, subject, password) 
        VALUES ('employee', 'Mehraj ud din mir', 'ICT', 'Computer', 'Mehraj123')
    ''')
    
    # Insert books (50 books as required)
    books_data = [
        (1, "To Kill a Mockingbird", "Fiction", "Harper Lee", "FIC001"),
        (2, "1984", "Fiction", "George Orwell", "FIC002"),
        (3, "Pride and Prejudice", "Romance", "Jane Austen", "ROM001"),
        (4, "The Great Gatsby", "Fiction", "F. Scott Fitzgerald", "FIC003"),
        (5, "Harry Potter and the Philosopher's Stone", "Fantasy", "J.K. Rowling", "FAN001"),
        (6, "The Catcher in the Rye", "Fiction", "J.D. Salinger", "FIC004"),
        (7, "Lord of the Flies", "Fiction", "William Golding", "FIC005"),
        (8, "The Hobbit", "Fantasy", "J.R.R. Tolkien", "FAN002"),
        (9, "Fahrenheit 451", "Science Fiction", "Ray Bradbury", "SCI001"),
        (10, "Jane Eyre", "Romance", "Charlotte Brontë", "ROM002"),
        (11, "Wuthering Heights", "Romance", "Emily Brontë", "ROM003"),
        (12, "The Lord of the Rings", "Fantasy", "J.R.R. Tolkien", "FAN003"),
        (13, "Animal Farm", "Fiction", "George Orwell", "FIC006"),
        (14, "Brave New World", "Science Fiction", "Aldous Huxley", "SCI002"),
        (15, "The Kite Runner", "Drama", "Khaled Hosseini", "DRA001"),
        (16, "Life of Pi", "Adventure", "Yann Martel", "ADV001"),
        (17, "The Book Thief", "Historical Fiction", "Markus Zusak", "HIS001"),
        (18, "The Alchemist", "Philosophy", "Paulo Coelho", "PHI001"),
        (19, "One Hundred Years of Solitude", "Magical Realism", "Gabriel García Márquez", "MAG001"),
        (20, "The Picture of Dorian Gray", "Gothic", "Oscar Wilde", "GOT001"),
        (21, "Dracula", "Horror", "Bram Stoker", "HOR001"),
        (22, "Frankenstein", "Horror", "Mary Shelley", "HOR002"),
        (23, "The Strange Case of Dr. Jekyll and Mr. Hyde", "Horror", "Robert Louis Stevenson", "HOR003"),
        (24, "A Tale of Two Cities", "Historical Fiction", "Charles Dickens", "HIS002"),
        (25, "Great Expectations", "Fiction", "Charles Dickens", "FIC007"),
        (26, "Oliver Twist", "Fiction", "Charles Dickens", "FIC008"),
        (27, "David Copperfield", "Fiction", "Charles Dickens", "FIC009"),
        (28, "The Adventures of Tom Sawyer", "Adventure", "Mark Twain", "ADV002"),
        (29, "Adventures of Huckleberry Finn", "Adventure", "Mark Twain", "ADV003"),
        (30, "Moby Dick", "Adventure", "Herman Melville", "ADV004"),
        (31, "The Odyssey", "Epic", "Homer", "EPI001"),
        (32, "The Iliad", "Epic", "Homer", "EPI002"),
        (33, "Romeo and Juliet", "Drama", "William Shakespeare", "DRA002"),
        (34, "Hamlet", "Drama", "William Shakespeare", "DRA003"),
        (35, "Macbeth", "Drama", "William Shakespeare", "DRA004"),
        (36, "Othello", "Drama", "William Shakespeare", "DRA005"),
        (37, "King Lear", "Drama", "William Shakespeare", "DRA006"),
        (38, "A Midsummer Night's Dream", "Comedy", "William Shakespeare", "COM001"),
        (39, "The Merchant of Venice", "Drama", "William Shakespeare", "DRA007"),
        (40, "The Tempest", "Drama", "William Shakespeare", "DRA008"),
        (41, "Don Quixote", "Adventure", "Miguel de Cervantes", "ADV005"),
        (42, "War and Peace", "Historical Fiction", "Leo Tolstoy", "HIS003"),
        (43, "Anna Karenina", "Romance", "Leo Tolstoy", "ROM004"),
        (44, "Crime and Punishment", "Psychological Fiction", "Fyodor Dostoevsky", "PSY001"),
        (45, "The Brothers Karamazov", "Philosophical Fiction", "Fyodor Dostoevsky", "PHI002"),
        (46, "Les Misérables", "Historical Fiction", "Victor Hugo", "HIS004"),
        (47, "The Hunchback of Notre-Dame", "Historical Fiction", "Victor Hugo", "HIS005"),
        (48, "The Count of Monte Cristo", "Adventure", "Alexandre Dumas", "ADV006"),
        (49, "The Three Musketeers", "Adventure", "Alexandre Dumas", "ADV007"),
        (50, "Around the World in Eighty Days", "Adventure", "Jules Verne", "ADV008")
    ]
    
    for book in books_data:
        conn.execute('''
            INSERT INTO books (id, title, category, author, code, available) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', book)
    
    # Get user IDs
    student_id = conn.execute("SELECT id FROM users WHERE name = 'Moosa'").fetchone()['id']
    employee_id = conn.execute("SELECT id FROM users WHERE name = 'Mehraj ud din mir'").fetchone()['id']
    
    # Student transactions (last 3 books issued, first 2 returned, one overdue by 6 days)
    # Issue last 3 books (48, 49, 50)
    issue_date_overdue = (datetime.now() - timedelta(days=13)).strftime('%Y-%m-%d')  # 13 days ago (6 days overdue)
    issue_date_recent = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')   # 3 days ago
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 48, ?, 'issued')
    ''', (student_id, issue_date_overdue))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 49, ?, 'issued')
    ''', (student_id, issue_date_recent))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 50, ?, 'issued')
    ''', (student_id, issue_date_recent))
    
    # Mark these books as unavailable
    conn.execute('UPDATE books SET available = 0 WHERE id IN (48, 49, 50)')
    
    # Return first 2 books (1, 2)
    return_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, return_date, status)
        VALUES (?, 1, ?, ?, 'returned')
    ''', (student_id, (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), return_date))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, return_date, status)
        VALUES (?, 2, ?, ?, 'returned')
    ''', (student_id, (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'), return_date))
    
    # Employee transactions (first 3 books issued, last 3 returned)
    # Issue first 3 books (1, 2, 3) - but 1,2 are available since student returned them
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 1, ?, 'issued')
    ''', (employee_id, issue_date_recent))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 2, ?, 'issued')
    ''', (employee_id, issue_date_recent))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, status)
        VALUES (?, 3, ?, 'issued')
    ''', (employee_id, issue_date_recent))
    
    # Mark books 1, 2, 3 as unavailable
    conn.execute('UPDATE books SET available = 0 WHERE id IN (1, 2, 3)')
    
    # Return last 3 books (48, 49, 50) - but these are currently with student, so use different books
    # Let's use books 4, 5, 6 for employee returns
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, return_date, status)
        VALUES (?, 4, ?, ?, 'returned')
    ''', (employee_id, (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'), return_date))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, return_date, status)
        VALUES (?, 5, ?, ?, 'returned')
    ''', (employee_id, (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d'), return_date))
    
    conn.execute('''
        INSERT INTO transactions (user_id, book_id, issue_date, return_date, status)
        VALUES (?, 6, ?, ?, 'returned')
    ''', (employee_id, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), return_date))
    
    conn.commit()
    conn.close()
