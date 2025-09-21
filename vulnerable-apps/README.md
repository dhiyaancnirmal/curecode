# Vulnerable Applications Testing Suite

This directory contains three web applications designed to test the capabilities of the autopatch security scanning tool. Each application has different security postures and vulnerability types.

## Applications Overview

### 1. Bloggit (Highly Vulnerable)
**Location:** `bloggit/`  
**Tech Stack:** PHP 7.4+, MySQL 5.7+  
**Security Level:** Intentionally Vulnerable

#### Vulnerabilities Implemented:
- **SQL Injection:** Direct string concatenation in all database queries
  - Login form: `$sql = "SELECT * FROM users WHERE username = '" . $_POST['username'] . "'"`
  - Search functionality: `$sql = "SELECT * FROM posts WHERE title LIKE '%" . $search_query . "%'"`
  - Comment retrieval: `$sql = "SELECT * FROM comments WHERE post_id = " . $post['id']`

- **Reflected XSS:** Direct output without sanitization
  - Search results: `echo "<h2>Search results for: " . $_GET['query'] . "</h2>";`

- **Stored XSS:** Unsanitized comment display
  - Comments: `echo $comment['comment_text'];` (no htmlspecialchars)

- **Information Disclosure:** Plain text password storage
- **Missing Input Validation:** No CSRF protection, no input sanitization

#### Testing Capabilities:
- Form-based SQL injection testing
- XSS payload testing in search and comments
- Authentication bypass attempts
- Input validation testing

### 2. TaskFlow (Subtly Flawed)
**Location:** `taskflow/`  
**Tech Stack:** Node.js/Express, React, PostgreSQL  
**Security Level:** Modern but Flawed

#### Vulnerabilities Implemented:
- **IDOR (Insecure Direct Object Reference):**
  - `GET /api/tasks/:taskId` - No ownership verification
  - Any authenticated user can access any task by ID
  - Comments can be added to any task without permission check

- **Broken Access Control:**
  - Admin dashboard accessible to any authenticated user
  - User role changes possible by any authenticated user
  - User deletion possible by any authenticated user

- **Information Disclosure:**
  - Full error stack traces exposed in JSON responses
  - Request body, headers, and user info leaked in errors
  - System information exposed in admin logs endpoint

- **Missing Security Headers:** CSP disabled for development
- **Weak Session Management:** JWT tokens don't expire properly

#### Testing Capabilities:
- API-based IDOR testing
- Privilege escalation testing
- Error handling and information disclosure
- JWT token manipulation
- Admin panel access testing

### 3. SecureCart (Secure by Design)
**Location:** `securecart/`  
**Tech Stack:** Django 4.2, PostgreSQL  
**Security Level:** Secure Implementation

#### Security Features Implemented:
- **SQL Injection Prevention:** Django ORM used exclusively
- **XSS Prevention:** Automatic HTML escaping in templates
- **CSRF Protection:** Built-in CSRF middleware enabled
- **Secure Access Control:** @login_required decorator and user filtering
- **Input Validation:** Django forms with validation
- **Secure Headers:** Security middleware configured
- **Password Security:** Django's built-in password hashing
- **Session Security:** Secure session configuration

#### Testing Capabilities:
- False positive testing
- Secure implementation verification
- Baseline security assessment

## Additional Testing Features

### Browser-Based Testing Capabilities

#### Form Interactions:
- Login forms with various input types
- Registration forms with validation
- Search forms with different parameters
- Comment submission forms
- Product ordering forms
- Admin panel forms

#### Multi-Step Workflows:
- User registration → Login → Profile access
- Product browsing → Cart addition → Checkout
- Task creation → Assignment → Status updates
- Admin panel access → User management

#### Dynamic Content:
- AJAX-based API calls
- Real-time updates
- Pagination and filtering
- File uploads (in SecureCart)

#### Session Management:
- Cookie-based sessions (Bloggit, SecureCart)
- JWT token-based authentication (TaskFlow)
- Session persistence across requests
- Logout functionality

## Vulnerability Categories for Testing

### 1. Injection Attacks
- **SQL Injection:** Bloggit (multiple vectors)
- **NoSQL Injection:** Not implemented (could be added)
- **Command Injection:** Not implemented (could be added)

### 2. Cross-Site Scripting (XSS)
- **Reflected XSS:** Bloggit search functionality
- **Stored XSS:** Bloggit comments
- **DOM-based XSS:** Not implemented (could be added)

### 3. Broken Authentication & Session Management
- **Weak Passwords:** All applications (default credentials)
- **Session Fixation:** Not explicitly implemented
- **JWT Issues:** TaskFlow (no expiration)

### 4. Insecure Direct Object References (IDOR)
- **TaskFlow:** Task access by ID
- **TaskFlow:** Comment access
- **TaskFlow:** User management

### 5. Security Misconfiguration
- **Information Disclosure:** TaskFlow error handling
- **Missing Security Headers:** TaskFlow (CSP disabled)
- **Default Credentials:** All applications

### 6. Sensitive Data Exposure
- **Plain Text Passwords:** Bloggit
- **Error Information:** TaskFlow
- **System Information:** TaskFlow admin logs

### 7. Missing Function Level Access Control
- **Admin Panel Access:** TaskFlow
- **User Role Changes:** TaskFlow
- **Data Deletion:** TaskFlow

### 8. Cross-Site Request Forgery (CSRF)
- **Missing CSRF Protection:** Bloggit, TaskFlow
- **CSRF Protection:** SecureCart (properly implemented)

### 9. Using Components with Known Vulnerabilities
- **Outdated Dependencies:** Could be added
- **Vulnerable Libraries:** Could be added

### 10. Unvalidated Redirects and Forwards
- **Not Implemented:** Could be added

## Recommended Testing Scenarios

### 1. Automated Scanning
- Run autopatch against each application
- Verify detection of known vulnerabilities
- Check for false positives in SecureCart

### 2. Manual Testing
- Test SQL injection payloads in Bloggit
- Attempt IDOR attacks in TaskFlow
- Verify secure implementations in SecureCart

### 3. API Testing
- Test TaskFlow REST API endpoints
- Verify authentication and authorization
- Test error handling and information disclosure

### 4. Form Testing
- Test all input forms across applications
- Verify validation and sanitization
- Test CSRF protection where implemented

## Setup Instructions

Each application has its own README.md with detailed setup instructions:

1. **Bloggit:** Requires PHP, MySQL, web server
2. **TaskFlow:** Requires Node.js, PostgreSQL, npm
3. **SecureCart:** Requires Python, PostgreSQL, pip

## Security Considerations

⚠️ **WARNING:** These applications contain intentional vulnerabilities and should only be used in isolated testing environments. Do not deploy to production or expose to the internet.

## Future Enhancements

### Additional Vulnerabilities to Add:
1. **File Upload Vulnerabilities**
2. **XML External Entity (XXE) Processing**
3. **Insecure Deserialization**
4. **Server-Side Request Forgery (SSRF)**
5. **Business Logic Vulnerabilities**
6. **Race Conditions**
7. **Memory Corruption Issues**

### Additional Testing Tools Needed:
1. **File Upload Testing**
2. **API Fuzzing**
3. **Business Logic Testing**
4. **Performance Testing**
5. **Mobile Application Testing**

This testing suite provides a comprehensive foundation for evaluating security scanning tools and should be expanded based on specific testing requirements.
