# Quick Start Guide

## Initial Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Initialize database with sample data**:
```bash
python seed_data.py
```

3. **Run the application**:
```bash
python run.py
```

4. **Access the application**:
- Open browser: http://localhost:5000
- Login with one of the seeded accounts

## Default Accounts

- **Admin**: admin@seait.edu / admin123
- **Staff**: staff@seait.edu / staff123  
- **Student**: student1@seait.edu / student123

## Key Features to Test

### As Student:
1. Login and go to dashboard
2. Report a lost item (Report Lost Item)
3. View matches when staff logs matching found items
4. Confirm matches and generate QR codes
5. View notifications

### As Staff:
1. Login and go to dashboard
2. Log found items (Log Found Item)
3. View high priority items (ID, Wallet, Phone)
4. Verify QR claim codes (Verify Claim)
5. Release items to users

### As Admin:
1. Login and go to dashboard
2. View system statistics
3. Manage users (Users → Create New User)
4. View reports and export data (Reports)
5. Monitor all matches and claims

## Database

- **Development**: Uses SQLite (lost_found.db) by default
- **Production**: Set `DATABASE_URL` environment variable for PostgreSQL

## Troubleshooting

- **Import errors**: Make sure you're in the project root directory
- **Database errors**: Run `python seed_data.py` to initialize
- **Port already in use**: Change port in `run.py` or set `PORT` environment variable
