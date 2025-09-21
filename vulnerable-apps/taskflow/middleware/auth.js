const jwt = require('jsonwebtoken');
const config = require('../config');
const pool = require('../database/connection');

// Middleware to verify JWT token
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ 
      error: 'Access token required',
      message: 'Please provide a valid authentication token'
    });
  }

  try {
    const decoded = jwt.verify(token, config.jwt.secret);
    
    // Get user from database
    const userResult = await pool.query(
      'SELECT id, email, role FROM users WHERE id = $1',
      [decoded.userId]
    );

    if (userResult.rows.length === 0) {
      return res.status(401).json({ 
        error: 'Invalid token',
        message: 'User not found'
      });
    }

    req.user = userResult.rows[0];
    next();
  } catch (error) {
    return res.status(403).json({ 
      error: 'Invalid token',
      message: 'Token verification failed',
      details: error.message
    });
  }
};

// Middleware to check if user is admin (VULNERABLE: Not properly implemented)
const requireAdmin = (req, res, next) => {
  // VULNERABLE: This middleware exists but is not used in admin routes
  // The admin routes only check if user is authenticated, not if they're admin
  if (!req.user) {
    return res.status(401).json({ 
      error: 'Authentication required',
      message: 'Please log in to access this resource'
    });
  }

  if (req.user.role !== 'admin') {
    return res.status(403).json({ 
      error: 'Admin access required',
      message: 'This resource requires administrator privileges'
    });
  }

  next();
};

module.exports = {
  authenticateToken,
  requireAdmin
};
