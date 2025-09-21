const express = require('express');
const { body, validationResult } = require('express-validator');
const pool = require('../database/connection');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all tasks for the authenticated user
router.get('/', authenticateToken, async (req, res, next) => {
  try {
    const result = await pool.query(`
      SELECT t.*, p.name as project_name, p.id as project_id
      FROM tasks t
      LEFT JOIN project_tasks pt ON t.id = pt.task_id
      LEFT JOIN projects p ON pt.project_id = p.id
      WHERE t.user_id = $1
      ORDER BY t.created_at DESC
    `, [req.user.id]);

    res.json({
      tasks: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    next(error);
  }
});

// VULNERABLE: IDOR - Get specific task by ID without checking ownership
router.get('/:taskId', authenticateToken, async (req, res, next) => {
  try {
    const { taskId } = req.params;

    // VULNERABLE: No check if the task belongs to the authenticated user
    // Any authenticated user can access any task by ID
    const result = await pool.query(`
      SELECT t.*, u.email as owner_email, p.name as project_name
      FROM tasks t
      LEFT JOIN users u ON t.user_id = u.id
      LEFT JOIN project_tasks pt ON t.id = pt.task_id
      LEFT JOIN projects p ON pt.project_id = p.id
      WHERE t.id = $1
    `, [taskId]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Task not found',
        message: 'The requested task does not exist'
      });
    }

    const task = result.rows[0];

    // Get comments for this task
    const commentsResult = await pool.query(`
      SELECT c.*, u.email as author_email
      FROM comments c
      LEFT JOIN users u ON c.user_id = u.id
      WHERE c.task_id = $1
      ORDER BY c.created_at ASC
    `, [taskId]);

    res.json({
      task: {
        ...task,
        comments: commentsResult.rows
      }
    });
  } catch (error) {
    next(error);
  }
});

// Create new task
router.post('/', authenticateToken, [
  body('title').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('priority').optional().isIn(['low', 'medium', 'high']),
  body('due_date').optional().isISO8601(),
  body('project_id').optional().isInt()
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { title, description, priority = 'medium', due_date, project_id } = req.body;

    const result = await pool.query(`
      INSERT INTO tasks (user_id, title, description, priority, due_date)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `, [req.user.id, title, description, priority, due_date]);

    const task = result.rows[0];

    // Link to project if project_id provided
    if (project_id) {
      await pool.query(`
        INSERT INTO project_tasks (project_id, task_id)
        VALUES ($1, $2)
      `, [project_id, task.id]);
    }

    res.status(201).json({
      message: 'Task created successfully',
      task
    });
  } catch (error) {
    next(error);
  }
});

// Update task
router.put('/:taskId', authenticateToken, [
  body('title').optional().trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('status').optional().isIn(['pending', 'in_progress', 'completed', 'cancelled']),
  body('priority').optional().isIn(['low', 'medium', 'high']),
  body('due_date').optional().isISO8601()
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { taskId } = req.params;
    const updates = req.body;

    // Check if task exists and belongs to user
    const existingTask = await pool.query(
      'SELECT id FROM tasks WHERE id = $1 AND user_id = $2',
      [taskId, req.user.id]
    );

    if (existingTask.rows.length === 0) {
      return res.status(404).json({
        error: 'Task not found',
        message: 'Task not found or you do not have permission to update it'
      });
    }

    // Build dynamic update query
    const updateFields = [];
    const values = [];
    let paramCount = 1;

    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        updateFields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (updateFields.length === 0) {
      return res.status(400).json({
        error: 'No valid fields to update',
        message: 'Please provide at least one field to update'
      });
    }

    updateFields.push(`updated_at = CURRENT_TIMESTAMP`);
    values.push(taskId);

    const result = await pool.query(`
      UPDATE tasks 
      SET ${updateFields.join(', ')}
      WHERE id = $${paramCount}
      RETURNING *
    `, values);

    res.json({
      message: 'Task updated successfully',
      task: result.rows[0]
    });
  } catch (error) {
    next(error);
  }
});

// Delete task
router.delete('/:taskId', authenticateToken, async (req, res, next) => {
  try {
    const { taskId } = req.params;

    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id',
      [taskId, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Task not found',
        message: 'Task not found or you do not have permission to delete it'
      });
    }

    res.json({
      message: 'Task deleted successfully',
      taskId: result.rows[0].id
    });
  } catch (error) {
    next(error);
  }
});

// Add comment to task
router.post('/:taskId/comments', authenticateToken, [
  body('comment_text').trim().isLength({ min: 1 })
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { taskId } = req.params;
    const { comment_text } = req.body;

    // VULNERABLE: No check if task exists or if user has access to it
    const result = await pool.query(`
      INSERT INTO comments (task_id, user_id, comment_text)
      VALUES ($1, $2, $3)
      RETURNING *
    `, [taskId, req.user.id, comment_text]);

    res.status(201).json({
      message: 'Comment added successfully',
      comment: result.rows[0]
    });
  } catch (error) {
    next(error);
  }
});

// Get user's projects
router.get('/projects/list', authenticateToken, async (req, res, next) => {
  try {
    const result = await pool.query(`
      SELECT p.*, COUNT(pt.task_id) as task_count
      FROM projects p
      LEFT JOIN project_tasks pt ON p.id = pt.project_id
      WHERE p.user_id = $1
      GROUP BY p.id
      ORDER BY p.created_at DESC
    `, [req.user.id]);

    res.json({
      projects: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    next(error);
  }
});

// Create new project
router.post('/projects', authenticateToken, [
  body('name').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim()
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { name, description } = req.body;

    const result = await pool.query(`
      INSERT INTO projects (user_id, name, description)
      VALUES ($1, $2, $3)
      RETURNING *
    `, [req.user.id, name, description]);

    res.status(201).json({
      message: 'Project created successfully',
      project: result.rows[0]
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
