import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from database import init_db, get_db_connection
from auth import authenticate_user, get_user_role

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "library_management_secret_key_2024")

# Initialize database on startup
with app.app_context():
    init_db()

def calculate_fine(issue_date_str):
    """Calculate fine for overdue books (₹2/day after 7 days)"""
    try:
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
        days_diff = (datetime.now() - issue_date).days
        if days_diff > 7:
            return (days_diff - 7) * 2
        return 0
    except:
        return 0

@app.route('/admin/register/student', methods=['POST'])
def admin_register_student():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    admission_number = request.form.get('admission_number')
    password = request.form.get('password')
    if not admission_number or not password:
        flash('Admission number and password are required.', 'error')
        return redirect(url_for('dashboard_admin'))
    conn = get_db_connection()
    try:
        # prevent duplicates on admission_number among students
        existing = conn.execute("""
            SELECT id FROM users 
            WHERE user_type = 'student' AND admission_number = ?
        """, (admission_number,)).fetchone()
        if existing:
            flash('Student with this admission number already exists.', 'error')
            return redirect(url_for('dashboard_admin'))
        conn.execute("""
            INSERT INTO users (user_type, admission_number, password)
            VALUES ('student', ?, ?)
        """, (admission_number, password))
        conn.commit()
        flash('Student registered successfully.', 'success')
    except Exception as e:
        flash(f'Error registering student: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/register/employee', methods=['POST'])
def admin_register_employee():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    name = request.form.get('name')
    department = request.form.get('department')
    password = request.form.get('password')
    if not name or not department or not password:
        flash('Name, department and password are required.', 'error')
        return redirect(url_for('dashboard_admin'))
    conn = get_db_connection()
    try:
        # prevent duplicates for the same employee name+department combo
        existing = conn.execute("""
            SELECT id FROM users 
            WHERE user_type = 'employee' AND name = ? AND department = ?
        """, (name, department)).fetchone()
        if existing:
            flash('Employee with this name and department already exists.', 'error')
            return redirect(url_for('dashboard_admin'))
        conn.execute("""
            INSERT INTO users (user_type, name, department, password)
            VALUES ('employee', ?, ?, ?)
        """, (name, department, password))
        conn.commit()
        flash('Employee registered successfully.', 'success')
    except Exception as e:
        flash(f'Error registering employee: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('dashboard_admin'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/<user_type>')
@app.route('/login/<user_type>')
def login_page(user_type):
    if user_type not in ['student', 'employee', 'admin']:
        return redirect(url_for('index'))
    return render_template(f'login_{user_type}.html', user_type=user_type)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    user_type = request.form.get('user_type')
    user = None
    
    if user_type == 'student':
        admission_number = request.form.get('admission_number')
        password = request.form.get('password')
        
        user = authenticate_user('student', {
            'admission_number': admission_number,
            'password': password
        })
        
    elif user_type == 'employee':
        name = request.form.get('name')
        department = request.form.get('department')
        password = request.form.get('password')
        
        user = authenticate_user('employee', {
            'name': name,
            'department': department,
            'password': password
        })
        
    elif user_type == 'admin':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        user = authenticate_user('admin', {
            'phone': phone,
            'password': password
        })
    
    if user:
        session['user_id'] = user['id']
        session['user_type'] = user_type
        session['user_name'] = (user.get('name') or user.get('admission_number', ''))
        return redirect(url_for(f'dashboard_{user_type}'))
    else:
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('login_page', user_type=user_type))

@app.route('/dashboard/student')
def dashboard_student():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get issued books
    issued_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date, t.id as transaction_id
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ? AND t.status = 'issued'
    ''', (user_id,)).fetchall()
    
    # Get returned books
    returned_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date, t.return_date
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ? AND t.status = 'returned'
    ''', (user_id,)).fetchall()
    
    # Get available books
    available_books = conn.execute('''
        SELECT * FROM books WHERE available = 1
        ORDER BY title
    ''').fetchall()
    
    # Calculate total fine
    total_fine = 0
    for book in issued_books:
        fine = calculate_fine(book['issue_date'])
        total_fine += fine
    
    conn.close()
    
    return render_template('dashboard_student.html', 
                         issued_books=issued_books,
                         returned_books=returned_books,
                         available_books=available_books,
                         total_fine=total_fine,
                         calculate_fine=calculate_fine)

@app.route('/dashboard/employee')
def dashboard_employee():
    if 'user_id' not in session or session.get('user_type') != 'employee':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get issued books
    issued_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ? AND t.status = 'issued'
    ''', (user_id,)).fetchall()
    
    # Get returned books
    returned_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date, t.return_date
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ? AND t.status = 'returned'
    ''', (user_id,)).fetchall()
    
    # Get available books
    available_books = conn.execute('''
        SELECT * FROM books WHERE available = 1
        ORDER BY title
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard_employee.html', 
                         issued_books=issued_books,
                         returned_books=returned_books,
                         available_books=available_books)

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get all issued books
    issued_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date, u.name, u.user_type, t.id as transaction_id
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN users u ON t.user_id = u.id
        WHERE t.status = 'issued'
        ORDER BY t.issue_date DESC
    ''').fetchall()
    
    # Get all returned books
    returned_books = conn.execute('''
        SELECT b.title, b.author, b.code, t.issue_date, t.return_date, u.name, u.user_type
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN users u ON t.user_id = u.id
        WHERE t.status = 'returned'
        ORDER BY t.return_date DESC
    ''').fetchall()
    
    # Get all books
    all_books = conn.execute('''
        SELECT * FROM books ORDER BY title
    ''').fetchall()
    
    # Get users for book assignment
    all_users = conn.execute('''
        SELECT id, name, user_type, admission_number, department FROM users WHERE user_type != 'admin'
        ORDER BY user_type, COALESCE(name, admission_number)
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard_admin.html', 
                         issued_books=issued_books,
                         returned_books=returned_books,
                         all_books=all_books,
                         all_users=all_users,
                         calculate_fine=calculate_fine)

@app.route('/admin/add_book', methods=['POST'])
def add_book():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    category = request.form.get('category')
    author = request.form.get('author')
    code = request.form.get('code')
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO books (title, category, author, code, available)
            VALUES (?, ?, ?, ?, 1)
        ''', (title, category, author, code))
        conn.commit()
        flash('Book added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding book: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/remove_book/<int:book_id>')
def remove_book(book_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        # Check if book is currently issued
        issued = conn.execute('''
            SELECT COUNT(*) as count FROM transactions 
            WHERE book_id = ? AND status = 'issued'
        ''', (book_id,)).fetchone()
        
        if issued['count'] > 0:
            flash('Cannot remove book - it is currently issued!', 'error')
        else:
            conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
            conn.commit()
            flash('Book removed successfully!', 'success')
    except Exception as e:
        flash(f'Error removing book: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/issue_book', methods=['POST'])
def issue_book():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    book_id = request.form.get('book_id')
    user_id = request.form.get('user_id')
    
    conn = get_db_connection()
    try:
        # Check if book is available
        book = conn.execute('SELECT available FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book or not book['available']:
            flash('Book is not available!', 'error')
        else:
            # Issue the book
            conn.execute('''
                INSERT INTO transactions (user_id, book_id, issue_date, status)
                VALUES (?, ?, ?, 'issued')
            ''', (user_id, book_id, datetime.now().strftime('%Y-%m-%d')))
            
            # Mark book as unavailable
            conn.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
            conn.commit()
            flash('Book issued successfully!', 'success')
    except Exception as e:
        flash(f'Error issuing book: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/return_book/<int:transaction_id>')
def return_book(transaction_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        # Get the transaction
        transaction = conn.execute('''
            SELECT book_id FROM transactions WHERE id = ? AND status = 'issued'
        ''', (transaction_id,)).fetchone()
        
        if transaction:
            # Mark as returned
            conn.execute('''
                UPDATE transactions 
                SET status = 'returned', return_date = ?
                WHERE id = ?
            ''', (datetime.now().strftime('%Y-%m-%d'), transaction_id))
            
            # Mark book as available
            conn.execute('UPDATE books SET available = 1 WHERE id = ?', (transaction['book_id'],))
            conn.commit()
            flash('Book returned successfully!', 'success')
        else:
            flash('Transaction not found!', 'error')
    except Exception as e:
        flash(f'Error returning book: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard_admin'))

@app.route('/search')
def search_books():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(request.referrer or url_for('index'))
    
    conn = get_db_connection()
    search_term = query.lower()
    books = conn.execute('''
        SELECT * FROM books 
        WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(code) LIKE ?
        ORDER BY title COLLATE NOCASE
    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')).fetchall()
    no_results = len(books) == 0
    
    # Return to appropriate dashboard with search results and required context
    user_type = session.get('user_type', 'student')
    if user_type == 'student':
        user_id = session.get('user_id')
        issued_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date, t.id as transaction_id
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id = ? AND t.status = 'issued'
        ''', (user_id,)).fetchall()
        returned_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date, t.return_date
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id = ? AND t.status = 'returned'
        ''', (user_id,)).fetchall()
        available_books = conn.execute('''
            SELECT * FROM books WHERE available = 1
            ORDER BY title
        ''').fetchall()
        total_fine = 0
        for book in issued_books:
            fine = calculate_fine(book['issue_date'])
            total_fine += fine
        conn.close()
        return render_template('dashboard_student.html',
            issued_books=issued_books,
            returned_books=returned_books,
            available_books=available_books,
            total_fine=total_fine,
            calculate_fine=calculate_fine,
            search_results=books,
            search_query=query,
            search_no_results=no_results
        )
    elif user_type == 'employee':
        user_id = session.get('user_id')
        issued_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id = ? AND t.status = 'issued'
        ''', (user_id,)).fetchall()
        returned_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date, t.return_date
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id = ? AND t.status = 'returned'
        ''', (user_id,)).fetchall()
        available_books = conn.execute('''
            SELECT * FROM books WHERE available = 1
            ORDER BY title
        ''').fetchall()
        conn.close()
        return render_template('dashboard_employee.html',
            issued_books=issued_books,
            returned_books=returned_books,
            available_books=available_books,
            search_results=books,
            search_query=query,
            search_no_results=no_results
        )
    else:  # admin
        issued_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date, u.name, u.user_type, t.id as transaction_id
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'issued'
            ORDER BY t.issue_date DESC
        ''').fetchall()
        returned_books = conn.execute('''
            SELECT b.title, b.author, b.code, t.issue_date, t.return_date, u.name, u.user_type
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'returned'
            ORDER BY t.return_date DESC
        ''').fetchall()
        all_books = conn.execute('''
            SELECT * FROM books ORDER BY title
        ''').fetchall()
        all_users = conn.execute('''
            SELECT id, name, user_type, admission_number, department FROM users WHERE user_type != 'admin'
            ORDER BY user_type, COALESCE(name, admission_number)
        ''').fetchall()
        conn.close()
        return render_template('dashboard_admin.html',
            issued_books=issued_books,
            returned_books=returned_books,
            all_books=all_books,
            all_users=all_users,
            calculate_fine=calculate_fine,
                         search_results=books, 
            search_query=query,
            search_no_results=no_results
        )

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)                                                              