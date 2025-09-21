# SecureCart - Secure E-commerce Application

A professional e-commerce prototype built with Django following security best practices. This application serves as a baseline for testing false positives in security scanning tools.

## Setup Instructions

1. **Prerequisites:**
   - Python 3.8+
   - PostgreSQL 12+
   - pip and virtualenv

2. **Virtual Environment Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Installation:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup:**
   ```bash
   # Create database
   createdb securecart
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Load sample data
   python manage.py loaddata fixtures/sample_data.json
   ```

5. **Configuration:**
   - Update database settings in `securecart/settings.py` if needed
   - Set `SECRET_KEY` in environment variables
   - Default: host=localhost, port=5432, database=securecart

6. **Launch:**
   ```bash
   python manage.py runserver
   ```

7. **Access:**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - User profile: http://localhost:8000/profile (requires login)

## Default Credentials
- **Admin:** Use `python manage.py createsuperuser` to create
- **Test User:** email: `test@example.com`, password: `testpass123`

## Security Features Implemented
- **SQL Injection Prevention:** Django ORM used exclusively
- **XSS Prevention:** Automatic HTML escaping in templates
- **CSRF Protection:** Built-in CSRF middleware enabled
- **Secure Access Control:** @login_required decorator and user filtering
- **Input Validation:** Django forms with validation
- **Secure Headers:** Security middleware configured
- **Password Security:** Django's built-in password hashing
- **Session Security:** Secure session configuration

## Application Features
- User registration and authentication
- Product catalog with search and filtering
- Shopping cart functionality
- Order management
- User profile with order history
- Admin interface for product management
- Responsive design

## API Endpoints
- `GET /` - Home page with products
- `GET /products/` - Product catalog
- `GET /products/<id>/` - Product detail
- `POST /cart/add/` - Add to cart
- `GET /cart/` - View cart
- `POST /orders/create/` - Create order
- `GET /profile/` - User profile (login required)
- `GET /orders/` - Order history (login required)

**This application is designed to be secure and should not trigger security alerts in properly configured scanning tools.**
