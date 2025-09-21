-- Sample data for Bloggit
-- WARNING: Passwords are stored in plain text for testing purposes

-- Insert sample users
INSERT INTO users (username, password) VALUES 
('admin', 'password123'),
('user1', 'userpass'),
('testuser', 'testpass'),
('john', 'john123'),
('jane', 'jane456');

-- Insert sample posts
INSERT INTO posts (title, content) VALUES 
('Welcome to Bloggit', 'This is the first post on our vulnerable blog. Feel free to explore and test the security features!'),
('Security Testing', 'This blog is designed for security testing. It contains various vulnerabilities that can be exploited for educational purposes.'),
('SQL Injection Demo', 'This post demonstrates how SQL injection can be used to bypass authentication and access sensitive data.'),
('XSS Vulnerabilities', 'Cross-site scripting (XSS) vulnerabilities allow attackers to inject malicious scripts into web pages viewed by other users.'),
('Web Security Basics', 'Understanding web security vulnerabilities is crucial for developers. This blog serves as a practical example of common security issues.');

-- Insert sample comments
INSERT INTO comments (post_id, comment_text, author) VALUES 
(1, 'Great first post! Looking forward to more content.', 'user1'),
(1, 'This is a test comment to demonstrate stored XSS vulnerabilities.', 'testuser'),
(2, 'Security testing is so important in web development.', 'john'),
(2, 'I found some interesting vulnerabilities in this application.', 'jane'),
(3, 'SQL injection is one of the most common web vulnerabilities.', 'admin'),
(4, 'XSS attacks can be very dangerous if not properly handled.', 'user1'),
(5, 'Thanks for sharing this educational content!', 'testuser');
