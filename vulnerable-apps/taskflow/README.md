# TaskFlow - Subtly Flawed Project Management App

A modern project management application built with Node.js/Express, React, and PostgreSQL. Contains subtle logic-based vulnerabilities for security testing.

## Setup Instructions

1. **Prerequisites:**
   - Node.js 16+ and npm
   - PostgreSQL 12+
   - Git

2. **Database Setup:**
   ```bash
   # Create database
   createdb taskflow
   
   # Run migrations
   npm run migrate
   ```

3. **Installation:**
   ```bash
   npm install
   ```

4. **Configuration:**
   - Update database connection in `config/database.js`
   - Set JWT secret in `.env` file
   - Default: host=localhost, port=5432, database=taskflow

5. **Launch:**
   ```bash
   # Start backend
   npm run dev
   
   # In another terminal, start frontend
   cd client
   npm start
   ```

6. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Admin Dashboard: http://localhost:3000/admin

## Default Credentials
- **Regular User:** email: `user@test.com`, password: `password123`
- **Admin User:** email: `admin@test.com`, password: `admin123`

## Known Vulnerabilities
- **IDOR (Insecure Direct Object Reference):** Can access any task by ID
- **Broken Access Control:** Any authenticated user can access admin dashboard
- **Information Disclosure:** Full error stack traces exposed
- **Missing Input Validation:** No rate limiting or input sanitization
- **Weak Session Management:** JWT tokens don't expire

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/:id` - Get specific task (IDOR vulnerable)
- `GET /api/admin/dashboard` - Admin dashboard (access control issue)

**WARNING: This application contains intentional vulnerabilities for security testing purposes only.**
