const bcrypt = require('bcryptjs');
const pool = require('../database/connection');

const seedData = async () => {
  try {
    // Hash passwords
    const userPassword = await bcrypt.hash('password123', 10);
    const adminPassword = await bcrypt.hash('admin123', 10);
    const testPassword = await bcrypt.hash('testpass', 10);

    // Insert users
    const users = await pool.query(`
      INSERT INTO users (email, password_hash, role) VALUES 
      ('user@test.com', $1, 'user'),
      ('admin@test.com', $2, 'admin'),
      ('test@example.com', $3, 'user'),
      ('john@doe.com', $1, 'user'),
      ('jane@smith.com', $1, 'user')
      ON CONFLICT (email) DO NOTHING
      RETURNING id, email, role
    `, [userPassword, adminPassword, testPassword]);

    console.log('Users seeded:', users.rows.length);

    // Get user IDs
    const userResult = await pool.query('SELECT id, email FROM users ORDER BY id');
    const usersById = {};
    userResult.rows.forEach(user => {
      usersById[user.email] = user.id;
    });

    // Insert projects
    const projects = await pool.query(`
      INSERT INTO projects (user_id, name, description, status) VALUES 
      ($1, 'Website Redesign', 'Complete overhaul of company website', 'active'),
      ($2, 'Mobile App Development', 'Build iOS and Android apps', 'active'),
      ($3, 'Database Migration', 'Migrate from MySQL to PostgreSQL', 'pending'),
      ($1, 'Security Audit', 'Comprehensive security review', 'active'),
      ($4, 'Marketing Campaign', 'Q4 marketing strategy', 'active')
      RETURNING id
    `, [
      usersById['user@test.com'],
      usersById['admin@test.com'],
      usersById['test@example.com'],
      usersById['john@doe.com']
    ]);

    console.log('Projects seeded:', projects.rows.length);

    // Insert tasks
    const tasks = await pool.query(`
      INSERT INTO tasks (user_id, title, description, status, priority, due_date) VALUES 
      ($1, 'Design new homepage', 'Create wireframes and mockups for homepage redesign', 'pending', 'high', '2024-02-15'),
      ($1, 'Implement user authentication', 'Add login/logout functionality with JWT', 'in_progress', 'high', '2024-02-10'),
      ($2, 'Setup CI/CD pipeline', 'Configure automated testing and deployment', 'completed', 'medium', '2024-01-30'),
      ($3, 'Database schema design', 'Design new PostgreSQL schema', 'pending', 'high', '2024-02-20'),
      ($1, 'Write API documentation', 'Document all REST API endpoints', 'pending', 'low', '2024-02-25'),
      ($4, 'Create marketing materials', 'Design brochures and social media content', 'in_progress', 'medium', '2024-02-12'),
      ($2, 'Security vulnerability scan', 'Run automated security tests', 'pending', 'high', '2024-02-08'),
      ($1, 'Performance optimization', 'Optimize database queries and caching', 'pending', 'medium', '2024-02-18'),
      ($3, 'User acceptance testing', 'Conduct UAT with stakeholders', 'pending', 'high', '2024-02-22'),
      ($4, 'Budget planning', 'Create detailed budget for Q2', 'completed', 'low', '2024-01-25')
      RETURNING id
    `, [
      usersById['user@test.com'],
      usersById['admin@test.com'],
      usersById['test@example.com'],
      usersById['john@doe.com']
    ]);

    console.log('Tasks seeded:', tasks.rows.length);

    // Insert comments
    await pool.query(`
      INSERT INTO comments (task_id, user_id, comment_text) VALUES 
      (1, $1, 'Great progress on the wireframes!'),
      (1, $2, 'Consider adding more interactive elements'),
      (2, $1, 'JWT implementation is working well'),
      (2, $3, 'Need to add refresh token functionality'),
      (3, $2, 'CI/CD pipeline is now live and working'),
      (4, $3, 'Schema design is complete, ready for review'),
      (5, $1, 'API documentation is comprehensive'),
      (6, $4, 'Marketing materials look great!'),
      (7, $2, 'Security scan found some issues to address'),
      (8, $1, 'Performance improvements are significant')
    `, [
      usersById['user@test.com'],
      usersById['admin@test.com'],
      usersById['test@example.com'],
      usersById['john@doe.com']
    ]);

    console.log('Comments seeded successfully');

    // Link tasks to projects
    await pool.query(`
      INSERT INTO project_tasks (project_id, task_id) VALUES 
      (1, 1), (1, 2), (1, 5), (1, 8),
      (2, 3), (2, 7),
      (3, 4), (3, 9),
      (4, 7), (4, 8),
      (5, 6), (5, 10)
    `);

    console.log('Project-task relationships created');

    console.log('Database seeded successfully!');
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    await pool.end();
  }
};

seedData();
