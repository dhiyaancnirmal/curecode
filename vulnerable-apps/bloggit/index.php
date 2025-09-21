<?php
require_once 'config.php';

// Handle search functionality (VULNERABLE TO REFLECTED XSS)
$search_query = '';
$posts = array();

if (isset($_GET['search']) && !empty($_GET['search'])) {
    $search_query = $_GET['search'];
    
    // VULNERABLE: Direct string concatenation for SQL injection
    $sql = "SELECT * FROM posts WHERE title LIKE '%" . $search_query . "%' OR content LIKE '%" . $search_query . "%'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $posts[] = $row;
        }
    }
} else {
    // Get all posts
    $sql = "SELECT * FROM posts ORDER BY created_at DESC";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $posts[] = $row;
        }
    }
}

// Handle comment submission (VULNERABLE TO STORED XSS)
if ($_POST && isset($_POST['comment']) && isset($_POST['post_id'])) {
    $comment_text = $_POST['comment'];
    $post_id = $_POST['post_id'];
    $author = isset($_POST['author']) ? $_POST['author'] : 'Anonymous';
    
    // VULNERABLE: Direct string concatenation for SQL injection
    $sql = "INSERT INTO comments (post_id, comment_text, author) VALUES (" . $post_id . ", '" . $comment_text . "', '" . $author . "')";
    $conn->query($sql);
    
    // Redirect to prevent duplicate submissions
    header("Location: " . $_SERVER['PHP_SELF']);
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bloggit - Vulnerable Blog</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .search-form { margin-bottom: 20px; text-align: center; }
        .search-form input { padding: 10px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }
        .search-form button { padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .post { margin-bottom: 30px; padding: 20px; border: 1px solid #eee; border-radius: 4px; }
        .post h2 { color: #333; margin-top: 0; }
        .post-meta { color: #666; font-size: 0.9em; margin-bottom: 15px; }
        .comments { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
        .comment { margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 4px; }
        .comment-form { margin-top: 20px; }
        .comment-form input, .comment-form textarea { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .comment-form button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .login-link { text-align: center; margin-bottom: 20px; }
        .login-link a { color: #007cba; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bloggit</h1>
            <p>A Vulnerable Blog Application for Security Testing</p>
        </div>
        
        <div class="login-link">
            <a href="login.php">Admin Login</a>
        </div>
        
        <div class="search-form">
            <form method="GET">
                <input type="text" name="search" placeholder="Search posts..." value="<?php echo htmlspecialchars($search_query); ?>">
                <button type="submit">Search</button>
            </form>
        </div>
        
        <?php if (!empty($search_query)): ?>
            <!-- VULNERABLE: Reflected XSS - Direct output without sanitization -->
            <h2>Search results for: <?php echo $search_query; ?></h2>
        <?php endif; ?>
        
        <?php if (empty($posts)): ?>
            <p>No posts found.</p>
        <?php else: ?>
            <?php foreach ($posts as $post): ?>
                <div class="post">
                    <h2><?php echo htmlspecialchars($post['title']); ?></h2>
                    <div class="post-meta">
                        Posted on <?php echo $post['created_at']; ?>
                    </div>
                    <div class="post-content">
                        <?php echo nl2br(htmlspecialchars($post['content'])); ?>
                    </div>
                    
                    <div class="comments">
                        <h3>Comments</h3>
                        
                        <?php
                        // Get comments for this post (VULNERABLE TO SQL INJECTION)
                        $comment_sql = "SELECT * FROM comments WHERE post_id = " . $post['id'] . " ORDER BY created_at DESC";
                        $comment_result = $conn->query($comment_sql);
                        
                        if ($comment_result && $comment_result->num_rows > 0):
                        ?>
                            <?php while ($comment = $comment_result->fetch_assoc()): ?>
                                <div class="comment">
                                    <strong><?php echo htmlspecialchars($comment['author']); ?></strong> 
                                    <span style="color: #666; font-size: 0.9em;"><?php echo $comment['created_at']; ?></span>
                                    <!-- VULNERABLE: Stored XSS - Direct output without sanitization -->
                                    <div><?php echo $comment['comment_text']; ?></div>
                                </div>
                            <?php endwhile; ?>
                        <?php else: ?>
                            <p>No comments yet.</p>
                        <?php endif; ?>
                        
                        <div class="comment-form">
                            <h4>Add a Comment</h4>
                            <form method="POST">
                                <input type="hidden" name="post_id" value="<?php echo $post['id']; ?>">
                                <input type="text" name="author" placeholder="Your name (optional)" maxlength="100">
                                <textarea name="comment" placeholder="Your comment..." rows="3" required></textarea>
                                <button type="submit">Post Comment</button>
                            </form>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</body>
</html>
