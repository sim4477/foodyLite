#!/bin/bash

# Food Delivery App Setup Script

echo "🍕 Setting up Food Delivery App..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    echo "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "CentOS/RHEL: sudo yum install postgresql postgresql-server"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed. Please install Redis first."
    echo "Ubuntu/Debian: sudo apt-get install redis-server"
    echo "CentOS/RHEL: sudo yum install redis"
    exit 1
fi

echo "✅ PostgreSQL and Redis are installed"

# Start PostgreSQL service
echo "🔄 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Start Redis service
echo "🔄 Starting Redis service..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create database and user
echo "🗄️ Creating database and user..."
sudo -u postgres psql -f setup_database.sql

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing Python requirements..."
cd backend
pip install -r requirements.txt

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create test data
echo "👥 Creating test users and sample data..."
python manage.py create_test_users

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "1. cd backend"
echo "2. python manage.py runserver"
echo ""
echo "👤 Test Users (use OTP: 1234):"
echo "- Customer: 9999999999"
echo "- Customer: 8888888888" 
echo "- Delivery Partner: 7777777777"
echo "- Delivery Partner: 6666666666"
echo "- Admin: 5555555555"
echo ""
echo "🌐 Access the app at: http://127.0.0.1:8000"
