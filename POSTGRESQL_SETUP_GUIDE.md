# 🐘 PostgreSQL Setup Guide - ATM Surveillance System

This guide will help you migrate from SQLite to PostgreSQL or set up PostgreSQL from scratch.

---

## 📋 Prerequisites

1. **PostgreSQL Installed**
   - Download from: https://www.postgresql.org/download/
   - Windows: Use PostgreSQL Installer
   - Verify installation: `psql --version`

2. **PostgreSQL Service Running**
   - Windows: Check Services (services.msc) for "postgresql-x64-XX"
   - Or run: `pg_ctl status` (in PostgreSQL bin directory)

3. **PostgreSQL Credentials**
   - Default user: `postgres`
   - You'll need your PostgreSQL password

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install PostgreSQL Driver

```bash
pip install psycopg2-binary
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root (`miniproject/.env`):

```env
# Database Type
DB_TYPE=postgresql

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_NAME=atm_surveillance
```

**Or use DATABASE_URL directly:**
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/atm_surveillance
```

**Note:** If your password contains special characters, URL-encode them:
- `@` → `%40`
- `!` → `%21`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`

Example: `password@123` → `password%40123`

### Step 3: Setup Database

Run the PostgreSQL setup script:

```bash
python setup_postgres.py
```

This will:
- ✅ Test PostgreSQL connection
- ✅ Create database `atm_surveillance`
- ✅ Create all required tables
- ✅ Create admin user (admin@atm.com / admin123)
- ✅ Insert sample data (optional)

---

## 📝 Manual Setup (Alternative)

If the automated script doesn't work, follow these manual steps:

### 1. Create Database

Open PostgreSQL command line or pgAdmin:

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE atm_surveillance;

-- Connect to the new database
\c atm_surveillance
```

### 2. Create Tables

Run these SQL commands:

```sql
-- Admin table
CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event log table
CREATE TABLE event_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255)
);

-- Detection stats table
CREATE TABLE detection_stats (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE UNIQUE,
    people_count INTEGER DEFAULT 0,
    helmet_violations INTEGER DEFAULT 0,
    face_cover_violations INTEGER DEFAULT 0,
    loitering_events INTEGER DEFAULT 0,
    posture_violations INTEGER DEFAULT 0
);

-- Create indexes
CREATE INDEX idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX idx_event_log_type ON event_log(event_type);
CREATE INDEX idx_detection_stats_date ON detection_stats(date);
```

### 3. Create Admin User

The setup script will do this automatically, or you can use the Flask app which creates it on first run.

---

## 🔧 Configuration Options

### Option 1: Environment Variables (.env file)

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=mypassword
DB_NAME=atm_surveillance
```

### Option 2: Direct DATABASE_URL

```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/atm_surveillance
```

### Option 3: Remote PostgreSQL

```env
DB_HOST=192.168.1.100
DB_PORT=5432
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=atm_surveillance
```

Or:
```env
DATABASE_URL=postgresql://myuser:mypassword@192.168.1.100:5432/atm_surveillance
```

---

## ✅ Verification

### Test Database Connection

```python
python -c "from backend.config import Config; print(Config.SQLALCHEMY_DATABASE_URI)"
```

### Test Setup Script

```bash
python setup_postgres.py
```

### Test Backend Connection

Start the backend:
```bash
python backend/app.py
```

Check the console for database connection messages.

---

## 🔄 Switching Between SQLite and PostgreSQL

### Use PostgreSQL (Default)
```env
DB_TYPE=postgresql
```

### Use SQLite (Fallback)
```env
DB_TYPE=sqlite
```

Or remove `DB_TYPE` and set:
```env
DATABASE_URL=sqlite:///atm_surveillance.db
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
- **Solution:** Check if PostgreSQL service is running
  - Windows: `net start postgresql-x64-XX`
  - Linux: `sudo systemctl start postgresql`

### Issue: "Authentication failed"
- **Solution:** Check username and password in `.env` file
- **Solution:** Verify PostgreSQL user exists:
  ```sql
  SELECT * FROM pg_user WHERE usename = 'postgres';
  ```

### Issue: "Database does not exist"
- **Solution:** Run `python setup_postgres.py` to create database

### Issue: "psycopg2 module not found"
- **Solution:** Install it: `pip install psycopg2-binary`

### Issue: "Permission denied"
- **Solution:** Ensure PostgreSQL user has CREATE DATABASE permission
- **Solution:** Run as PostgreSQL superuser

### Issue: "Port 5432 already in use"
- **Solution:** Check if another PostgreSQL instance is running
- **Solution:** Change port in `.env`: `DB_PORT=5433`

---

## 📊 Database Differences (SQLite vs PostgreSQL)

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Primary Key | INTEGER PRIMARY KEY AUTOINCREMENT | SERIAL PRIMARY KEY |
| Auto Increment | AUTOINCREMENT | SERIAL |
| Timestamp | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |
| Date | DATE DEFAULT CURRENT_DATE | DATE DEFAULT CURRENT_DATE |
| UNIQUE Constraint | UNIQUE(date) | UNIQUE(date) |
| Connection | File-based | Network-based |
| Performance | Good for small apps | Excellent for production |
| Scalability | Limited | High |

---

## 🎯 Quick Start Checklist

- [ ] PostgreSQL installed and running
- [ ] `.env` file created with PostgreSQL credentials
- [ ] `psycopg2-binary` installed (`pip install -r requirements.txt`)
- [ ] Database created (`python setup_postgres.py`)
- [ ] Backend starts without errors (`python backend/app.py`)
- [ ] Frontend connects to backend successfully
- [ ] Can login with admin@atm.com / admin123

---

## 📚 Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- SQLAlchemy PostgreSQL: https://docs.sqlalchemy.org/en/14/dialects/postgresql.html

---

**Need Help?** Check the main README.md or run `python setup_postgres.py` for automated setup.

