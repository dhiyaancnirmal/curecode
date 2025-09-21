-- Sample data for Bloggit

-- Insert sample users
INSERT INTO users (username, password) VALUES 
('admin', 'password123'),
('user1', 'userpass'),
('testuser', 'testpass'),
('john', 'john123'),
('jane', 'jane456');

-- Insert sample posts
INSERT INTO posts (title, content) VALUES 
('Welcome to Bloggit', 'This is the first post on our blog. We share thoughts, insights, and stories here.'),
('Technology Trends', 'Exploring the latest trends in web development and technology.'),
('Web Development Tips', 'Useful tips and tricks for modern web development.'),
('XSS Vulnerabilities', 'Cross-site scripting (XSS) vulnerabilities allow attackers to inject malicious scripts into web pages viewed by other users.'),
('Web Security Basics', 'Understanding web security vulnerabilities is crucial for developers. This blog serves as a practical example of common security issues.');

-- Insert sample comments
INSERT INTO comments (post_id, comment_text, author) VALUES 
(1, 'Great first post! Looking forward to more content.', 'user1'),
(1, 'Great post! Looking forward to reading more content.', 'testuser'),
(2, 'Very informative article, thanks for sharing.', 'john'),
(2, 'I found some interesting vulnerabilities in this application.', 'jane'),
(3, 'SQL injection is one of the most common web vulnerabilities.', 'admin'),
(4, 'XSS attacks can be very dangerous if not properly handled.', 'user1'),
(5, 'Thanks for sharing this educational content!', 'testuser');
