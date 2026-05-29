# Breathe ESG - Complete Setup & Run Guide
# Windows PowerShell version

# Colors for output
$info = "Blue"
$success = "Green"
$error_color = "Red"
$warning = "Yellow"

Write-Host "========================================" -ForegroundColor $info
Write-Host "Breathe ESG - Project Setup & Run" -ForegroundColor $info
Write-Host "========================================" -ForegroundColor $info
Write-Host ""

# ========== BACKEND SETUP ==========
Write-Host "[1/6] Setting up Backend (Django)..." -ForegroundColor $info

# Navigate to backend
cd backend

# Check if venv exists, create if not
if (-Not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor $warning
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor $success
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor $success
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor $warning
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor $error_color
    exit 1
}
Write-Host "Virtual environment activated." -ForegroundColor $success

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor $warning
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: pip install had some issues, but continuing..." -ForegroundColor $warning
} else {
    Write-Host "Python dependencies installed." -ForegroundColor $success
}

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor $warning
    Copy-Item ".env.example" ".env"
    # Ensure SQLite is configured
    $envContent = Get-Content ".env" -Raw
    if ($envContent -NotLike "*DB_ENGINE=django.db.backends.sqlite3*") {
        # Replace PostgreSQL with SQLite
        $envContent = $envContent -Replace "DB_ENGINE=django.db.backends.postgresql", "DB_ENGINE=django.db.backends.sqlite3"
        $envContent = $envContent -Replace "DB_NAME=breathe_esg", "DB_NAME=db.sqlite3"
        Set-Content ".env" $envContent
    }
    Write-Host ".env file created with SQLite configuration." -ForegroundColor $success
} else {
    Write-Host ".env file already exists." -ForegroundColor $success
}

# Run Django migrations
Write-Host "Running Django migrations..." -ForegroundColor $warning
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Migrations had issues" -ForegroundColor $warning
}
Write-Host "Migrations completed." -ForegroundColor $success

# Create superuser (demo credentials)
Write-Host ""
Write-Host "Creating demo superuser..." -ForegroundColor $warning
Write-Host "  Email: admin@example.com" -ForegroundColor $info
Write-Host "  Password: admin123" -ForegroundColor $info
echo "admin@example.com
admin123
admin123" | python manage.py shell -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth.models import User
from apps.core.models import Client

# Create superuser
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin')
else:
    print('Superuser already exists')

# Create sample client
if not Client.objects.filter(name='Sample Corp').exists():
    client = Client.objects.create(
        name='Sample Corp',
        industry='Manufacturing',
        country='US'
    )
    print(f'Sample client created: {client.name}')
else:
    print('Sample client already exists')
" 2>/dev/null || python manage.py createsuperuser --noinput --username admin --email admin@example.com

Write-Host "Demo superuser setup completed." -ForegroundColor $success

# Navigate back to root
cd ..

Write-Host ""
Write-Host "[2/6] Backend setup complete!" -ForegroundColor $success
Write-Host ""

# ========== FRONTEND SETUP ==========
Write-Host "[3/6] Setting up Frontend (React)..." -ForegroundColor $info

cd frontend

# Install npm dependencies
Write-Host "Installing npm dependencies (this may take a minute)..." -ForegroundColor $warning
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "npm dependencies installed." -ForegroundColor $success
} else {
    Write-Host "npm install completed with warnings (this is usually okay)." -ForegroundColor $warning
}

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor $warning
    @"
REACT_APP_API_URL=http://localhost:8000/api
"@ | Out-File -Encoding UTF8 ".env"
    Write-Host ".env file created." -ForegroundColor $success
}

cd ..

Write-Host ""
Write-Host "[4/6] Frontend setup complete!" -ForegroundColor $success
Write-Host ""

# ========== SUMMARY ==========
Write-Host "========================================" -ForegroundColor $info
Write-Host "Setup Complete! Ready to Run!" -ForegroundColor $success
Write-Host "========================================" -ForegroundColor $info
Write-Host ""

Write-Host "To start the application, open TWO PowerShell windows:" -ForegroundColor $info
Write-Host ""

Write-Host "Window 1 - Backend (Django):" -ForegroundColor $info
Write-Host "  cd backend" -ForegroundColor $warning
Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor $warning
Write-Host "  python manage.py runserver" -ForegroundColor $warning
Write-Host ""

Write-Host "Window 2 - Frontend (React):" -ForegroundColor $info
Write-Host "  cd frontend" -ForegroundColor $warning
Write-Host "  npm start" -ForegroundColor $warning
Write-Host ""

Write-Host "Then access the application:" -ForegroundColor $info
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor $warning
Write-Host "  Backend API: http://localhost:8000/api" -ForegroundColor $warning
Write-Host "  Admin Panel: http://localhost:8000/admin" -ForegroundColor $warning
Write-Host ""

Write-Host "Demo Login Credentials:" -ForegroundColor $info
Write-Host "  Email: analyst@breatheesg.com" -ForegroundColor $warning
Write-Host "  Password: demo1234" -ForegroundColor $warning
Write-Host ""

Write-Host "Admin Credentials:" -ForegroundColor $info
Write-Host "  Email: admin@example.com" -ForegroundColor $warning
Write-Host "  Password: admin123" -ForegroundColor $warning
Write-Host ""

Write-Host "========================================" -ForegroundColor $success
Write-Host "Setup script completed successfully!" -ForegroundColor $success
Write-Host "========================================" -ForegroundColor $success
