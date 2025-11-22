#!/usr/bin/env python3
"""
PostgreSQL Setup Helper for ATM Surveillance System
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_password(password):
    """Test if password works"""
    print(f"Testing password: {password}")
    cmd = f'psql -U postgres -h localhost -c "SELECT 1;" -W'
    
    # Create a temporary password file
    with open('temp_pwd.txt', 'w') as f:
        f.write(password)
    
    try:
        # Use the password file
        cmd = f'psql -U postgres -h localhost -c "SELECT 1;" --password'
        success, stdout, stderr = run_command(f'echo {password} | {cmd}')
        
        if success:
            print(f"SUCCESS: Password '{password}' works!")
            return True
        else:
            print(f"FAILED: Password '{password}' doesn't work")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists('temp_pwd.txt'):
            os.remove('temp_pwd.txt')

def create_database():
    """Create the database"""
    print("\nCreating database 'atmsurvelliance'...")
    
    # Try different passwords
    passwords_to_try = [
        "S@dh5518!",
        "postgres", 
        "admin",
        "password",
        "123456",
        ""
    ]
    
    working_password = None
    
    for pwd in passwords_to_try:
        if test_password(pwd):
            working_password = pwd
            break
    
    if working_password:
        print(f"\nUsing password: {working_password}")
        
        # Create database
        cmd = f'psql -U postgres -h localhost -c "CREATE DATABASE atmsurvelliance;"'
        success, stdout, stderr = run_command(f'echo {working_password} | {cmd}')
        
        if success:
            print("SUCCESS: Database created!")
            return working_password
        else:
            print(f"FAILED to create database: {stderr}")
    else:
        print("No working password found")
    
    return None

def main():
    print("PostgreSQL Setup Helper for ATM Surveillance System")
    print("=" * 60)
    
    # Check if PostgreSQL is running
    success, stdout, stderr = run_command('net start | findstr -i postgres')
    if success and 'postgresql' in stdout.lower():
        print("SUCCESS: PostgreSQL service is running")
    else:
        print("ERROR: PostgreSQL service is not running")
        print("Please start PostgreSQL service first")
        return
    
    # Try to create database
    working_password = create_database()
    
    if working_password:
        print(f"\nSUCCESS: PostgreSQL setup completed!")
        print(f"Working password: {working_password}")
        print("\nUpdate your config.py with:")
        if working_password:
            encoded_pwd = working_password.replace('@', '%40').replace('!', '%21')
            print(f"SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:{encoded_pwd}@localhost/atmsurvelliance'")
        else:
            print("SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/atmsurvelliance'")
        
        print("\nNext steps:")
        print("1. Update config.py with the connection string above")
        print("2. Run: python backend/setup_database.py")
        print("3. Run: python backend/app.py")
    else:
        print("\nFAILED: Could not set up PostgreSQL")
        print("\nManual steps:")
        print("1. Open pgAdmin or psql")
        print("2. Connect to PostgreSQL")
        print("3. Create database 'atmsurvelliance'")
        print("4. Update config.py with correct connection string")

if __name__ == "__main__":
    main()
