// VULNERABLE: Error handler that leaks stack traces
const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // VULNERABLE: Always return full error details including stack trace
  const errorResponse = {
    error: true,
    message: err.message || 'Internal Server Error',
    stack: err.stack, // VULNERABLE: Exposing stack trace
    timestamp: new Date().toISOString(),
    path: req.path,
    method: req.method,
    body: req.body, // VULNERABLE: Exposing request body
    query: req.query, // VULNERABLE: Exposing query parameters
    headers: req.headers, // VULNERABLE: Exposing headers
    user: req.user || null, // VULNERABLE: Exposing user info
    statusCode: err.statusCode || 500
  };

  // Add additional error details
  if (err.code) errorResponse.code = err.code;
  if (err.details) errorResponse.details = err.details;
  if (err.validation) errorResponse.validation = err.validation;

  res.status(err.statusCode || 500).json(errorResponse);
};

module.exports = { errorHandler };
