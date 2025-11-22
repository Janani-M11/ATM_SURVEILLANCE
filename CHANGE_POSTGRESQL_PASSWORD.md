# 🔑 How to Change PostgreSQL Password

## Method 1: Using psql Command Line (Recommended)

### Step 1: Open psql as postgres user
```bash
psql -U postgres
```

If it asks for a password and you don't know it, try:
```bash
psql -U postgres -h localhost
```

### Step 2: Change the password
Once connected, run:
```sql
ALTER USER postgres WITH PASSWORD 'your_new_password';
```

Replace `your_new_password` with your desired password.

### Step 3: Exit psql
```sql
\q
```

---

## Method 2: Using Windows Command Prompt

### Step 1: Open Command Prompt as Administrator

### Step 2: Navigate to PostgreSQL bin directory
```bash
cd "C:\Program Files\PostgreSQL\17\bin"
```
*(Adjust version number if different)*

### Step 3: Run psql
```bash
psql -U postgres
```

### Step 4: Change password
```sql
ALTER USER postgres WITH PASSWORD 'your_new_password';
\q
```

---

## Method 3: Using pgAdmin (GUI Method)

1. **Open pgAdmin** (usually in Start Menu)

2. **Connect to PostgreSQL server**
   - Right-click on "PostgreSQL 17" (or your version)
   - Select "Connect Server"
   - Enter current password (or leave blank if none)

3. **Navigate to Login/Group Roles**
   - Expand "Servers" → "PostgreSQL 17"
   - Expand "Login/Group Roles"
   - Right-click on "postgres"
   - Select "Properties"

4. **Change password**
   - Go to "Definition" tab
   - Enter new password in "Password" field
   - Click "Save"

---

## Method 4: Using SQL File (If you can't connect)

### Step 1: Create a password file
Create a file `change_password.sql`:
```sql
ALTER USER postgres WITH PASSWORD 'your_new_password';
```

### Step 2: Run it
```bash
psql -U postgres -f change_password.sql
```

---

## Method 5: Reset Password via pg_hba.conf (If you forgot password)

### Step 1: Find pg_hba.conf file
Location is usually:
```
C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

### Step 2: Edit pg_hba.conf
1. **Backup the file first!**
2. Open in Notepad (as Administrator)
3. Find the line:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```
4. Change to:
   ```
   host    all             all             127.0.0.1/32            trust
   ```
5. Save the file

### Step 3: Restart PostgreSQL service
```bash
# Stop service
net stop postgresql-x64-17

# Start service
net start postgresql-x64-17
```
*(Adjust version number)*

### Step 4: Connect without password and change it
```bash
psql -U postgres
ALTER USER postgres WITH PASSWORD 'your_new_password';
\q
```

### Step 5: Restore pg_hba.conf
Change back to `scram-sha-256` and restart PostgreSQL.

---

## Method 6: Quick PowerShell Script

Save this as `change_postgres_password.ps1`:

```powershell
# Change PostgreSQL Password Script
$newPassword = Read-Host "Enter new PostgreSQL password" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($newPassword))

$sql = "ALTER USER postgres WITH PASSWORD '$plainPassword';"

Write-Host "Connecting to PostgreSQL..."
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c $sql

Write-Host "Password changed successfully!"
```

Run it:
```powershell
.\change_postgres_password.ps1
```

---

## After Changing Password

### Update your .env file:
```env
DB_PASSWORD=your_new_password
```

### Test the connection:
```bash
python setup_postgres.py
```

---

## Troubleshooting

### "Password authentication failed"
- Make sure PostgreSQL service is running
- Verify you're using the correct username
- Check if password has special characters (may need URL encoding)

### "Connection refused"
- PostgreSQL service might not be running
- Check service status: `Get-Service | Where-Object {$_.Name -like "*postgres*"}`

### "psql: command not found"
- Add PostgreSQL bin to PATH, or use full path:
  ```
  "C:\Program Files\PostgreSQL\17\bin\psql.exe"
  ```

### Special Characters in Password
If your password contains special characters like `@`, `!`, `#`, etc., you may need to:
- URL-encode them in connection strings: `@` = `%40`, `!` = `%21`
- Or use quotes in SQL: `ALTER USER postgres WITH PASSWORD 'your@pass!word';`

---

## Quick Reference

**Most Common Method:**
```bash
psql -U postgres
ALTER USER postgres WITH PASSWORD 'newpassword';
\q
```

**Update .env after:**
```env
DB_PASSWORD=newpassword
```

---

**Need Help?** Make sure PostgreSQL service is running before attempting password change.

