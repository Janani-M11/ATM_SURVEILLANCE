# 🚀 PostgreSQL Quick Start

## Fast Setup (3 Commands)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
Create a file named `.env` in the `miniproject` folder:

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_NAME=atm_surveillance
```

**Replace `your_postgres_password` with your actual PostgreSQL password.**

### 3. Run Setup
```bash
python setup_postgres.py
```

Or use the batch file:
```bash
setup_postgres.bat
```

---

## ✅ Verify It Works

Start the backend:
```bash
python backend/app.py
```

If you see no database errors, PostgreSQL is configured correctly!

---

## 📝 Need Help?

See **POSTGRESQL_SETUP_GUIDE.md** for detailed instructions.

---

## 🔄 Switch Back to SQLite

In `.env` file, change:
```env
DB_TYPE=sqlite
```

Or remove the `.env` file and use:
```env
DATABASE_URL=sqlite:///atm_surveillance.db
```

