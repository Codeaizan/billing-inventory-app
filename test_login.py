import bcrypt
import sqlite3
from database.db_manager import db

# Generate correct hash for admin123
password = "admin123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
correct_hash = hashed.decode('utf-8')

print(f"Generated hash for 'admin123': {correct_hash}")
print()

# Update database with correct hash
try:
    with db.get_connection() as conn:
        # Delete existing admin user
        conn.execute("DELETE FROM users WHERE username = 'admin'")
        
        # Insert with correct hash
        conn.execute("""
            INSERT INTO users (id, username, password_hash, full_name) 
            VALUES (1, 'admin', ?, 'Administrator')
        """, (correct_hash,))
        
        conn.commit()
        print("✓ Admin user updated successfully!")
        print()
        
        # Verify it worked
        cursor = conn.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
        user = cursor.fetchone()
        
        if user:
            print(f"Username: {user['username']}")
            print(f"Hash in DB: {user['password_hash'][:50]}...")
            print()
            
            # Test verification
            test_result = bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
            print(f"Password verification test: {'✓ PASS' if test_result else '✗ FAIL'}")
        else:
            print("✗ User not found after insert!")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
