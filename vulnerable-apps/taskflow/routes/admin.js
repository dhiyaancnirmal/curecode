const express = require('express');
const pool = require('../database/connection');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// VULNERABLE: Admin dashboard - only checks authentication, not admin role
router.get('/dashboard', authenticateToken, async (req, res, next) => {
  try {
    // VULNERABLE: No check for admin role - any authenticated user can access
    // The requireAdmin middleware exists but is not used here
    
    // Get all users
    const usersResult = await pool.query(`
      SELECT id, email, role, created_at, 
             (SELECT COUNT(*) FROM tasks WHERE user_id = users.id) as task_count
      FROM users 
      ORDER BY created_at DESC
    `);

    // Get all tasks with user information
    const tasksResult = await pool.query(`
      SELECT t.*, u.email as user_email, u.role as user_role,
             p.name as project_name
      FROM tasks t
      LEFT JOIN users u ON t.user_id = u.id
      LEFT JOIN project_tasks pt ON t.id = pt.task_id
      LEFT JOIN projects p ON pt.project_id = p.id
      ORDER BY t.created_at DESC
    `);

    // Get all projects with user information
    const projectsResult = await pool.query(`
      SELECT p.*, u.email as user_email, u.role as user_role,
             COUNT(pt.task_id) as task_count
      FROM projects p
      LEFT JOIN users u ON p.user_id = u.id
      LEFT JOIN project_tasks pt ON p.id = pt.project_id
      GROUP BY p.id, u.email, u.role
      ORDER BY p.created_at DESC
    `);

    // Get statistics
    const statsResult = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM users) as total_users,
        (SELECT COUNT(*) FROM tasks) as total_tasks,
        (SELECT COUNT(*) FROM projects) as total_projects,
        (SELECT COUNT(*) FROM comments) as total_comments,
        (SELECT COUNT(*) FROM tasks WHERE status = 'completed') as completed_tasks,
        (SELECT COUNT(*) FROM tasks WHERE status = 'in_progress') as in_progress_tasks,
        (SELECT COUNT(*) FROM tasks WHERE status = 'pending') as pending_tasks
    `);

    res.json({
      message: 'Admin dashboard data retrieved successfully',
      current_user: {
        id: req.user.id,
        email: req.user.email,
        role: req.user.role
      },
      statistics: statsResult.rows[0],
      users: usersResult.rows,
      tasks: tasksResult.rows,
      projects: projectsResult.rows
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Get all users - no admin role check
router.get('/users', authenticateToken, async (req, res, next) => {
  try {
    const result = await pool.query(`
      SELECT id, email, role, created_at,
             (SELECT COUNT(*) FROM tasks WHERE user_id = users.id) as task_count,
             (SELECT COUNT(*) FROM projects WHERE user_id = users.id) as project_count
      FROM users 
      ORDER BY created_at DESC
    `);

    res.json({
      users: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Get all tasks - no admin role check
router.get('/tasks', authenticateToken, async (req, res, next) => {
  try {
    const result = await pool.query(`
      SELECT t.*, u.email as user_email, u.role as user_role,
             p.name as project_name,
             (SELECT COUNT(*) FROM comments WHERE task_id = t.id) as comment_count
      FROM tasks t
      LEFT JOIN users u ON t.user_id = u.id
      LEFT JOIN project_tasks pt ON t.id = pt.task_id
      LEFT JOIN projects p ON pt.project_id = p.id
      ORDER BY t.created_at DESC
    `);

    res.json({
      tasks: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Get all projects - no admin role check
router.get('/projects', authenticateToken, async (req, res, next) => {
  try {
    const result = await pool.query(`
      SELECT p.*, u.email as user_email, u.role as user_role,
             COUNT(pt.task_id) as task_count
      FROM projects p
      LEFT JOIN users u ON p.user_id = u.id
      LEFT JOIN project_tasks pt ON p.id = pt.project_id
      GROUP BY p.id, u.email, u.role
      ORDER BY p.created_at DESC
    `);

    res.json({
      projects: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Delete any user - no admin role check
router.delete('/users/:userId', authenticateToken, async (req, res, next) => {
  try {
    const { userId } = req.params;

    // VULNERABLE: Any authenticated user can delete any other user
    const result = await pool.query(
      'DELETE FROM users WHERE id = $1 RETURNING id, email',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'User not found',
        message: 'The specified user does not exist'
      });
    }

    res.json({
      message: 'User deleted successfully',
      deletedUser: result.rows[0]
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Update any user's role - no admin role check
router.put('/users/:userId/role', authenticateToken, async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { role } = req.body;

    if (!['user', 'admin'].includes(role)) {
      return res.status(400).json({
        error: 'Invalid role',
        message: 'Role must be either "user" or "admin"'
      });
    }

    // VULNERABLE: Any authenticated user can change any other user's role
    const result = await pool.query(
      'UPDATE users SET role = $1 WHERE id = $2 RETURNING id, email, role',
      [role, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'User not found',
        message: 'The specified user does not exist'
      });
    }

    res.json({
      message: 'User role updated successfully',
      user: result.rows[0]
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Get system logs - no admin role check
router.get('/logs', authenticateToken, async (req, res, next) => {
  try {
    // VULNERABLE: Exposing sensitive system information
    const systemInfo = {
      node_version: process.version,
      platform: process.platform,
      arch: process.arch,
      uptime: process.uptime(),
      memory_usage: process.memoryUsage(),
      environment: process.env.NODE_ENV,
      database_connections: 'Not implemented - would show active connections',
      recent_errors: 'Not implemented - would show application errors'
    };

    res.json({
      message: 'System logs retrieved successfully',
      system_info: systemInfo,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: Database backup endpoint - no admin role check
router.get('/backup', authenticateToken, async (req, res, next) => {
  try {
    // VULNERABLE: Any authenticated user can trigger database backup
    // In a real application, this would be a dangerous operation
    
    const backupInfo = {
      message: 'Database backup initiated',
      timestamp: new Date().toISOString(),
      backup_id: Math.random().toString(36).substr(2, 9),
      status: 'In progress',
      estimated_completion: new Date(Date.now() + 5 * 60 * 1000).toISOString()
    };

    res.json(backupInfo);
  } catch (error) {
    next(error);
  }
});

module.exports = router;
