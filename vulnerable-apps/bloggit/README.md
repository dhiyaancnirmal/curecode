# Bloggit - Modern Blog Platform

A modern blog application built with PHP and MySQL for content management and sharing.

## Setup Instructions

1. **Prerequisites:**
   - PHP 7.4+ with MySQL extension
   - MySQL 5.7+ or MariaDB
   - Web server (Apache/Nginx) or PHP built-in server

2. **Database Setup:**
   ```bash
   mysql -u root -p
   CREATE DATABASE bloggit;
   USE bloggit;
   SOURCE schema.sql;
   SOURCE sample_data.sql;
   ```

3. **Configuration:**
   - Update database credentials in `config.php` if needed
   - Default: host=localhost, user=root, password=, database=bloggit

4. **Launch:**
   ```bash
   # Using PHP built-in server
   php -S localhost:8000
   
   # Or configure your web server to serve this directory
   ```

5. **Access:**
   - Main page: http://localhost:8000
   - Login: http://localhost:8000/login.php

## Default Credentials
- Username: `admin`
- Password: `password123`

## Known Vulnerabilities
- SQL Injection in login, search, and post retrieval
- Reflected XSS in search results
- Stored XSS in comments
- No input validation or sanitization
- Plain text password storage

**Note: This application is designed for educational and development purposes.**
