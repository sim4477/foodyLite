# 🍕 Food Delivery Web App (Lite Version)

A Django-based food delivery application with real-time chat functionality, role-based authentication, and PostgreSQL database support.

## 🚀 Features

### User Roles & Authentication
- **Customer**: Login via mobile number & OTP (static OTP: 1234)
  - Create new bookings
  - View bookings
  - Cancel bookings
  - Real-time chat with delivery partner when assigned

- **Delivery Partner**: Login and view assigned bookings
  - Update booking status: Start → Reached → Collected → Delivered
  - Real-time chat with customers

- **Admin**: Login and view all bookings
  - Assign bookings to delivery partners
  - Monitor all booking activities

### Core Features
- ✅ OTP-based authentication with static OTP (1234)
- ✅ Role-based access control
- ✅ Real-time chat using Django Channels and WebSockets
- ✅ Booking management system
- ✅ Status tracking for deliveries
- ✅ PostgreSQL database integration
- ✅ Responsive UI with jQuery
- ✅ Admin panel for booking assignment

## 🛠️ Tech Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL
- **Real-time Communication**: Django Channels + Redis
- **Frontend**: HTML, CSS, JavaScript, jQuery, Bootstrap
- **Authentication**: Custom OTP-based system
- **Deployment Ready**: Gunicorn, WhiteNoise

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis Server
- Git

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd food_delivery_app_with_reusable_functions

# Run the automated setup script
./setup.sh
```

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib redis-server python3-pip python3-venv

# CentOS/RHEL
sudo yum install postgresql postgresql-server redis python3-pip
```

#### 2. Setup Database
```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -f setup_database.sql
```

#### 3. Setup Application
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create test data
python manage.py create_test_users

# Collect static files
python manage.py collectstatic --noinput
```

## 🏃‍♂️ Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the development server
cd backend
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000

## 👤 Test Users

Use OTP **1234** for all test users:

| Role | Mobile Number | Username |
|------|---------------|----------|
| Customer | 9999999999 | customer1 |
| Customer | 8888888888 | customer2 |
| Delivery Partner | 7777777777 | delivery1 |
| Delivery Partner | 6666666666 | delivery2 |
| Admin | 5555555555 | admin1 |

## 📱 User Workflows

### Customer Workflow
1. Login with mobile number + OTP (1234)
2. Create a new booking with food details and addresses
3. View booking status and details
4. Chat with delivery partner when assigned
5. Cancel booking if needed (before assignment)

### Delivery Partner Workflow
1. Login with mobile number + OTP (1234)
2. View assigned bookings
3. Update delivery status (Start → Reached → Collected → Delivered)
4. Chat with customers for coordination

### Admin Workflow
1. Login with mobile number + OTP (1234)
2. View all bookings
3. Assign pending bookings to delivery partners
4. Monitor overall system activity

## 🗂️ Project Structure

```
food_delivery_app_with_reusable_functions/
├── backend/
│   ├── apps/
│   │   ├── authentication/     # User authentication & OTP
│   │   ├── booking/           # Booking management
│   │   ├── chat/              # Real-time chat system
│   │   └── common/            # Shared utilities
│   ├── food_delivery/         # Main Django project
│   │   ├── settings/          # Environment-specific settings
│   │   └── urls.py           # URL routing
│   └── manage.py
├── frontend/
│   ├── static/               # CSS, JS, images
│   └── templates/            # HTML templates
├── setup.sh                 # Automated setup script
├── setup_database.sql       # Database setup
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://fooddelivery_user:fooddelivery_pass@localhost:5432/food_delivery_db

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:8000
```

## 🚀 Deployment

### Heroku Deployment
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables in Heroku dashboard
4. Deploy: `git push heroku main`

### PythonAnywhere Deployment
1. Upload code to PythonAnywhere
2. Create virtual environment and install requirements
3. Configure database settings
4. Set up static files and WSGI configuration

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication
python manage.py test apps.booking
python manage.py test apps.chat
```

## 📊 Database Schema

### Key Models
- **User**: Custom user model with role-based authentication
- **Booking**: Food delivery bookings with status tracking
- **ChatRoom**: Chat rooms for customer-delivery partner communication
- **ChatMessage**: Individual chat messages
- **OTP**: OTP verification system

## 🔒 Security Features

- OTP-based authentication
- Role-based access control
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure session management

## 📈 Performance Features

- Database query optimization
- Static file compression
- Caching with Redis
- Pagination for large datasets
- WebSocket connection management

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env`

2. **Redis Connection Error**
   - Ensure Redis is running: `sudo systemctl status redis-server`
   - Check Redis URL configuration

3. **Static Files Not Loading**
   - Run: `python manage.py collectstatic --noinput`
   - Check STATIC_ROOT and STATIC_URL settings

4. **WebSocket Connection Failed**
   - Ensure Redis is running
   - Check CHANNEL_LAYERS configuration
   - Verify ASGI application setup

## 📝 API Endpoints

### Authentication
- `POST /auth/api/send-otp/` - Send OTP to mobile number
- `POST /auth/api/verify-otp/` - Verify OTP and login
- `GET /auth/api/profile/` - Get user profile

### Booking Management
- `GET /booking/` - List user bookings
- `POST /booking/create/` - Create new booking
- `GET /booking/<id>/` - Get booking details
- `POST /booking/<id>/cancel/` - Cancel booking
- `POST /booking/<id>/update-status/` - Update delivery status
- `POST /booking/assign/<id>/` - Assign booking to delivery partner

### Chat System
- `GET /chat/room/<booking_id>/` - Chat room interface
- `GET /chat/api/messages/<booking_id>/` - Get chat messages
- `WebSocket /ws/chat/<booking_id>/` - Real-time chat

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created as part of a Django development assessment.

---

**Note**: This is a lite version of a food delivery application designed for demonstration purposes. For production use, additional features like payment integration, restaurant management, and advanced security measures would be required.