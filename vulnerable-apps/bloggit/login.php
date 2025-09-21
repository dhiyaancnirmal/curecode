<?php
require_once 'config.php';

$error_message = '';
$success_message = '';

// Handle login form submission
if ($_POST && isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // VULNERABLE: SQL Injection - Direct string concatenation
    $sql = "SELECT * FROM users WHERE username = '" . $username . "' AND password = '" . $password . "'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        $user = $result->fetch_assoc();
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['logged_in'] = true;
        
        $success_message = "Login successful! Welcome, " . $user['username'];
    } else {
        $error_message = "Invalid username or password.";
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: login.php");
    exit();
}

// Check if user is already logged in
if (isset($_SESSION['logged_in']) && $_SESSION['logged_in']) {
    $logged_in = true;
} else {
    $logged_in = false;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Bloggit</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #005a87; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        .success { color: #155724; background: #d4edda; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        .info { color: #0c5460; background: #d1ecf1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #007cba; text-decoration: none; }
        .user-info { background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bloggit Login</h1>
            <p>Admin Panel Access</p>
        </div>
        
        <?php if ($logged_in): ?>
            <div class="user-info">
                <h3>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h3>
                <p>You are successfully logged in.</p>
            </div>
            
            <div class="info">
                <h4>Available Actions:</h4>
                <ul>
                    <li>View all posts and comments</li>
                    <li>Access admin functionality</li>
                    <li>Test security vulnerabilities</li>
                </ul>
            </div>
            
            <a href="index.php" class="btn" style="text-decoration: none; display: block; text-align: center; margin-bottom: 10px;">Go to Blog</a>
            <a href="?logout=1" class="btn" style="text-decoration: none; display: block; text-align: center; background: #dc3545;">Logout</a>
            
        <?php else: ?>
            <?php if ($error_message): ?>
                <div class="error"><?php echo $error_message; ?></div>
            <?php endif; ?>
            
            <?php if ($success_message): ?>
                <div class="success"><?php echo $success_message; ?></div>
            <?php endif; ?>
            
            <div class="info">
                <h4>Test Credentials:</h4>
                <p><strong>Username:</strong> admin<br>
                <strong>Password:</strong> password123</p>
                <p><em>Or try SQL injection: <code>' OR '1'='1</code></em></p>
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn">Login</button>
            </form>
        <?php endif; ?>
        
        <div class="back-link">
            <a href="index.php">← Back to Blog</a>
        </div>
    </div>
</body>
</html>
