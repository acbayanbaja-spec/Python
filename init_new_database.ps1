# PowerShell script to initialize the new database
# Run this to set up tables and seed data

Write-Host "Initializing new database..." -ForegroundColor Green

# Set DATABASE_URL
$env:DATABASE_URL = "postgresql://seait_lost_and_found_ydec_user:IvpfRg6Q8vUym4ERmTVimnA4vNx0Ufmk@dpg-d6dgbji4d50c73apeilg-a.singapore-postgres.render.com:5432/seait_lost_and_found_ydec"

Write-Host "Testing connection..." -ForegroundColor Yellow
python connect_render_db.py

Write-Host "`nCreating database tables..." -ForegroundColor Yellow
flask db upgrade

Write-Host "`nSeeding database with initial data..." -ForegroundColor Yellow
python seed_data.py

Write-Host "`nDone! Database initialized successfully." -ForegroundColor Green
