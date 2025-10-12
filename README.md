# Remit - Resource Management System

[![Version](https://img.shields.io/badge/version-0.0.1.22-blue.svg)](https://github.com/michaelbag/remit/releases/tag/v0.0.1.22)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-orange.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

A comprehensive Django-based resource management system for tracking equipment, services, employees, and organizational resources with advanced admin interface and API capabilities.

## 🚀 Features

### Core Functionality
- **Equipment Management**: Track equipment models, types, and configurations
- **Service Management**: Manage services associated with equipment
- **Resource Management**: Handle organizational resources with advanced filtering
- **Employee Management**: Track employees with department and organization relationships
- **QR Code Integration**: Generate and manage QR codes for equipment and resources

### Admin Interface Enhancements
- **Advanced Autocomplete**: Smart filtering for all relationship fields
- **Custom Forms**: Enhanced forms with virtual fields and validation
- **GUID Management**: Copy-to-clipboard functionality for system identifiers
- **Internationalization**: Full i18n support with translation-ready strings
- **Responsive Design**: Modern, mobile-friendly admin interface

### API Capabilities
- **RESTful API**: Complete API for all resources
- **Authentication**: Token-based authentication
- **Custom Endpoints**: Specialized endpoints for specific use cases
- **Documentation**: Comprehensive API documentation

## 🛠️ Technology Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: Django Admin with custom JavaScript
- **API**: Django REST Framework
- **Autocomplete**: django-autocomplete-light
- **Authentication**: Django's built-in authentication system

## 📋 Requirements

- Python 3.13+
- Django 5.2.7
- django-autocomplete-light
- django-rest-framework
- Pillow (for image handling)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/michaelbag/remit.git
cd remit
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

## 📁 Project Structure

```
remit/
├── apps/
│   ├── acc/                 # Access management
│   ├── equipment/           # Equipment management
│   ├── org/                 # Organization management
│   ├── qr/                  # QR code management
│   ├── res/                 # Resource management
│   └── service/             # Service management
├── api/                     # REST API
├── common/                  # Common utilities
├── config/                  # Configuration management
├── static/                  # Static files
├── templates/               # HTML templates
└── remit/                   # Main project settings
```

## 🔧 Configuration

### Environment Variables
Create a `local_settings.py` file based on `local_settings_example.py`:

```python
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security settings
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 📚 API Documentation

### Authentication
All API endpoints require authentication. Use token authentication:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     https://your-domain.com/api/endpoint/
```

### Key Endpoints

#### QR Codes Modified Count
Get count of QR codes modified since a specific datetime:

```bash
GET /api/qr-codes/modified-count/?since=2024-01-01T00:00:00Z
```

**Response:**
```json
{
    "count": 5,
    "since": "2024-01-01T00:00:00+00:00",
    "message": "Found 5 QR codes modified since 2024-01-01T00:00:00+00:00"
}
```

#### Equipment Management
- `GET /api/equipment/` - List all equipment
- `POST /api/equipment/` - Create new equipment
- `GET /api/equipment/{id}/` - Get specific equipment
- `PUT /api/equipment/{id}/` - Update equipment
- `DELETE /api/equipment/{id}/` - Delete equipment

#### Resource Management
- `GET /api/resources/` - List all resources
- `POST /api/resources/` - Create new resource
- `GET /api/resources/{id}/` - Get specific resource
- `PUT /api/resources/{id}/` - Update resource
- `DELETE /api/resources/{id}/` - Delete resource

## 🎯 Key Features

### Advanced Autocomplete
All relationship fields feature intelligent autocomplete with filtering:

- **Employee Selection**: Filtered by active status and organization
- **Service Selection**: Filtered by equipment and active status
- **Resource Selection**: Filtered by category, type, and active status
- **Equipment Selection**: Filtered by type and active status

### Security Features
- **Authentication Required**: All autocomplete endpoints require login
- **Parameter Validation**: Input validation for all API endpoints
- **Service Validation**: Additional security checks for service-based filtering
- **Graceful Error Handling**: Safe handling of invalid parameters

### Admin Interface
- **Custom Forms**: Enhanced forms with virtual fields
- **GUID Copy Button**: One-click copying of system identifiers
- **Visual Indicators**: Clear distinction between form-only and database fields
- **Responsive Design**: Works on all device sizes

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Run specific app tests:

```bash
python manage.py test apps.res
python manage.py test api
```

## 📦 Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email settings
5. Set up SSL/HTTPS

### Docker Support
```bash
docker build -t remit .
docker run -p 8000:8000 remit
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Changelog

### Version 0.0.1.22
- Enhanced admin interface and autocomplete functionality
- Added autocomplete for employee, service, and accounts_from fields
- Implemented GUID copy button in ExtSystem admin
- Made category field mandatory in ResourceType
- Added virtual form_only_equipment field for equipment selection
- Refactored views structure for equipment app
- Enhanced security in autocomplete views
- Fixed RelatedObjectDoesNotExist error for new resources
- Added internationalization support
- Improved JavaScript error handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Michael Bag** - *Initial work* - [michaelbag](https://github.com/michaelbag)

## 🙏 Acknowledgments

- Django community for the excellent framework
- django-autocomplete-light for the autocomplete functionality
- Django REST Framework for API capabilities

## 📞 Support

For support, email support@example.com or create an issue in the GitHub repository.

---

**Made with ❤️ using Django**
