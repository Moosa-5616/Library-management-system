def authenticate_user(user_type, credentials):
    """Authenticate user based on type and credentials"""
    from database import get_db_connection
    
    conn = get_db_connection()
    user = None
    
    try:
        if user_type == 'student':
            user = conn.execute('''
                SELECT * FROM users 
                WHERE user_type = 'student' 
                AND admission_number = ? 
                AND password = ?
            ''', (
                credentials['admission_number'],
                credentials['password']
            )).fetchone()
            
        elif user_type == 'employee':
            user = conn.execute('''
                SELECT * FROM users 
                WHERE user_type = 'employee' 
                AND name = ? 
                AND department = ? 
                AND password = ?
            ''', (
                credentials['name'],
                credentials['department'],
                credentials['password']
            )).fetchone()
            
        elif user_type == 'admin':
            user = conn.execute('''
                SELECT * FROM users 
                WHERE user_type = 'admin' 
                AND phone = ? 
                AND password = ?
            ''', (
                credentials['phone'],
                credentials['password']
            )).fetchone()
        
        return dict(user) if user else None
        
    finally:
        conn.close()

def get_user_role(user_id):
    """Get user role by user ID"""
    from database import get_db_connection
    
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT user_type FROM users WHERE id = ?', (user_id,)).fetchone()
        return user['user_type'] if user else None
    finally:
        conn.close()
