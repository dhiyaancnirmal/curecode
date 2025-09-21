<?php
// Database configuration
$host = 'localhost';
$username = 'root';
$password = '';
$database = 'bloggit';

// Create connection
$conn = new mysqli($host, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Set charset
$conn->set_charset("utf8");

// Session management
session_start();
?>
