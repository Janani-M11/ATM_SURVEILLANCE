import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'atm-surveillance-secret-key-2024-very-secure')
    
    # Database configuration - supports both PostgreSQL and SQLite
    DB_TYPE = os.getenv('DB_TYPE', 'postgresql').lower()  # 'postgresql' or 'sqlite'
    
    if DB_TYPE == 'postgresql':
        # PostgreSQL configuration
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_NAME = os.getenv('DB_NAME', 'atm_surveillance')
        
        # Construct PostgreSQL connection string
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        # SQLite configuration (fallback)
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///atm_surveillance.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False