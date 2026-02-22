# Centralized AI-Based Lost and Found Information System for SEAIT

A production-ready Flask web application for managing lost and found items at South East Asian Institute of Technology (SEAIT).

## Features

- **Role-Based Access Control**: Admin, Staff, and Student roles with appropriate permissions
- **Lost Item Reporting**: Students can report lost items with images and details
- **Found Item Logging**: Staff can log found items with categorization and storage tracking
- **AI Matching**: Intelligent matching algorithm using TF-IDF, keyword matching, and category/color comparison
- **QR Code Claims**: Generate and verify QR codes for item claims
- **Notifications**: Real-time notifications for matches and status updates
- **Dashboards**: Separate dashboards for Admin, Staff, and Students
- **Reports**: Monthly statistics and CSV export functionality

## Tech Stack

- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Jinja2 templates, Bootstrap 5, JavaScript
- **AI Matching**: scikit-learn (TF-IDF, cosine similarity)
- **QR Codes**: qrcode library

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional):
```bash
# For PostgreSQL (production)
export DATABASE_URL=postgresql://user:password@localhost/lost_found_db

# For development (SQLite will be used by default)
# No DATABASE_URL needed
```

5. **Initialize the database**:
```bash
# Run migrations (if using Flask-Migrate)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or seed with sample data
python seed_data.py
```

6. **Run the application**:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Default Login Credentials

After running `seed_data.py`:

- **Admin**: admin@seait.edu / admin123
- **Staff**: staff@seait.edu / staff123
- **Student**: student1@seait.edu / student123

## Project Structure

```
app/
├── __init__.py          # Application factory
├── models/              # Database models
│   ├── user.py
│   ├── lost_item.py
│   ├── found_item.py
│   ├── match.py
│   ├── claim.py
│   └── notification.py
├── routes/              # Blueprint routes
│   ├── auth.py
│   ├── user.py
│   ├── staff.py
│   ├── admin.py
│   └── api.py
├── services/            # Business logic services
│   ├── lost_found_matcher.py
│   ├── notification_service.py
│   └── qr_service.py
├── templates/           # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── user/
│   ├── staff/
│   └── admin/
├── static/              # Static files (CSS, JS, images)
│   └── uploads/         # Uploaded images
└── utils/               # Utility functions
    └── helpers.py
config.py                # Configuration
run.py                   # Application entry point
seed_data.py             # Database seeding script
requirements.txt         # Python dependencies
Procfile                # Deployment configuration
```

## AI Matching Algorithm

The matching system uses multiple techniques:

1. **TF-IDF Text Similarity** (30% weight): Compares item descriptions using cosine similarity
2. **Keyword Matching** (30% weight): Matches keywords from item names and descriptions
3. **Category & Color Matching** (30% weight): Exact and partial matches for category and color
4. **Image Matching** (10% weight): Placeholder for future computer vision implementation

Matches with scores ≥ 50% are automatically suggested to users.

## Deployment

### Heroku

1. Create a Heroku app
2. Set environment variables:
```bash
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```
3. Deploy:
```bash
git push heroku main
```

### Other Platforms

The application is compatible with any WSGI server (Gunicorn, uWSGI, etc.) and supports PostgreSQL for production databases.

## Security Features

- Password hashing with Werkzeug
- Role-based access control decorators
- File upload validation
- CSRF protection (Flask-WTF recommended for production)
- Secure session handling

## API Endpoints

- `GET /api/lost-items` - Get user's lost items (authenticated)
- `GET /api/found-items` - Get all found items (staff/admin only)
- `GET /api/matches/<lost_item_id>` - Get matches for a lost item

## License

This project is developed for SEAIT (South East Asian Institute of Technology).

## Support

For issues or questions, please contact the development team.
